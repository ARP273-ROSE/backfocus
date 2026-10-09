"""Garde-fou : le dépôt est public — aucune donnée personnelle dans ses fichiers.

Parcourt TOUS les fichiers suivis par git (à défaut, toute l'arborescence hors build/dist) : fichiers texte, texte
extrait des PDF (pdftotext + métadonnées pdfinfo), contenu décompressé des .gz, blocs texte des PNG, chaînes des
autres fichiers binaires. Les motifs couvrent prénoms, identifiants, machines, chemins d'infrastructure et lieu
privés ; la liste blanche (`PERMIS`, `HOME_GENERIQUES`) est explicite.
"""
import gzip
import os
import re
import shutil
import subprocess
import zlib
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
CE_FICHIER = Path(__file__).resolve()

# dossiers personnels génériques admis (exemples de documentation, conteneurs publics, CI)
HOME_GENERIQUES = r'x|user|username|utilisateur|runner|astro|sage|jovyan|linuxbrew'
MOTIFS = [
    r'(?i)kevin', r'\b[Ss]ophie\b', r'(?i)cyrille', r'(?i)kguion', r'(?i)altesch', r'(?i)@gmail\.com',
    r'(?i)orly\.tour', r'(?i)gypaete', r'(?i)alert[-_ ]?bay', r'(?i)fakarava', r'(?i)mauna ?kea',
    r'/mnt/nas\b', r'/mnt/zpool2', r'/mnt/apps_pool', r'/workspace\b', r'(?<![\w.~])/root/',
    r'/home/(?!(?:%s)\b)[A-Za-z0-9_.-]+' % HOME_GENERIQUES,
    r'(?i)C:\\{1,2}Users\\{1,2}(?!(?:x|Public|runneradmin|username|utilisateur|nom|name)\b)\w+',
    r'(?i)compi[eè]gne', r'(?i)air ?france', r'\bPNT\b', r'(?i)patagonie', r'(?i)truenas',
]
MOTIFS_DEPOT = []  # motifs propres à ce dépôt
# liste blanche explicite : textes exacts admis. « SOPHIE » en capitales (spectrographe de l'OHP) n'est pas pris
# par le motif sensible à la casse ; le collecteur de rapports et le compte GitHub sont publics.
PERMIS = {'fenice.giff.re', 'ARP273-ROSE'}
EXCLUS = {'build', 'dist', '.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
RE = [re.compile(m) for m in MOTIFS + MOTIFS_DEPOT]
MIN_FICHIERS = 15


def fichiers_du_depot():
    try:
        r = subprocess.run(['git', 'ls-files', '-z'], cwd=RACINE, capture_output=True, timeout=30)
        if r.returncode == 0 and r.stdout:
            return [RACINE / f for f in r.stdout.decode('utf-8').split('\0') if f]
    except (OSError, subprocess.SubprocessError):
        pass
    out = []
    for d, sous, noms in os.walk(RACINE):
        sous[:] = [s for s in sous if s not in EXCLUS and not s.endswith('.egg-info')]
        out += [Path(d) / n for n in noms if not n.endswith(('.tar.gz', '.deb', '.zip', '.pyc'))]
    return out


def chercher(texte: str):
    return [m.group(0) for r in RE for m in r.finditer(texte) if m.group(0) not in PERMIS]


def textes_png(donnees: bytes) -> str:
    """Blocs tEXt / zTXt / iTXt d'un PNG (logiciel, commentaire, chemin…)."""
    out, i = [], 8
    while i + 8 <= len(donnees):
        n = int.from_bytes(donnees[i:i + 4], 'big')
        genre = donnees[i + 4:i + 8]
        corps = donnees[i + 8:i + 8 + n]
        try:
            if genre == b'tEXt':
                out.append(corps.decode('latin-1'))
            elif genre == b'zTXt':
                k = corps.find(b'\0')
                out.append(corps[:k].decode('latin-1') + ' '
                           + zlib.decompress(corps[k + 2:]).decode('latin-1', 'replace'))
            elif genre == b'iTXt':
                out.append(corps.decode('utf-8', 'replace'))
        except zlib.error:
            pass
        i += 12 + n
    return '\n'.join(out)


def contenu(p: Path) -> str:
    donnees = p.read_bytes()
    nom = p.name.lower()
    if nom.endswith('.pdf'):
        if not shutil.which('pdftotext'):
            pytest.skip('pdftotext absent (poppler-utils) : PDF non vérifiables ici')
        r = subprocess.run(['pdftotext', '-q', str(p), '-'], capture_output=True, timeout=120)
        texte = r.stdout.decode('utf-8', 'replace')
        if shutil.which('pdfinfo'):                                   # métadonnées (auteur, créateur, titre…)
            texte += subprocess.run(['pdfinfo', str(p)], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        return texte
    if nom.endswith('.gz'):
        return gzip.decompress(donnees).decode('utf-8', 'replace')
    if nom.endswith('.png'):
        return textes_png(donnees)
    if b'\0' not in donnees[:8192]:
        try:
            return donnees.decode('utf-8')
        except UnicodeDecodeError:
            pass
    # binaire : chaînes intégrées (suites d'au moins 6 caractères imprimables, comme `strings`)
    return '\n'.join(m.decode('ascii') for m in re.findall(rb'[\x20-\x7e]{6,}', donnees))


def test_motifs_detectes():
    """Le garde-fou sait reconnaître ce qu'il cherche (et laisse passer la liste blanche)."""
    for x in ('Retour de Kevin', '/mnt/nas/X', '/home/jdupont/a', 'C:\\Users\\jdupont\\a', '/workspace/GitHub',
              '/root/bin', 'Sophie', 'NAS gypaete', 'site de Compiègne'):
        assert chercher(x), x
    for x in ('T193 SOPHIE', '/home/x/donnees', '/home/sage/carnet', 'C:\\Users\\Public', '/mnt/partage/donnees',
              'https://fenice.giff.re/rapports/collecte.php', 'ARP273-ROSE', '~/root/'):
        assert not chercher(x), x


def test_aucune_donnee_personnelle_dans_le_depot():
    fautes = []
    vus = 0
    for p in fichiers_du_depot():
        if p.resolve() == CE_FICHIER or not p.is_file():
            continue
        vus += 1
        for t in sorted(set(chercher(contenu(p)))):
            fautes.append('%s : %r' % (p.relative_to(RACINE), t))
    assert vus >= MIN_FICHIERS
    assert not fautes, 'données personnelles :\n' + '\n'.join(fautes[:80])
