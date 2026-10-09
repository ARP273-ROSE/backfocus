"""Garde-fou : le dépôt est public — aucune donnée personnelle dans ses fichiers.

Ce fichier ne contient AUCUN mot interdit en clair : seulement des empreintes salées (SHA-256 tronqué)
des jetons interdits. Chaque fichier suivi par git est découpé en jetons (minuscules, sans accents) ;
l'empreinte de chaque jeton, de chaque suite de 2 ou 3 jetons concaténés, des débuts de chemins absolus
et des coordonnées normalisées est comparée aux listes ci-dessous. Formats lus : texte, texte des PDF
(pdftotext + pdfinfo), .gz décompressés, blocs texte des PNG, chaînes des autres binaires ; plus les
messages de commit disponibles dans le clone.

Réglages propres au dépôt (facultatifs) : clé « confidentialite » de kit.json, ou tests/confidentialite.json :
    {"min_fichiers": 50, "jetons_applications": true, "empreintes_depot": ["…"], "exclus": ["chemin/relatif"]}

Gabarit commun (_kit_windows) : ne pas modifier ici, le reposer avec poser_le_kit.py.
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import unicodedata
import zlib
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
CE_FICHIER = Path(__file__).resolve()

# --- empreintes (générées par le gabarit commun, jamais écrites à la main) -----------------------
# @EMPREINTES@
SEL = 'kit-confidentialite-2026-10-14'
EMPREINTES = {
    'mots': {'17a67afa41e78504', '2188de283f47bc5c', '43c96feee6197949', '585d958c0950152b', '6eaebc7001fdf0bb',
             '715b4cbbd154f618', '7d72de838d7f261f', '81a531c977e1f969', '84fe165a28b00b54', '917de1bba66df855',
             'a5c3e9116412d538', 'b5c789d4b0f652a4', 'bc232ae7c7778059', 'd03c205fdec0a7a0', 'd5bd0cbfd6a75e70',
             'eb3dbd309149adaf', 'f206d8c35cbf3aa7', 'f417a9f5398f691f', 'f6e73769e3e0f957'},
    'sauf_capitales': {'e71fe5f22a76278f'},
    'capitales': {'f51c5dd0b2bf054f'},
    'chemins': {'4e32eda40ac0fd1a', 'bbeb50778be85e6e'},
    'dossiers': {'135c6b80e87cfd49'},
    'nombres': {'270f230bef385e43', '2a9f0643640b0c01', 'd1eb3355ccab540b'},
    'nombres_lies': {'67a92d5ca1cb1ef1', '8518d8f5b8fe6070', '86b3c77658dd7b59'},
    'sexa': {'89d5ef045dbbd8d1', '8a64471bf682fe4c'},
    'sous_chaines': {5: {'84fe165a28b00b54'}, 6: {'6eaebc7001fdf0bb', '7d72de838d7f261f', '81a531c977e1f969'}, 7: {'2188de283f47bc5c', '585d958c0950152b', '715b4cbbd154f618', 'b5c789d4b0f652a4', 'f417a9f5398f691f'}, 8: {'17a67afa41e78504', 'bc232ae7c7778059', 'eb3dbd309149adaf'}, 9: {'917de1bba66df855', 'a5c3e9116412d538', 'd5bd0cbfd6a75e70'}},
}
EMPREINTES_APPLICATIONS = {
    'mots': {'138ed58e6e3adbdd', '4139707c847612a1', '53d29494a5bf47ee', '72281055df367d60', '83a4a77337776098',
             '8beff5a029b422e2', '8d48a97e4be0f8c1', '94a33cd738268da2', 'cfa1155487cd1f60', 'e299fd67cd0b6722',
             'febff4bf483d4638'},
    'sous_chaines': {7: {'4139707c847612a1', '72281055df367d60', 'cfa1155487cd1f60'}, 9: {'febff4bf483d4638'}, 10: {'83a4a77337776098'}, 11: {'e299fd67cd0b6722'}},
}
# @FIN-EMPREINTES@

# dossiers personnels génériques admis (exemples de documentation, conteneurs publics, CI)
HOME_GENERIQUES = r'x|user|username|utilisateur|runner|runneradmin|astro|sage|jovyan|linuxbrew'
USERS_GENERIQUES = r'x|Public|runneradmin|username|utilisateur|nom|name|Musicien|Musician|Default|All Users'
STRUCTURELS = [
    re.compile(r'/home/(?!(?:%s)\b)[A-Za-z0-9_.-]+' % HOME_GENERIQUES),
    re.compile(r'(?i)C:\\{1,2}Users\\{1,2}(?!(?:%s)\b)\w+' % USERS_GENERIQUES),
]
# témoins fictifs des chemins structurels, admis
PERMIS = {'/home/jdupont', 'C:\\Users\\jdupont', 'C:\\\\Users\\\\jdupont'}
EXCLUS = {'build', 'dist', '.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}


def _reglages() -> dict:
    for p, cle in ((RACINE / 'kit.json', 'confidentialite'), (RACINE / 'tests' / 'confidentialite.json', None)):
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        d = d.get(cle) if cle else d
        if isinstance(d, dict):
            return d
    return {}


REGLAGES = _reglages()
MIN_FICHIERS = int(REGLAGES.get('min_fichiers', 1))
AVEC_APPLICATIONS = bool(REGLAGES.get('jetons_applications', True))


def empreinte(jeton: str) -> str:
    return hashlib.sha256((SEL + '\0' + jeton).encode('utf-8')).hexdigest()[:16]


def normaliser(mot: str) -> str:
    mot = unicodedata.normalize('NFKD', mot)
    return ''.join(c for c in mot if not unicodedata.combining(c)).lower()


def _ensembles():
    mots = set(EMPREINTES['mots']) | set(REGLAGES.get('empreintes_depot', ()))
    sous = {int(k): set(v) for k, v in EMPREINTES['sous_chaines'].items()}
    if AVEC_APPLICATIONS:
        mots |= set(EMPREINTES_APPLICATIONS['mots'])
        for k, v in EMPREINTES_APPLICATIONS['sous_chaines'].items():
            sous.setdefault(int(k), set()).update(v)
    return mots, sous


MOTS, SOUS_CHAINES = _ensembles()
RE_JETON = re.compile(r'[^\W_]+')
RE_CHEMIN = re.compile(r'(?<![\w.~/\\-])((?:/[A-Za-z0-9_.-]+){1,2})')
RE_NOMBRE = re.compile(r'(?<![\d.])(\d{1,3})[.,](\d{3,})')
RE_SEXA = re.compile(r'(?<!\d)(\d{1,3}) ?([*°:]) ?(\d{2})(?: ?[:\'′] ?(\d{2}))?(?!\d)')
_cache = {}
# rapport en clair seulement sur demande, en local (le journal de la CI est public)
EN_CLAIR = os.environ.get('CONFIDENTIALITE_EN_CLAIR') == '1'


def _jeton_interdit(n: str) -> bool:
    r = _cache.get(n)
    if r is None:
        r = empreinte(n) in MOTS or any(
            empreinte(n[i:i + lg]) in ens
            for lg, ens in SOUS_CHAINES.items() if lg < len(n) for i in range(len(n) - lg + 1))
        _cache[n] = r
    return r


def chercher(texte: str, binaire: bool = False):
    """Fautes trouvées dans `texte`. Le jeton fautif n'est rendu que par sa position et une forme
    masquée : le rapport de la CI (public) ne doit pas recopier ce qu'il protège. `binaire` : texte tiré
    des chaînes d'un fichier binaire, où un jeton de moins de 5 caractères naît du hasard (son, police)."""
    fautes = []
    court = 5 if binaire else 0

    def faute(debut, brut):
        fautes.append('car. %d : %s' % (debut, brut if EN_CLAIR else brut[:1] + '•' * max(0, len(brut) - 2) + brut[-1:]))

    jetons = [(m.start(), m.group(0), normaliser(m.group(0))) for m in RE_JETON.finditer(texte)]
    for i, (debut, brut, n) in enumerate(jetons):
        if len(n) < court:
            continue
        h = empreinte(n)
        if _jeton_interdit(n):
            faute(debut, brut)
        elif h in EMPREINTES['sauf_capitales'] and not brut.isupper():
            faute(debut, brut)
        elif h in EMPREINTES['capitales'] and brut.isupper():
            faute(debut, brut)
        for k in (2, 3):
            if i + k <= len(jetons):
                bloc = jetons[i:i + k]
                if any(b[0] - (a[0] + len(a[1])) > 3 for a, b in zip(bloc, bloc[1:])):   # séparés par plus que « - », « . », «  »
                    continue
                if empreinte(''.join(x[2] for x in bloc)) in MOTS:
                    faute(debut, ''.join(x[1] for x in bloc))
    for m in RE_CHEMIN.finditer(texte):
        segs = m.group(1).split('/')[1:]
        suite = texte[m.end():m.end() + 1] == '/'                    # le chemin continue après
        for k in (1, 2):
            if len(segs) >= k:
                h = empreinte('/' + '/'.join(normaliser(s) for s in segs[:k]))
                if h in EMPREINTES['chemins'] or (h in EMPREINTES['dossiers'] and (len(segs) > k or suite)):
                    faute(m.start(), m.group(1))
    lies = []
    for m in RE_NOMBRE.finditer(texte):
        h = empreinte('%d.%s' % (int(m.group(1)), m.group(2)[:3]))
        if h in EMPREINTES['nombres']:
            faute(m.start(), m.group(0))
        elif h in EMPREINTES['nombres_lies']:
            lies.append(m)
    if lies and any(empreinte('%d.%s' % (int(m.group(1)), m.group(2)[:3])) in EMPREINTES['nombres']
                    for m in RE_NOMBRE.finditer(texte)):
        for m in lies:
            faute(m.start(), m.group(0))
    for m in RE_SEXA.finditer(texte):
        if m.group(2) in '*°' or m.group(4):
            if empreinte('%d:%s' % (int(m.group(1)), m.group(3))) in EMPREINTES['sexa']:
                faute(m.start(), m.group(0))
    for r in STRUCTURELS:
        for m in r.finditer(texte):
            if m.group(0) not in PERMIS:
                faute(m.start(), m.group(0))
    return fautes


def fichiers_du_depot():
    exclus = {(RACINE / e).resolve() for e in REGLAGES.get('exclus', ())}
    try:
        r = subprocess.run(['git', 'ls-files', '-z'], cwd=RACINE, capture_output=True, timeout=30)
        if r.returncode == 0 and r.stdout:
            out = [RACINE / f for f in r.stdout.decode('utf-8').split('\0')
                   if f and '__pycache__' not in f and not f.endswith('.pyc')]
            return [p for p in out if p.resolve() not in exclus]
    except (OSError, subprocess.SubprocessError):
        pass
    out = []
    for d, sous, noms in os.walk(RACINE):
        sous[:] = [s for s in sous if s not in EXCLUS and not s.endswith('.egg-info')]
        out += [Path(d) / n for n in noms if not n.endswith(('.tar.gz', '.deb', '.zip', '.pyc'))]
    return [p for p in out if p.resolve() not in exclus]


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
    return lire(p)[0]


def lire(p: Path):
    """(texte, binaire) : le texte examiné d'un fichier, et s'il vient des chaînes d'un binaire."""
    donnees = p.read_bytes()
    nom = p.name.lower()
    if nom.endswith('.pdf'):
        if not shutil.which('pdftotext'):
            pytest.skip('pdftotext absent (poppler-utils) : PDF non vérifiables ici')
        r = subprocess.run(['pdftotext', '-q', str(p), '-'], capture_output=True, timeout=120)
        texte = r.stdout.decode('utf-8', 'replace')
        if shutil.which('pdfinfo'):                                   # métadonnées (auteur, créateur, titre…)
            texte += subprocess.run(['pdfinfo', str(p)], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        return texte, False
    if nom.endswith('.gz'):
        try:
            return gzip.decompress(donnees).decode('utf-8', 'replace'), False
        except (OSError, EOFError, zlib.error):
            pass
    if nom.endswith('.png'):
        return textes_png(donnees), False
    if b'\0' not in donnees[:8192]:
        try:
            return donnees.decode('utf-8'), False
        except UnicodeDecodeError:
            pass
    # binaire : chaînes intégrées (suites d'au moins 6 caractères imprimables, comme `strings`)
    return '\n'.join(m.decode('ascii') for m in re.findall(rb'[\x20-\x7e]{6,}', donnees)), True


def test_garde_fou_arme():
    """Le garde-fou a ses listes, et ses motifs structurels marchent (témoins fictifs)."""
    assert len(EMPREINTES['mots']) >= 10 and EMPREINTES['chemins'] and EMPREINTES['nombres']
    assert all(len(h) == 16 for h in EMPREINTES['mots'])
    assert chercher('/home/' + 'jmartin' + '/a') and chercher('C:\\Users\\' + 'jmartin' + '\\a')
    for x in ('/home/x/donnees', '/home/sage/carnet', 'C:\\Users\\Public', '/mnt/partage/donnees',
              'https://fenice.giff.re/rapports/collecte.php', 'ARP273-ROSE', '~/root/',
              'Observatoire de Haute-Provence 43.9317 5.7122', 'durée 02:45', 'ARP273-ROSE/Tutti'):
        assert not chercher(x), x


def test_aucune_donnee_personnelle_dans_le_depot():
    fautes = []
    vus = 0
    for p in fichiers_du_depot():
        if p.resolve() == CE_FICHIER or not p.is_file():
            continue
        vus += 1
        texte, binaire = lire(p)
        for t in sorted(set(chercher(p.name) + chercher(texte, binaire))):
            fautes.append('%s : %s' % (p.relative_to(RACINE), t))
    assert vus >= MIN_FICHIERS
    assert not fautes, 'données personnelles :\n' + '\n'.join(fautes[:80])


def test_messages_de_commit():
    """Messages de commit présents dans le clone (toute l'histoire en local, le dernier en CI)."""
    try:
        r = subprocess.run(['git', 'log', '--format=%H%n%an %ae%n%B%x00', '-n', '5000'], cwd=RACINE,
                           capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        pytest.skip('git absent')
    if r.returncode != 0:
        pytest.skip('pas de dépôt git')
    fautes = []
    for bloc in r.stdout.decode('utf-8', 'replace').split('\0'):
        sha, _, texte = bloc.strip().partition('\n')
        fautes += ['%s : %s' % (sha[:10], t) for t in chercher(texte)]
    assert not fautes, 'messages de commit :\n' + '\n'.join(fautes[:40])
