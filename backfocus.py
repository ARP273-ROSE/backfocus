#!/usr/bin/env python3
"""
Backfocus Calculator v2.0.0 – Bilingual (EN/FR) cross-platform application.
Dark space/cosmos theme · 12 000+ reference DB · Galaxy cursor.
Light convention: Telescope (left) → Camera (right).
PyQt6 GUI.
"""

# Windows: set AppUserModelID before any GUI import so taskbar uses our icon
import sys
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ARP273.BackfocusCalculator.2")
    except (AttributeError, OSError):
        pass

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QTreeWidget, QTreeWidgetItem,
    QMenuBar, QMenu, QSplitter, QFrame, QGroupBox, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout, QTextBrowser,
    QMessageBox, QFileDialog, QProgressBar, QSizePolicy,
    QHeaderView, QAbstractItemView, QListWidget, QListWidgetItem,
    QSpacerItem, QToolBar)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QMimeData, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPixmap, QIcon, QImage,
    QPainterPath, QAction, QCursor, QDrag, QPalette, QFontMetrics)

import json, os, copy, itertools, math, random, bisect, threading, queue

VERSION = "2.0.1"

# ═══════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════
TR = {
    "app_title":         {"en": "Backfocus Calculator", "fr": "Calculateur de Backfocus"},
    "file":              {"en": "File", "fr": "Fichier"},
    "language":          {"en": "Language", "fr": "Langue"},
    "view":              {"en": "View", "fr": "Affichage"},
    "settings":          {"en": "Settings", "fr": "Paramètres"},
    "help_menu":         {"en": "Help", "fr": "Aide"},
    "export_config":     {"en": "Export Configuration…", "fr": "Exporter la configuration…"},
    "import_config":     {"en": "Import Configuration…", "fr": "Importer la configuration…"},
    "export_all":        {"en": "Export All Data…", "fr": "Exporter toutes les données…"},
    "import_all":        {"en": "Import All Data…", "fr": "Importer toutes les données…"},
    "save_all":          {"en": "Save All", "fr": "Tout enregistrer"},
    "quit":              {"en": "Quit", "fr": "Quitter"},
    "confirm_import_all":{"en": "This will replace ALL your current data (parts, configurations, settings).\nAre you sure?",
                          "fr": "Ceci remplacera TOUTES vos données actuelles (pièces, configurations, réglages).\nÊtes-vous sûr?"},
    "import_all_ok":     {"en": "All data imported successfully.", "fr": "Toutes les données importées avec succès."},
    "export_all_ok":     {"en": "All data exported successfully.", "fr": "Toutes les données exportées avec succès."},
    "save_all_ok":       {"en": "All data saved.", "fr": "Toutes les données enregistrées."},
    "confirm_quit":      {"en": "All data has been saved. Quit?", "fr": "Toutes les données ont été enregistrées. Quitter?"},
    "open_catalog":      {"en": "Parts Catalog", "fr": "Catalogue de pièces"},
    "new_part":          {"en": "New Part", "fr": "Nouvelle pièce"},
    "user_guide":        {"en": "User Guide", "fr": "Guide d'utilisation"},
    "about":             {"en": "About", "fr": "À propos"},
    "report_bug":        {"en": "Report Bug…", "fr": "Signaler un bug…"},
    "units":             {"en": "Measurement Units", "fr": "Unités de mesure"},
    "length_mm":         {"en": "Lengths in mm", "fr": "Longueurs en mm"},
    "length_in":         {"en": "Lengths in inches", "fr": "Longueurs en pouces"},
    "mass_g":            {"en": "Mass in grams", "fr": "Masse en grammes"},
    "mass_oz":           {"en": "Mass in ounces", "fr": "Masse en onces"},
    "part_brand":        {"en": "Brand", "fr": "Marque"},
    "part_name":         {"en": "Name", "fr": "Nom"},
    "part_type":         {"en": "Type", "fr": "Type"},
    "optical_length":    {"en": "Optical Length", "fr": "Longueur optique"},
    "mass_label":        {"en": "Mass", "fr": "Masse"},
    "reversible":        {"en": "Reversible", "fr": "Réversible"},
    "bf_role":           {"en": "Backfocus role", "fr": "Rôle backfocus"},
    "bf_start":          {"en": "BF starts here", "fr": "BF commence ici"},
    "bf_end":            {"en": "BF ends here", "fr": "BF finit ici"},
    "bf_none":           {"en": "None", "fr": "Aucun"},
    "qty":               {"en": "Qty", "fr": "Qté"},
    "part_notes":        {"en": "Notes", "fr": "Notes"},
    "tside":             {"en": "Telescope side", "fr": "Côté télescope"},
    "cside":             {"en": "Camera side", "fr": "Côté caméra"},
    "thread":            {"en": "Thread", "fr": "Filetage"},
    "gender":            {"en": "Gender", "fr": "Genre"},
    "gender_male":       {"en": "Male", "fr": "Mâle"},
    "gender_female":     {"en": "Female", "fr": "Femelle"},
    "gender_all":        {"en": "All", "fr": "Tous"},
    "type_telescope":    {"en": "Telescope", "fr": "Télescope"},
    "type_refractor":    {"en": "Refractor", "fr": "Lunette"},
    "type_camera_lens":  {"en": "Camera Lens", "fr": "Objectif photo"},
    "type_camera":       {"en": "Astro Camera", "fr": "Caméra astro"},
    "type_dslr":         {"en": "DSLR / Mirrorless", "fr": "Reflex / Hybride"},
    "type_eyepiece":     {"en": "Eyepiece", "fr": "Oculaire"},
    "type_barlow":       {"en": "Barlow Lens", "fr": "Barlow"},
    "type_reducer":      {"en": "Focal Reducer", "fr": "Réducteur"},
    "type_flattener":    {"en": "Field Flattener", "fr": "Aplanisseur"},
    "type_extender":     {"en": "Focal Extender", "fr": "Extendeur"},
    "type_corrector":    {"en": "Coma Corrector", "fr": "Correcteur de coma"},
    "type_filter_wheel": {"en": "Filter Wheel", "fr": "Roue à filtres"},
    "type_filter_holder":{"en": "Filter Holder", "fr": "Porte-filtre"},
    "type_oag":          {"en": "OAG", "fr": "Diviseur optique"},
    "type_rotator":      {"en": "Rotator", "fr": "Rotateur"},
    "type_focuser":      {"en": "Focuser", "fr": "Porte-oculaire"},
    "type_diagonal":     {"en": "Diagonal", "fr": "Renvoi coudé"},
    "type_adapter":      {"en": "Adapter Ring", "fr": "Bague"},
    "type_spacer":       {"en": "Spacer", "fr": "Espaceur"},
    "type_anti_tilt":    {"en": "Anti-tilt Adapter", "fr": "Anti-tilt"},
    "type_guide_scope":  {"en": "Guide Scope", "fr": "Lunette guide"},
    "type_flip_mirror":  {"en": "Flip Mirror", "fr": "Miroir basculant"},
    "add_part":          {"en": "Add", "fr": "Ajouter"},
    "edit_part":         {"en": "Edit", "fr": "Modifier"},
    "delete_part":       {"en": "Delete", "fr": "Supprimer"},
    "duplicate_part":    {"en": "Duplicate", "fr": "Dupliquer"},
    "add_config":        {"en": "New Config", "fr": "Nouvelle config"},
    "delete_config":     {"en": "Delete", "fr": "Supprimer"},
    "edit_config":       {"en": "Edit", "fr": "Modifier"},
    "dup_config":        {"en": "Duplicate", "fr": "Dupliquer"},
    "add_to_stack":      {"en": "Add part", "fr": "Ajouter pièce"},
    "remove_from_stack": {"en": "Remove", "fr": "Retirer"},
    "move_up":           {"en": "Up", "fr": "Haut"},
    "move_down":         {"en": "Down", "fr": "Bas"},
    "flip_piece":        {"en": "Flip", "fr": "Retourner"},
    "mark_bf_start":     {"en": "Set BF start", "fr": "Début BF"},
    "mark_bf_end":       {"en": "Set BF end", "fr": "Fin BF"},
    "auto_suggest":      {"en": "Suggest part", "fr": "Suggérer pièce"},
    "auto_complete":     {"en": "Auto-complete", "fr": "Auto-compléter"},
    "filter_all":        {"en": "All", "fr": "Tous"},
    "filter_brand":      {"en": "Brand", "fr": "Marque"},
    "filter_type":       {"en": "Type", "fr": "Type"},
    "filter_thread":     {"en": "Thread", "fr": "Filetage"},
    "filter_diameter":   {"en": "Diameter", "fr": "Diamètre"},
    "filter_gender":     {"en": "Gender", "fr": "Genre"},
    "filter_owned":      {"en": "Owned only", "fr": "Possédés"},
    "search":            {"en": "Search…", "fr": "Rechercher…"},
    "reset_filters":     {"en": "Reset", "fr": "Réinit."},
    "config_name":       {"en": "Configuration Name", "fr": "Nom de la configuration"},
    "target_bf":         {"en": "Target BF", "fr": "BF cible"},
    "notes":             {"en": "Notes", "fr": "Notes"},
    "train_label":       {"en": "Optical Train  [ Telescope → Camera ]",
                          "fr": "Train optique  [ Télescope → Caméra ]"},
    "total_label":       {"en": "Total:", "fr": "Total :"},
    "bf_total_label":    {"en": "Backfocus:", "fr": "Backfocus :"},
    "target_label":      {"en": "Target:", "fr": "Cible :"},
    "diff_label":        {"en": "Diff:", "fr": "Écart :"},
    "status_ok":         {"en": "OK", "fr": "OK"},
    "status_short":      {"en": "Short {v:.2f}", "fr": "Court {v:.2f}"},
    "status_long":       {"en": "Long {v:.2f}", "fr": "Long {v:.2f}"},
    "diagram":           {"en": "Diagram", "fr": "Diagramme"},
    "conflict_title":    {"en": "Part conflict", "fr": "Conflit de pièce"},
    "conflict_msg":      {"en": "'{name}' already used in: {cfgs}.\nOwned: {qty}. Used: {used}x.\nAdd anyway?",
                          "fr": "'{name}' déjà utilisé dans : {cfgs}.\nPossédé : {qty}. Utilisé : {used}x.\nAjouter quand même ?"},
    "suggest_title":     {"en": "Suggestions", "fr": "Suggestions"},
    "suggest_gap":       {"en": "Gap: {v:.2f}", "fr": "Écart : {v:.2f}"},
    "suggest_after":     {"en": "After:", "fr": "Après :"},
    "suggest_perfect":   {"en": "PERFECT", "fr": "PARFAIT"},
    "suggest_none":      {"en": "No compatible part found", "fr": "Aucune pièce compatible"},
    "insert":            {"en": "Insert", "fr": "Insérer"},
    "ac_title":          {"en": "Auto-complete results", "fr": "Résultats auto-complétion"},
    "ac_use_other":      {"en": "Allow parts from other configs", "fr": "Autoriser pièces d'autres configs"},
    "ac_use_unowned":    {"en": "Include parts not owned (qty=0)", "fr": "Inclure pièces non possédées (qté=0)"},
    "ac_need_bf":        {"en": "Mark at least one part as BF Start and one as BF End first.",
                          "fr": "Désignez d'abord au moins une pièce comme Début BF et une comme Fin BF."},
    "ac_no_solution":    {"en": "No combination found", "fr": "Aucune combinaison trouvée"},
    "conn_warn_title":   {"en": "Connection warning", "fr": "Alerte connexion"},
    "conn_warn_msg":     {"en": "Incompatible connection!\n\n{prev_name} output: {prev_conn}\n{new_name} input: {new_conn}\n\n{reason}\n\nInsert anyway?",
                          "fr": "Connexion incompatible !\n\n{prev_name} sortie : {prev_conn}\n{new_name} entrée : {new_conn}\n\n{reason}\n\nInsérer quand même ?"},
    "conn_reason_thread":{"en": "Thread mismatch: {a} vs {b}", "fr": "Filetages différents : {a} vs {b}"},
    "conn_reason_gender":{"en": "Same gender: {g}-{g} (need Male-Female)", "fr": "Même genre : {g}-{g} (il faut Mâle-Femelle)"},
    "conn_insert_ghost": {"en": "Insert placeholder", "fr": "Insérer un fantôme"},
    "conn_flip_insert":  {"en": "Flip & insert", "fr": "Retourner et insérer"},
    "conn_mark_flip":    {"en": "Mark reversible & flip", "fr": "Marquer réversible et retourner"},
    "conn_edit_part":    {"en": "Edit part…", "fr": "Modifier la pièce…"},
    "insert_ghost":      {"en": "Insert ghost", "fr": "Insérer fantôme"},
    "ghost_name":        {"en": "? Missing adapter", "fr": "? Adaptateur manquant"},
    "resolve_ghosts":    {"en": "Resolve ghosts", "fr": "Résoudre fantômes"},
    "resolve_title":     {"en": "Resolve placeholder", "fr": "Résoudre le fantôme"},
    "resolve_need":      {"en": "Need: {tside} → {cside}", "fr": "Besoin : {tside} → {cside}"},
    "resolve_none":      {"en": "No matching adapter found in database.", "fr": "Aucun adaptateur correspondant trouvé dans la base."},
    "resolve_replaced":  {"en": "Ghost replaced by '{name}'", "fr": "Fantôme remplacé par '{name}'"},
    "no_ghosts":         {"en": "No placeholder to resolve.", "fr": "Aucun fantôme à résoudre."},
    "save":              {"en": "Save", "fr": "Enregistrer"},
    "cancel":            {"en": "Cancel", "fr": "Annuler"},
    "ok":                {"en": "OK", "fr": "OK"},
    "confirm_delete":    {"en": "Confirm", "fr": "Confirmer"},
    "confirm_delete_msg":{"en": "Delete '{name}'?", "fr": "Supprimer '{name}' ?"},
    "none":              {"en": "(none)", "fr": "(aucun)"},
    "not_reversible":    {"en": "Cannot flip", "fr": "Non réversible"},
    "catalog_title":     {"en": "Parts Catalog", "fr": "Catalogue de pièces"},
    "total_parts":       {"en": "{n} parts", "fr": "{n} pièces"},
    "close":             {"en": "Close", "fr": "Fermer"},
    "drag_hint":         {"en": "Drag a part from the catalog onto the optical train",
                          "fr": "Glissez une pièce du catalogue sur le train optique"},
    "drop_added":        {"en": "'{name}' added to the train", "fr": "'{name}' ajouté au train"},
    "qty_adjust_title":  {"en": "Quantity conflict", "fr": "Conflit de quantité"},
    "qty_not_owned_msg": {"en": "'{name}' is not marked as owned (qty=0).\nSet quantity to 1?",
                          "fr": "'{name}' n'est pas marqué comme possédé (qté=0).\nMettre la quantité à 1 ?"},
    "qty_adjust_msg":    {"en": "'{name}' is used {used}x but you own {qty}.\nAdjust owned quantity to {new_qty}?",
                          "fr": "'{name}' est utilisé {used}x mais vous en possédez {qty}.\nAjuster la quantité possédée à {new_qty} ?"},
    "qty_adjust_custom": {"en": "Set custom quantity:", "fr": "Quantité personnalisée :"},
    "qty_adjusted":      {"en": "Quantity updated to {qty}", "fr": "Quantité mise à jour à {qty}"},
    "drop_cancelled":    {"en": "Drop cancelled", "fr": "Dépôt annulé"},
    "no_config":         {"en": "Select a configuration first", "fr": "Sélectionnez d'abord une configuration"},
    "bf_start_after_end":{"en": "BF Start must be before BF End.", "fr": "Le début BF doit être avant la fin BF."},
    "bf_end_before_start":{"en": "BF End must be after BF Start.", "fr": "La fin BF doit être après le début BF."},
    "fits_analyzer":     {"en": "FITS / XISF Backfocus Analyzer\u2026", "fr": "Analyseur FITS / XISF de backfocus\u2026"},
    "fits_btn":          {"en": "\u2b50 Analyze FITS Image", "fr": "\u2b50 Analyser image FITS"},
    "fits_analyzer_missing_deps": {
        "en": "The FITS analyzer requires additional packages.\n\nRun:\n  pip install numpy scipy astropy photutils matplotlib\n\nOr relaunch with launch.bat / launch.sh to install automatically.",
        "fr": "L'analyseur FITS nécessite des paquets supplémentaires.\n\nExécutez :\n  pip install numpy scipy astropy photutils matplotlib\n\nOu relancez avec launch.bat / launch.sh pour installer automatiquement."},
    "check_updates":     {"en": "Check for Updates…", "fr": "Vérifier les mises à jour…"},
    "update_available":  {"en": "Update Available", "fr": "Mise à jour disponible"},
    "update_title":      {"en": "Update Available", "fr": "Mise à jour disponible"},
    "update_current":    {"en": "Current version: v{current}", "fr": "Version actuelle : v{current}"},
    "update_new":        {"en": "New version: v{new}", "fr": "Nouvelle version : v{new}"},
    "update_changelog":  {"en": "Changelog:", "fr": "Changements :"},
    "update_download":   {"en": "Download && Install", "fr": "Télécharger et installer"},
    "update_skip":       {"en": "Skip", "fr": "Ignorer"},
    "update_downloading":{"en": "Downloading update…", "fr": "Téléchargement de la mise à jour…"},
    "update_installing": {"en": "Installing update…", "fr": "Installation de la mise à jour…"},
    "update_restarting": {"en": "Restarting…", "fr": "Redémarrage…"},
    "update_error":      {"en": "Update failed: {err}", "fr": "Échec de la mise à jour : {err}"},
    "update_up_to_date": {"en": "You are up to date (v{version}).", "fr": "Vous êtes à jour (v{version})."},
    "update_no_connection":{"en": "Could not reach GitHub.\nCheck your internet connection.", "fr": "Impossible de joindre GitHub.\nVérifiez votre connexion internet."},
    "crash_detected":    {"en": "Crash Detected", "fr": "Crash détecté"},
    "crash_report_msg":  {"en": "The application crashed during the last session.\n\nWould you like to send an anonymous bug report?",
                          "fr": "L'application a planté lors de la dernière session.\n\nVoulez-vous envoyer un rapport de bug anonyme ?"},
    "crash_report_send": {"en": "Send Report", "fr": "Envoyer le rapport"},
    "crash_report_skip": {"en": "Skip", "fr": "Ignorer"},
    "crash_report_sent": {"en": "Bug report opened in your browser.\nPlease click 'Submit' to send it.",
                          "fr": "Rapport de bug ouvert dans votre navigateur.\nCliquez sur 'Submit' pour l'envoyer."},
    "error_log":         {"en": "Error Log", "fr": "Journal d'erreurs"},
    "create_shortcut":   {"en": "Create Desktop Shortcut", "fr": "Créer un raccourci bureau"},
}

# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
THREADS = [""] + sorted([
    "M42", "T2 (M42x0.75)", "M48", "M52", "M54", "M56", "M63", "M68", "M72",
    "M81", "M82", "M84", "M92", "M117",
    "SC (Schmidt-Cassegrain)", "EOS", "Canon RF", "Nikon F", "Nikon Z",
    "Sony E", "Fuji X", "MFT", "Pentax K", "CS", '1.25"', '2"',
    "ZWO 6-bolt", "ZWO 4-bolt", "QHY 4-bolt",
])
GENDERS = ["", "Female", "Male"]
PART_TYPES = [
    "type_telescope", "type_refractor", "type_camera_lens",
    "type_camera", "type_dslr", "type_eyepiece",
    "type_barlow", "type_reducer", "type_flattener", "type_extender", "type_corrector",
    "type_filter_wheel", "type_filter_holder",
    "type_oag", "type_rotator", "type_focuser", "type_diagonal",
    "type_adapter", "type_spacer", "type_anti_tilt",
    "type_guide_scope", "type_flip_mirror",
]
NOT_REVERSIBLE = {
    "type_telescope", "type_refractor", "type_camera_lens",
    "type_camera", "type_dslr", "type_eyepiece",
    "type_rotator", "type_oag", "type_focuser", "type_diagonal",
    "type_guide_scope", "type_flip_mirror",
}
BF_ROLE_START_TYPES = {"type_reducer", "type_flattener", "type_extender", "type_corrector", "type_barlow"}
BF_ROLE_END_TYPES   = {"type_camera", "type_dslr", "type_eyepiece"}
DIAMETERS = ["All"] + sorted(["M42", "M48", "M52", "M54", "M68", "M72", "M81", "SC", "T2", "EOS"])

def _resource_path(filename):
    """Get path to resource, works with PyInstaller frozen exe."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

# Data files stay in project dir (not frozen bundle) for portability
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(_APP_DIR, "backfocus_data.json")
_CRASH_FILE = os.path.join(_APP_DIR, "_crash_report.json")
_ERROR_LOG = os.path.join(_APP_DIR, "backfocus_errors.log")

try:
    from reference_data import REFERENCE_DB
except ImportError:
    REFERENCE_DB = []

try:
    from fits_analyzer import FITSAnalyzerWindow
    _HAS_FITS_ANALYZER = True
except ImportError:
    _HAS_FITS_ANALYZER = False

_REF_INDEX = {}
_REF_BRANDS = set()
for _ref in REFERENCE_DB:
    _key = (_ref.get("brand","") + " " + _ref.get("name","")).lower().strip()
    _REF_INDEX[_key] = _ref
    _REF_BRANDS.add(_ref.get("brand",""))
_REF_KEYS_SORTED = sorted(_REF_INDEX.keys())

import platform as _platform
_os_name = _platform.system()
FONT_FAMILY = "Segoe UI" if _os_name == "Windows" else ("SF Pro Display" if _os_name == "Darwin" else "DejaVu Sans")
FONT_MONO = "Cascadia Code" if _os_name == "Windows" else "DejaVu Sans Mono"

# ═══════════════════════════════════════════════════════════════════
#  COLOR PALETTE (Soft Space Theme – varied pastels)
# ═══════════════════════════════════════════════════════════════════
C = {
    "bg_dark":       "#1A1A2A",
    "bg_mid":        "#222234",
    "bg_light":      "#2C2C40",
    "bg_hover":      "#38384E",
    "bg_selected":   "#483870",
    "fg_main":       "#D8D8E4",
    "fg_dim":        "#807896",
    "fg_bright":     "#F2EEF8",
    "accent_blue":   "#88BCDE",
    "accent_purple": "#C09AE8",
    "accent_teal":   "#80D8CC",
    "accent_pink":   "#E8AACC",
    "accent_gold":   "#E4C880",
    "accent_green":  "#96DCAE",
    "accent_red":    "#E08878",
    "accent_orange": "#E4B878",
    "border":        "#403850",
    "bf_zone":       "#283838",
    "canvas_bg":     "#1C1C2C",
    "tree_odd":      "#20202E",
    "tree_even":     "#282836",
    "separator":     "#3A3450",
    "tab_active":    "#2C2C40",
    "tab_inactive":  "#1E1E28",
    "menu_bg":       "#222234",
    "btn_bg":        "#303044",
    "btn_hover":     "#484060",
    "btn_active":    "#5A4A7C",
    "owned_bg":      "#282820",
    "notowned_fg":   "#686078",
}

TYPE_COLORS = {
    "type_telescope": "#E09484", "type_refractor": "#D88C7C", "type_camera_lens": "#C88474",
    "type_camera": "#88BCDE", "type_dslr": "#7EB0D0", "type_eyepiece": "#78A8C8",
    "type_filter_wheel": "#C09AE8", "type_filter_holder": "#B892D8",
    "type_oag": "#80D8CC", "type_rotator": "#E4B878", "type_focuser": "#D0A87A",
    "type_adapter": "#909CA6", "type_spacer": "#A0A0AC",
    "type_reducer": "#96DCAE", "type_flattener": "#90D4A8", "type_extender": "#78BC90",
    "type_corrector": "#78BC90", "type_barlow": "#80C498",
    "type_anti_tilt": "#E4C880", "type_diagonal": "#C8B08A",
    "type_guide_scope": "#80B8D0", "type_flip_mirror": "#B890B8",
}

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def _center_dlg(dlg, parent):
    """Center a dialog on its parent."""
    pg = parent.geometry()
    dg = dlg.geometry()
    x = pg.x() + (pg.width() - dg.width()) // 2
    y = pg.y() + (pg.height() - dg.height()) // 2
    dlg.move(max(0, x), max(0, y))

def _default_data():
    return {"language": "fr", "length_unit": "mm", "mass_unit": "g",
            "parts": [], "configurations": []}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                d = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return _default_data()
        for k, v in _default_data().items():
            d.setdefault(k, v)
        for p in d.get("parts", []):
            if p.get("owned", False) and p.get("qty", 0) == 0:
                p["qty"] = 1
        return d
    return _default_data()

def _write_json_sync(json_str):
    """Write pre-serialized JSON string to disk atomically."""
    tmp = DATA_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(json_str)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, DATA_FILE)
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        _log_error(f"Save error: {e}")

class _AsyncSaveWriter:
    """Background thread that writes JSON to disk without blocking the UI."""
    def __init__(self):
        self._queue = queue.Queue(maxsize=1)
        self._done = threading.Event()
        self._done.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while True:
            json_str = self._queue.get()
            self._done.clear()
            _write_json_sync(json_str)
            self._done.set()

    def schedule(self, data):
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        try:
            self._queue.get_nowait()
        except queue.Empty:
            pass
        self._queue.put(json_str)

    def flush_sync(self):
        self._done.wait(timeout=5)

_save_writer = _AsyncSaveWriter()

def save_data(data, sync=False):
    if sync:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        _write_json_sync(json_str)
    else:
        _save_writer.schedule(data)

# ═══════════════════════════════════════════════════════════════════
#  AUTO-UPDATE HELPERS
# ═══════════════════════════════════════════════════════════════════
_UPDATE_REPO = "ARP273-ROSE/backfocus"
_UPDATE_FILE_WHITELIST = {
    "backfocus.py", "fits_analyzer.py", "reference_data.py", "gen_refdb.py",
    "test_audit.py", "launch.bat", "launch.sh", "requirements.txt",
    "README.md", ".gitattributes", ".gitignore", "shortcut_helper.py",
}
_UPDATE_DIR_WHITELIST = {"manual"}

def _parse_version(tag):
    s = tag.strip().lstrip("vV")
    parts = []
    for p in s.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)

def _check_for_update():
    try:
        import urllib.request, json as _json
        url = f"https://api.github.com/repos/{_UPDATE_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "User-Agent": "BackfocusCalculator"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read().decode())
        tag = data.get("tag_name", "")
        if not tag:
            return "up_to_date"
        remote = _parse_version(tag)
        local = _parse_version(VERSION)
        if remote > local:
            zurl = data.get("zipball_url", "")
            if not zurl.startswith(f"https://api.github.com/repos/{_UPDATE_REPO}/"):
                return None
            return {"tag": tag, "version": tag.lstrip("vV"),
                    "body": data.get("body", ""), "zipball_url": zurl}
        return "up_to_date"
    except Exception:
        return None

_MAX_UPDATE_SIZE = 50 * 1024 * 1024

def _download_and_apply_update(zipball_url):
    import urllib.request, zipfile, tempfile, shutil
    app_dir = _APP_DIR
    tmp_zip = os.path.join(tempfile.mkdtemp(prefix="backfocus_"), "update.zip")
    tmp_dir = tempfile.mkdtemp(prefix="backfocus_extract_")
    try:
        req = urllib.request.Request(zipball_url, headers={"User-Agent": "BackfocusCalculator"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(tmp_zip, "wb") as f:
                total = 0
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > _MAX_UPDATE_SIZE:
                        raise ValueError("Download exceeds 50 MB limit")
                    f.write(chunk)
        real_tmp = os.path.realpath(tmp_dir)
        with zipfile.ZipFile(tmp_zip) as zf:
            for info in zf.infolist():
                if info.filename.startswith('/') or '..' in info.filename:
                    raise ValueError(f"Unsafe zip entry: {info.filename}")
                target = os.path.realpath(os.path.join(tmp_dir, info.filename))
                if not target.startswith(real_tmp + os.sep) and target != real_tmp:
                    raise ValueError(f"Zip path traversal: {info.filename}")
                if info.external_attr and (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f"Symlink in zip: {info.filename}")
            zf.extractall(tmp_dir)
        entries = os.listdir(tmp_dir)
        src_root = os.path.join(tmp_dir, entries[0]) if len(entries) == 1 else tmp_dir
        for fname in os.listdir(src_root):
            src_path = os.path.join(src_root, fname)
            dst_path = os.path.join(app_dir, fname)
            if os.path.islink(src_path):
                continue
            if os.path.isfile(src_path) and fname in _UPDATE_FILE_WHITELIST:
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path) and fname in _UPDATE_DIR_WHITELIST:
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path, symlinks=False)
    finally:
        parent_zip = os.path.dirname(tmp_zip)
        if os.path.isdir(parent_zip):
            shutil.rmtree(parent_zip, ignore_errors=True)
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

def _merge_reference_db(data):
    by_key = {}
    for i, p in enumerate(data["parts"]):
        by_key[(p.get("brand",""), p.get("name",""))] = i
    added = 0
    SPEC_FIELDS = ("type","optical_length","mass","tside_thread","tside_gender",
                   "cside_thread","cside_gender","reversible","bf_role")
    ref_keys = set()
    for ref in REFERENCE_DB:
        key = (ref.get("brand",""), ref.get("name",""))
        ref_keys.add(key)
        if key in by_key:
            p = data["parts"][by_key[key]]
            for f in SPEC_FIELDS:
                if f in ref:
                    p[f] = ref[f]
        else:
            data["parts"].append(dict(ref, qty=0))
            added += 1
    purged = 0
    kept = []
    for p in data["parts"]:
        key = (p.get("brand",""), p.get("name",""))
        if key in ref_keys or p.get("qty", 0) > 0 or p.get("notes", ""):
            kept.append(p)
        else:
            purged += 1
    data["parts"] = kept
    return added, purged

def _extract_diam(conn):
    if not conn:
        return ""
    for d in ("M117","M92","M84","M82","M81","M72","M68","M63","M56","M54","M52","M48","M42"):
        if d in conn:
            return d
    for m in ("SC","T2","EOS","Canon RF","Nikon F","Nikon Z","Sony E","Fuji X",
              "MFT","Pentax K","CS","ZWO 6-bolt","ZWO 4-bolt","QHY 4-bolt"):
        if m in conn:
            return m
    return conn

def _conn_compat(thread_a, gender_a, thread_b, gender_b):
    if not thread_a or not thread_b:
        return True
    if _extract_diam(thread_a) != _extract_diam(thread_b):
        return False
    if gender_a and gender_b and gender_a == gender_b:
        return False
    return True

def _effective(item):
    if item.get("flipped"):
        return {"tside_thread": item.get("cside_thread",""), "tside_gender": item.get("cside_gender",""),
                "cside_thread": item.get("tside_thread",""), "cside_gender": item.get("tside_gender","")}
    return item

def _fmt_len(val, unit="mm"):
    if unit == "in":
        return f'{val/25.4:.4f}"'
    return f"{val:.2f} mm"

def _fmt_mass(val, unit="g"):
    if unit == "oz":
        return f"{val/28.3495:.2f} oz"
    return f"{val:.0f} g"

def _safe_int(s, default=0):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

# ═══════════════════════════════════════════════════════════════════
#  PATH ANONYMIZATION (for bug reports — never expose username)
# ═══════════════════════════════════════════════════════════════════
def _anonymize_path(text):
    """Replace user home directory with ~ in text to avoid exposing username."""
    if not text:
        return text
    import pathlib
    home = str(pathlib.Path.home())
    # Windows paths (both / and \ separators)
    text = text.replace(home.replace("\\", "/"), "~")
    text = text.replace(home, "~")
    # Also handle common patterns with different case on Windows
    if sys.platform == "win32":
        text = text.replace(home.lower(), "~")
        text = text.replace(home.upper(), "~")
    return text

# ═══════════════════════════════════════════════════════════════════
#  ERROR LOGGING & CRASH CAPTURE
# ═══════════════════════════════════════════════════════════════════
_MAX_ERROR_LOG_BYTES = 100 * 1024

def _log_error(msg):
    try:
        from datetime import datetime
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
        if os.path.exists(_ERROR_LOG):
            try:
                sz = os.path.getsize(_ERROR_LOG)
                if sz > _MAX_ERROR_LOG_BYTES:
                    with open(_ERROR_LOG, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    lines = content.splitlines(True)
                    half = len(lines) // 2
                    with open(_ERROR_LOG, "w", encoding="utf-8") as f:
                        f.writelines(lines[half:])
            except OSError:
                pass
        with open(_ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass

def _global_exception_handler(exc_type, exc_value, exc_tb):
    import traceback
    from datetime import datetime
    tb_str = _anonymize_path("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    _log_error(f"CRASH: {exc_type.__name__}: {exc_value}\n{tb_str}")
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR
        qt_ver = PYQT_VERSION_STR
    except Exception:
        qt_ver = "?"
    try:
        crash = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "version": VERSION,
            "os": _platform.system(),
            "python": _platform.python_version(),
            "arch": _platform.machine(),
            "qt": f"PyQt6 {qt_ver}",
            "error_type": exc_type.__name__,
            "error_msg": _anonymize_path(str(exc_value)),
            "traceback": tb_str,
        }
        with open(_CRASH_FILE, "w", encoding="utf-8") as f:
            json.dump(crash, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

def _get_recent_errors(n=10):
    try:
        if not os.path.exists(_ERROR_LOG):
            return ""
        with open(_ERROR_LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:]).strip()
    except OSError:
        return ""

# ═══════════════════════════════════════════════════════════════════
#  GALAXY CURSOR
# ═══════════════════════════════════════════════════════════════════
class GalaxyCursor(QWidget):
    SIZE = 22
    POLL_MS = 33
    OFFSET = 20
    LERP = 0.45

    def __init__(self, parent_window):
        super().__init__(None)
        self.parent_window = parent_window
        self._paused = False
        self._stopped = False
        self._cur_x = 0.0
        self._cur_y = 0.0
        self._last_ix = -1
        self._last_iy = -1
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.SIZE, self.SIZE)
        self._pixmap = self._create_galaxy()
        self.show()
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(self.POLL_MS)

    def _create_galaxy(self):
        img = QImage(self.SIZE, self.SIZE, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        S = self.SIZE; cx, cy = S/2, S/2
        rng = random.Random(42)
        def px(x, y, col):
            ix, iy = int(round(x)), int(round(y))
            if 0 <= ix < S and 0 <= iy < S:
                img.setPixelColor(ix, iy, QColor(col))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                px(cx+dx, cy+dy, "#3A2A10")
        px(cx, cy, "#C8B060")
        px(cx-1, cy, "#786028"); px(cx+1, cy, "#786028")
        px(cx, cy-1, "#786028"); px(cx, cy+1, "#786028")
        arm_pal = ["#B09848","#90A0B0","#78A0C8","#60A0D8","#5098D0"]
        for off in (0, math.pi):
            for i in range(40):
                f = i/40; t = f*2.2*math.pi + off; r2 = 1.8 + f*8.5
                x = cx + r2*math.cos(t); y = cy + r2*math.sin(t)
                ci = min(int(f*len(arm_pal)), len(arm_pal)-1)
                px(x, y, arm_pal[ci])
                if rng.random() < .15:
                    dx2, dy2 = rng.choice([-1,0,1]), rng.choice([-1,0,1])
                    px(x+dx2, y+dy2, "#88B0D0")
        for _ in range(4):
            x, y = rng.uniform(1,S-1), rng.uniform(1,S-1)
            if (x-cx)**2+(y-cy)**2 > 35:
                px(x, y, "#A8B8D0")
        return QPixmap.fromImage(img)

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawPixmap(0, 0, self._pixmap)

    def pause(self):
        self._paused = True; self.hide()

    def resume(self):
        self._paused = False; self.show()

    def stop(self):
        self._stopped = True; self._timer.stop(); self.close()

    def _poll(self):
        if self._stopped or self._paused:
            return
        try:
            pos = QCursor.pos()
            tx = pos.x() + self.OFFSET; ty = pos.y() + self.OFFSET
            self._cur_x += (tx - self._cur_x) * self.LERP
            self._cur_y += (ty - self._cur_y) * self.LERP
            ix, iy = int(self._cur_x), int(self._cur_y)
            if ix != self._last_ix or iy != self._last_iy:
                self._last_ix = ix; self._last_iy = iy
                self.move(ix, iy)
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════════
#  HELP WINDOW
# ═══════════════════════════════════════════════════════════════════
def _build_help_html(lang):
    v = VERSION
    css = f"""<style>
body {{ background:{C['bg_dark']}; color:{C['fg_main']}; font-family:'{FONT_FAMILY}'; font-size:10pt; padding:15px 20px; }}
h1 {{ color:{C['accent_blue']}; font-size:16pt; margin-top:20px; }}
h2 {{ color:{C['accent_teal']}; font-size:12pt; margin-top:15px; }}
h3 {{ color:{C['accent_purple']}; font-size:10pt; margin-top:10px; }}
ul {{ margin-left:15px; }}
li {{ margin:3px 0; }}
code {{ font-family:'{FONT_MONO}'; color:{C['accent_green']}; }}
</style>"""
    def sec(t, lv=1): return f"<h{lv}>{t}</h{lv}>"
    def par(t): return f"<p>{t}</p>"
    def bul(items): return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    if lang == "fr":
        return css + f"""
{sec(f"Calculateur de Backfocus v{v} — Guide complet")}
{par("Bienvenue ! Cette application vous aide à concevoir et vérifier vos trains optiques pour l'astrophotographie. Thème sombre spatial, curseur galaxie, base de 12 000+ produits réels.")}
{sec("1. Démarrage rapide", 2)}
{bul(["Au premier lancement, la base de 12 000+ produits est chargée automatiquement dans votre catalogue.",
"Toutes les données sont sauvegardées automatiquement à chaque fermeture dans backfocus_data.json.",
"Utilisez le menu Langue pour passer de Français à English à tout moment."])}
{sec("2. Catalogue de pièces", 2)}
{par("Ouvrez le catalogue via le menu Affichage > Catalogue de pièces ou le bouton dans la barre d'outils.")}
{sec("Ajouter / Modifier une pièce", 3)}
{bul(["Cliquez « Ajouter » et remplissez : Marque, Nom, Type (22 catégories), Longueur optique (mm), Masse (g).",
"Connexions : côté télescope et côté caméra, chacun avec filetage + genre (Mâle/Femelle).",
"Cochez Réversible si la pièce peut être retournée. Définissez le Rôle BF (start/end) si applicable.",
"Utilisez le bouton « Auto-fill » pour remplir tous les champs depuis la base de 12 000+ produits (125 marques).",
"Double-cliquez une pièce pour la modifier. Utilisez « Dupliquer » pour créer une copie."])}
{sec("Quantité possédée", 3)}
{bul(["Utilisez les boutons +/− pour ajuster rapidement la quantité.",
"Les pièces possédées (qté > 0) sont affichées en doré. Les autres sont grisées."])}
{sec("Filtres et tri", 3)}
{bul(["Barre de recherche : filtrez par texte (marque/nom).",
"Filtres combinables : type, diamètre de filetage, genre (M/F), possédées uniquement.",
"Cliquez sur les en-têtes de colonnes pour trier par n'importe quel critère.",
"Bouton « Réinit. » pour effacer tous les filtres."])}
{sec("3. Configurations", 2)}
{par("La fenêtre principale est dédiée aux configurations de trains optiques.")}
{bul(["Cliquez « + » pour créer une nouvelle configuration.",
"Donnez un nom et un backfocus cible en mm (ex: 55).",
"Cliquez « Ajouter pièce » pour insérer une pièce de votre catalogue.",
"Le télescope est en haut (gauche), la caméra en bas (droite) — convention du chemin lumineux.",
"Utilisez Haut/Bas pour réordonner, « Retourner » pour inverser une pièce réversible."])}
{sec("4. Pièces fantômes", 2)}
{par("Quand les connexions sont incompatibles, l'appli propose : Retourner, Insérer quand même, Insérer un fantôme, ou Modifier la pièce.")}
{bul(["Le fantôme (orange) représente une bague d'adaptation à trouver.",
"« Résoudre fantômes » cherche les pièces compatibles dans votre catalogue.",
"Vous pouvez aussi insérer un fantôme manuellement."])}
{sec("5. Zone de backfocus", 2)}
{bul(["Sélectionnez la pièce de début BF et cliquez « Début BF ».",
"Sélectionnez la pièce de fin BF et cliquez « Fin BF ».",
"BF calculé = somme des longueurs optiques après le début jusqu'à la fin. La pièce de début sert de point zéro.",
"L'écart est affiché en couleur : vert (OK), orange (court), rouge (long)."])}
{sec("6. Suggestions & Auto-complétion", 2)}
{bul(["« Suggérer pièce » cherche UNE pièce possédée qui comblerait l'écart.",
"« Auto-compléter » cherche des combinaisons de 1, 2 ou 3 pièces."])}
{sec("7. Compatibilité des connexions", 2)}
{bul(["Le diamètre de filetage doit correspondre (ex: M42 ↔ M42).",
"Les genres doivent être opposés (Mâle ↔ Femelle).",
"Filetages métriques : M42/T2, M48, M54, M56, M63, M68, M72, M81, M82, M84, M92, M117.",
"Montures photo : EOS, Canon RF, Nikon F/Z, Sony E, Fuji X, MFT, Pentax K.",
"Coulants : 1.25\", 2\". Fixations : SC, ZWO/QHY bolt."])}
{sec("8. Unités de mesure", 2)}
{bul(["Menu Paramètres > Unités de mesure. Longueurs : mm ou pouces. Masse : grammes ou onces."])}
{sec("9. Sauvegarde & Export", 2)}
{bul(["Sauvegarde automatique à chaque fermeture dans backfocus_data.json.",
"« Tout enregistrer » pour sauvegarder manuellement.",
"Export/Import de configuration ou de toutes les données en JSON."])}
{sec("10. Diagramme visuel", 2)}
{bul(["Le diagramme en bas représente le train optique en couleurs.",
"La zone de backfocus est mise en surbrillance.",
"Une ligne pointillée rouge indique la cible de backfocus."])}
{sec("11. Raccourcis clavier", 2)}
{bul(["Entrée : confirmer. Échap : fermer/annuler.",
"Double-clic sur une pièce du catalogue : modifier.",
"Double-clic dans la liste de suggestions : insérer."])}
{sec("12. 22 types de pièces", 2)}
{bul(["Télescope, Lunette, Objectif photo, Caméra astro, Reflex/Hybride, Oculaire.",
"Barlow, Réducteur, Aplanisseur, Extenseur, Correcteur de coma.",
"Roue à filtres, Porte-filtre, OAG, Rotateur, Porte-oculaire, Renvoi coudé.",
"Bague d'adaptation, Espaceur, Anti-tilt, Lunette guide, Miroir basculant."])}
{sec("13. Analyseur FITS / XISF de backfocus", 2)}
{bul(["Menu Affichage > Analyseur FITS / XISF de backfocus.",
"Formats : FITS (.fits/.fit/.fts), FITS compressé (.fits.fz), XISF (.xisf).",
"Détection d'étoiles → ajustement gaussien 2D → carte FWHM → verdict.",
"Mosaïque 3×3 : 9 crops avec FWHM moyen et qualité relative au centre."])}
{sec("14. Rapports de bugs et capture de crashs", 2)}
{bul(["Capture automatique des crashs dans backfocus_errors.log et _crash_report.json.",
"Détection au redémarrage avec envoi optionnel via GitHub Issues.",
"Rapport manuel via menu Aide > Signaler un bug."])}
{sec("15. Performance et fluidité (v2.0)", 2)}
{bul(["Interface PyQt6 native, thème sombre intégré.",
"Sauvegarde asynchrone : écriture sur disque déportée sur un thread dédié.",
"Curseur galaxie optimisé : 30 fps, skip si position inchangée.",
"Quantités +/− rapides : seule la ligne modifiée est mise à jour.",
"Cache de recherche pièces : index pré-calculé pour 12 000+ pièces."])}
{sec("16. Mises à jour automatiques", 2)}
{bul(["Vérification silencieuse au démarrage (thread en arrière-plan, 2s de délai).",
"Vérification manuelle via Aide > Vérifier les mises à jour.",
"Compare la version locale avec les GitHub Releases.",
"Dialogue de mise à jour : version actuelle/nouvelle, changelog, boutons Télécharger/Ignorer.",
"Téléchargement sécurisé : limite de taille, validation zip, anti path-traversal.",
"Redémarrage automatique après mise à jour."])}
{sec("17. Raccourci bureau et multi-PC", 2)}
{bul(["Menu Aide > Créer un raccourci bureau. Fonctionne sur Windows, Linux, macOS.",
"Le raccourci cible launch.bat / launch.sh (portable entre PCs).",
"L'environnement virtuel (venv) est créé localement sur chaque PC.",
"Windows : %LOCALAPPDATA%\\\\BackfocusCalculator\\\\venv",
"Linux/macOS : ~/.local/share/BackfocusCalculator/venv",
"Le dossier projet peut être sur un NAS ou un disque synchronisé sans conflit."])}
"""
    else:
        return css + f"""
{sec(f"Backfocus Calculator v{v} — Complete Guide")}
{par("Welcome! This application helps you design and verify optical trains for astrophotography. Dark space theme, galaxy cursor, 12,000+ real product database.")}
{sec("1. Quick Start", 2)}
{bul(["On first launch, the 12,000+ product database is automatically loaded into your catalog.",
"All data is saved automatically on close to backfocus_data.json.",
"Use the Language menu to switch between English and Français at any time."])}
{sec("2. Parts Catalog", 2)}
{par("Open the catalog via View > Parts Catalog or the toolbar button.")}
{bul(["Click 'Add' and fill in: Brand, Name, Type (22 categories), Optical Length (mm), Mass (g).",
"Connections: telescope-side and camera-side, each with thread + gender (Male/Female).",
"Check Reversible if the part can be flipped. Set BF Role (start/end) if applicable.",
"Use 'Auto-fill' to populate from the 12,000+ product database.",
"Double-click a part to edit it. Use 'Duplicate' to create a copy.",
"Use +/− buttons to adjust owned quantity. Owned parts shown in gold."])}
{sec("3. Configurations", 2)}
{bul(["Click '+' to create a new configuration with a name and target BF (mm).",
"Click 'Add part' to insert parts. Telescope at top, camera at bottom.",
"Use Up/Down to reorder, 'Flip' to reverse a reversible part."])}
{sec("4. Ghost Pieces", 2)}
{bul(["When connections are incompatible: Flip, Insert anyway, Insert ghost, or Edit part.",
"Ghost (orange) = missing adapter. 'Resolve ghosts' searches your catalog.",
"You can also insert a ghost manually."])}
{sec("5. Backfocus Zone", 2)}
{bul(["Select start part → 'Set BF start'. Select end part → 'Set BF end'.",
"BF = sum of optical lengths after start up to end. Start piece = zero point.",
"Gap is color-coded: green (OK), orange (short), red (long)."])}
{sec("6. Suggest & Auto-complete", 2)}
{bul(["'Suggest part' finds ONE owned part that fills the gap.",
"'Auto-complete' searches for combinations of 1, 2, or 3 parts."])}
{sec("7. Connection Compatibility", 2)}
{bul(["Thread diameter must match (e.g., M42 ↔ M42). Genders must be opposite.",
"Metric threads: M42/T2, M48, M54–M117. Camera mounts: EOS, Canon RF, Nikon F/Z, Sony E, etc.",
"Barrels: 1.25\", 2\". Bolt mounts: ZWO/QHY."])}
{sec("8. Measurement Units", 2)}
{bul(["Settings > Measurement Units. Lengths: mm or inches. Mass: grams or ounces."])}
{sec("9. Save & Export", 2)}
{bul(["Auto-save on close. 'Save All' for manual save.",
"Export/Import configuration or all data as JSON."])}
{sec("10. Visual Diagram", 2)}
{bul(["Diagram at bottom shows the optical train in color.",
"BF zone highlighted. Dashed red line = BF target."])}
{sec("11. Keyboard Shortcuts", 2)}
{bul(["Enter: confirm. Escape: close/cancel.",
"Double-click catalog part: edit. Double-click suggestion: insert."])}
{sec("12. 22 Part Types", 2)}
{bul(["Telescope, Refractor, Camera Lens, Astro Camera, DSLR/Mirrorless, Eyepiece.",
"Barlow, Reducer, Flattener, Extender, Coma Corrector.",
"Filter Wheel, Filter Holder, OAG, Rotator, Focuser, Diagonal.",
"Adapter Ring, Spacer, Anti-tilt, Guide Scope, Flip Mirror."])}
{sec("13. FITS / XISF Backfocus Analyzer", 2)}
{bul(["View > FITS/XISF Backfocus Analyzer.",
"Formats: FITS (.fits/.fit/.fts), compressed FITS (.fits.fz), XISF (.xisf).",
"Star detection → 2D Gaussian fit → FWHM map → verdict.",
"Mosaic 3×3: 9 crops with mean FWHM and quality vs center."])}
{sec("14. Bug Reports & Crash Capture", 2)}
{bul(["Automatic crash capture in backfocus_errors.log and _crash_report.json.",
"Detection on restart with optional GitHub Issue submission.",
"Manual report via Help > Report Bug."])}
{sec("15. Performance & Fluidity (v2.0)", 2)}
{bul(["Native PyQt6 interface with built-in dark theme.",
"Async save: disk I/O offloaded to dedicated thread.",
"Galaxy cursor: 30 fps, skip if position unchanged.",
"Fast qty +/−: only affected row updated.",
"Parts search cache: pre-built index for 12,000+ parts."])}
{sec("16. Automatic Updates", 2)}
{bul(["Silent check on startup (background thread, 2s delay).",
"Manual check via Help > Check for Updates.",
"Compares local version against GitHub Releases.",
"Update dialog: current/new version, changelog, Download/Skip buttons.",
"Secure download: size limit, zip validation, anti path-traversal.",
"Automatic restart after update."])}
{sec("17. Desktop Shortcut & Multi-PC", 2)}
{bul(["Help > Create Desktop Shortcut. Works on Windows, Linux, macOS.",
"Shortcut targets launch.bat / launch.sh (portable across PCs).",
"Virtual environment (venv) created locally on each PC.",
"Windows: %LOCALAPPDATA%\\\\BackfocusCalculator\\\\venv",
"Linux/macOS: ~/.local/share/BackfocusCalculator/venv",
"Project folder can live on a NAS or synced drive without conflicts."])}
"""

def open_help(parent, lang="en"):
    dlg = QDialog(parent)
    dlg.setWindowTitle("User Guide" if lang == "en" else "Guide d'utilisation")
    dlg.resize(920, 720)
    dlg.setStyleSheet(f"background: {C['bg_mid']};")
    layout = QVBoxLayout(dlg)
    browser = QTextBrowser()
    browser.setOpenExternalLinks(True)
    browser.setStyleSheet(f"background: {C['bg_dark']}; color: {C['fg_main']}; border: none; padding: 10px;")
    browser.setHtml(_build_help_html(lang))
    layout.addWidget(browser)
    dlg.exec()

# ═══════════════════════════════════════════════════════════════════
#  QSS STYLESHEET
# ═══════════════════════════════════════════════════════════════════
def _build_stylesheet():
    return f"""
QMainWindow, QDialog {{ background: {C['bg_mid']}; color: {C['fg_main']}; }}
QWidget {{ font-family: '{FONT_FAMILY}'; font-size: 9pt; }}
QLabel {{ color: {C['fg_main']}; }}
QPushButton {{
    background: {C['btn_bg']}; color: {C['fg_main']}; border: 1px solid {C['border']};
    border-radius: 6px; padding: 6px 12px; font-size: 9pt;
}}
QPushButton:hover {{ background: {C['btn_hover']}; }}
QPushButton:pressed {{ background: {C['btn_active']}; }}
QPushButton:disabled {{ color: {C['fg_dim']}; }}
QPushButton[accent="true"] {{
    background: {C['accent_teal']}; color: {C['bg_dark']}; font-weight: bold;
}}
QPushButton[accent="true"]:hover {{ background: {C['accent_green']}; }}
QPushButton[fits="true"] {{
    background: {C['accent_purple']}; color: {C['fg_bright']}; font-weight: bold;
    font-size: 10pt; padding: 8px 18px;
}}
QPushButton[fits="true"]:hover {{ background: #D0ACF0; }}
QPushButton[small="true"] {{ padding: 3px 6px; font-size: 8pt; }}
QLineEdit {{
    background: {C['bg_light']}; color: {C['fg_main']}; border: 1px solid {C['border']};
    border-radius: 3px; padding: 4px;
}}
QLineEdit:focus {{ border-color: {C['accent_purple']}; background: {C['bg_hover']}; }}
QComboBox {{
    background: {C['bg_light']}; color: {C['fg_main']}; border: 1px solid {C['border']};
    border-radius: 3px; padding: 3px 4px;
}}
QComboBox:focus {{ border-color: {C['accent_purple']}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background: {C['bg_light']}; color: {C['fg_main']}; selection-background-color: {C['bg_selected']};
}}
QCheckBox {{ color: {C['fg_main']}; }}
QCheckBox::indicator {{ width: 14px; height: 14px; }}
QCheckBox::indicator:checked {{ background: {C['accent_teal']}; border: 1px solid {C['accent_teal']}; border-radius: 3px; }}
QCheckBox::indicator:unchecked {{ background: {C['bg_light']}; border: 1px solid {C['border']}; border-radius: 3px; }}
QTreeWidget {{
    background: {C['tree_odd']}; color: {C['fg_main']}; border: none;
    alternate-background-color: {C['tree_even']};
}}
QTreeWidget::item {{ padding: 4px 2px; }}
QTreeWidget::item:selected {{ background: {C['bg_selected']}; color: {C['fg_bright']}; }}
QHeaderView::section {{
    background: {C['bg_dark']}; color: {C['accent_teal']}; border: none;
    font-weight: bold; padding: 4px; font-size: 9pt;
}}
QListWidget {{
    background: {C['bg_light']}; color: {C['fg_main']}; border: none;
}}
QListWidget::item:selected {{ background: {C['bg_selected']}; color: {C['fg_bright']}; }}
QGroupBox {{
    background: {C['bg_mid']}; border: 1px groove {C['border']}; border-radius: 4px;
    margin-top: 8px; padding-top: 14px;
}}
QGroupBox::title {{
    color: {C['accent_pink']}; font-weight: bold; subcontrol-origin: margin;
    left: 10px; padding: 0 4px;
}}
QSplitter::handle {{ background: {C['separator']}; }}
QScrollBar:vertical {{
    background: {C['bg_dark']}; width: 12px; border: none;
}}
QScrollBar::handle:vertical {{ background: {C['bg_light']}; border-radius: 4px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background: {C['bg_hover']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {C['bg_dark']}; height: 12px; border: none;
}}
QScrollBar::handle:horizontal {{ background: {C['bg_light']}; border-radius: 4px; min-width: 20px; }}
QProgressBar {{
    background: {C['bg_dark']}; border: none; border-radius: 4px; text-align: center;
}}
QProgressBar::chunk {{ background: {C['accent_teal']}; border-radius: 4px; }}
QMenuBar {{ background: {C['menu_bg']}; color: {C['fg_main']}; }}
QMenuBar::item:selected {{ background: {C['bg_selected']}; }}
QMenu {{ background: {C['menu_bg']}; color: {C['fg_main']}; border: 1px solid {C['border']}; }}
QMenu::item:selected {{ background: {C['bg_selected']}; color: {C['fg_bright']}; }}
QMenu::separator {{ background: {C['separator']}; height: 1px; margin: 4px 8px; }}
QTextBrowser {{ background: {C['bg_dark']}; color: {C['fg_main']}; border: none; }}
"""

# ═══════════════════════════════════════════════════════════════════
#  DIAGRAM WIDGET
# ═══════════════════════════════════════════════════════════════════
class DiagramWidget(QWidget):
    itemMoved = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stack = []
        self._bf_total = 0
        self._target = 0
        self._bs = -1
        self._be = -1
        self._ranges = []
        self._drag_idx = None
        self._drag_target = None
        self._drag_started = False
        self._drag_x0 = 0
        self._mouse_x = 0
        self.setMinimumHeight(80)
        self.setStyleSheet(f"background: {C['canvas_bg']};")

    def set_data(self, stack, bs, be, target):
        self._stack = list(stack)
        self._target = target
        self._bs = bs
        self._be = be
        self.update()

    def get_ranges(self):
        return self._ranges

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        stack = self._stack; bs = self._bs; be = self._be; target = self._target
        self._ranges = []
        if not stack:
            p.setPen(QColor(C["fg_dim"]))
            p.drawText(W//2-10, H//2, "—")
            return
        margin = 18; avail = W - 2*margin
        vis_total = sum(max(it.get("optical_length",0),2) for it in stack)
        ref = max(target * 1.10, vis_total * 1.05) if target > 0 else vis_total
        bh = 42; yt = (H-bh)/2; x = margin
        src = self._drag_idx; tgt = self._drag_target
        dragging = self._drag_started and src is not None
        insert_x = None
        for si, item in enumerate(stack):
            ol = max(item.get("optical_length",0),2)
            bw = max(ol/ref*avail, 8) if ref > 0 else 12
            is_ghost = item.get("ghost", False)
            col = QColor(C["accent_orange"]) if is_ghost else QColor(TYPE_COLORS.get(item.get("type",""), C["fg_dim"]))
            if dragging and si == src:
                # Dimmed placeholder at original position
                p.setPen(QPen(QColor(C["fg_dim"]), 1, Qt.PenStyle.DashLine))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRect(int(x), int(yt), int(bw), int(bh))
                if tgt is not None and tgt < src:
                    insert_x = x
            else:
                if 0 <= bs <= be and bs < si <= be:
                    p.fillRect(int(x-1), int(yt-5), int(bw+2), int(bh+10), QColor(C["bf_zone"]))
                if is_ghost:
                    p.setPen(QPen(QColor(C["accent_orange"]), 1, Qt.PenStyle.DashLine))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRect(int(x), int(yt), int(bw), int(bh))
                    p.setPen(QColor(C["accent_orange"]))
                    p.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
                    p.drawText(int(x), int(yt), int(bw), int(bh), Qt.AlignmentFlag.AlignCenter, "?")
                else:
                    p.fillRect(int(x+1), int(yt+1), int(bw-2), int(bh-2), col)
                    p.setPen(QColor(C["border"]))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRect(int(x), int(yt), int(bw), int(bh))
                    if bw > 24:
                        p.setPen(QColor(C["bg_dark"]))
                        p.setFont(QFont(FONT_FAMILY, 7))
                        p.drawText(int(x+2), int(yt+2), int(bw-4), int(bh-4),
                                   Qt.AlignmentFlag.AlignCenter, item.get("name","")[:16])
                p.setPen(QColor(C["fg_dim"]))
                p.setFont(QFont(FONT_FAMILY, 7))
                p.drawText(int(x), int(yt+bh+2), int(bw), 14,
                           Qt.AlignmentFlag.AlignCenter, f'{item.get("optical_length",0):.1f}')
                if dragging and si == tgt and tgt is not None and tgt >= src:
                    insert_x = x + bw
            self._ranges.append((x, x+bw, si))
            x += bw
        # Insertion marker
        if dragging and insert_x is not None and src != tgt:
            p.setPen(QPen(QColor(C["accent_green"]), 3))
            ix = int(insert_x)
            p.drawLine(ix, int(yt-8), ix, int(yt+bh+8))
        # Floating piece during drag
        if dragging and src is not None and src < len(stack):
            item = stack[src]
            ol = max(item.get("optical_length",0),2)
            fw = max(ol/ref*avail, 8) if ref > 0 else 12
            fx = self._mouse_x - fw/2
            fy = yt - 4
            dcol = QColor(C["accent_orange"]) if item.get("ghost") else QColor(TYPE_COLORS.get(item.get("type",""), C["fg_dim"]))
            p.fillRect(int(fx), int(fy), int(fw), int(bh), dcol)
            p.setPen(QColor(C["accent_green"]))
            p.drawRect(int(fx), int(fy), int(fw), int(bh))
        # Labels
        p.setPen(QColor(C["fg_dim"])); p.setFont(QFont(FONT_FAMILY, 7))
        p.drawText(margin, int(yt-14), "Telescope")
        p.drawText(W-margin-50, int(yt-14), "Camera")
        # BF annotation
        if 0 <= bs <= be and len(self._ranges) > max(bs, be):
            bx1 = self._ranges[bs][1]; bx2 = self._ranges[be][0]
            mid = (bx1 + bx2) / 2
            p.setPen(QColor(C["accent_green"])); p.setFont(QFont(FONT_FAMILY, 8, QFont.Weight.Bold))
            p.drawText(int(mid-10), int(yt-14), "BF")
            p.setPen(QPen(QColor(C["accent_green"]), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(bx1), int(yt-8), int(bx2), int(yt-8))
        # Target line
        if target > 0 and ref > 0:
            tx = margin + (target/ref)*avail
            if margin < tx < W-margin:
                p.setPen(QPen(QColor(C["accent_red"]), 2, Qt.PenStyle.DashLine))
                p.drawLine(int(tx), int(yt-6), int(tx), int(yt+bh+6))

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._drag_idx = None; self._drag_target = None; self._drag_started = False
        mx = event.position().x()
        for x0, x1, si in self._ranges:
            if x0 <= mx <= x1:
                self._drag_idx = si; self._drag_x0 = mx; break

    def mouseMoveEvent(self, event):
        if self._drag_idx is None:
            return
        mx = event.position().x()
        if not self._drag_started:
            if abs(mx - self._drag_x0) < 5:
                return
            self._drag_started = True
        self._mouse_x = mx
        target = self._drag_idx
        for x0, x1, si in self._ranges:
            if x0 <= mx <= x1:
                target = si; break
        self._drag_target = target
        self.update()

    def mouseReleaseEvent(self, event):
        if self._drag_idx is not None and self._drag_started:
            if self._drag_target is not None and self._drag_target != self._drag_idx:
                self.itemMoved.emit(self._drag_idx, self._drag_target)
        self._drag_idx = None; self._drag_target = None; self._drag_started = False
        self.update()

# ═══════════════════════════════════════════════════════════════════
#  TREE ITEM STYLING HELPER
# ═══════════════════════════════════════════════════════════════════
def _style_tree_item(item, tags, ncols):
    bg = QColor(C["tree_odd"]) if "odd" in tags else QColor(C["tree_even"])
    fg = QColor(C["fg_main"])
    if "bf_zone" in tags:
        bg = QColor(C["bf_zone"])
    if "ghost" in tags:
        fg = QColor(C["accent_orange"]); bg = QColor("#342C22")
    if "owned" in tags:
        fg = QColor(C["accent_gold"])
    elif "notowned" in tags:
        fg = QColor(C["notowned_fg"])
    if "bf_start" in tags:
        fg = QColor(C["accent_green"])
    elif "bf_end" in tags:
        fg = QColor(C["accent_pink"])
    if "mismatch" in tags:
        fg = QColor(C["accent_red"])
    for col in range(ncols):
        item.setBackground(col, QBrush(bg))
        item.setForeground(col, QBrush(fg))

# ═══════════════════════════════════════════════════════════════════
#  DRAGGABLE TREE (for catalog drag-to-main-window)
# ═══════════════════════════════════════════════════════════════════
class _DraggableTree(QTreeWidget):
    """QTreeWidget that initiates drag with part index as mime text."""
    def startDrag(self, supportedActions):
        items = self.selectedItems()
        if not items:
            return
        idx = items[0].data(0, Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(idx))
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)

# ═══════════════════════════════════════════════════════════════════
#  PARTS CATALOG WINDOW
# ═══════════════════════════════════════════════════════════════════
class CatalogWindow(QDialog):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.setWindowTitle(app.t("catalog_title"))
        self.resize(1450, 860)
        self._sort_col = None
        self._sort_rev = False
        self._drag_data = None
        self._search_timer = QTimer(); self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(150); self._search_timer.timeout.connect(self._refresh)
        self._build()
        self._refresh()
        self.show()

    def _build(self):
        a = self.app
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        # Filter toolbar
        tb = QHBoxLayout()
        # Search
        sf = QVBoxLayout()
        sf.addWidget(QLabel(a.t("search")))
        self._search_edit = QLineEdit()
        self._search_edit.setFixedWidth(160)
        self._search_edit.textChanged.connect(lambda: self._search_timer.start())
        sf.addWidget(self._search_edit)
        tb.addLayout(sf)
        # Brand
        bf = QVBoxLayout()
        bf.addWidget(QLabel(a.t("filter_brand")))
        brands = sorted(_REF_BRANDS | {p.get("brand","") for p in a.data["parts"] if p.get("brand","")})
        self._fb = QComboBox(); self._fb.addItems([a.t("filter_all")] + brands)
        self._fb.setFixedWidth(140); self._fb.currentIndexChanged.connect(lambda: self._refresh())
        bf.addWidget(self._fb); tb.addLayout(bf)
        # Type
        tf = QVBoxLayout()
        tf.addWidget(QLabel(a.t("filter_type")))
        self._ft = QComboBox()
        self._ft.addItems([a.t("filter_all")] + sorted([a._ttype(k) for k in PART_TYPES]))
        self._ft.setFixedWidth(140); self._ft.currentIndexChanged.connect(lambda: self._refresh())
        tf.addWidget(self._ft); tb.addLayout(tf)
        # Thread
        thf = QVBoxLayout()
        thf.addWidget(QLabel(a.t("filter_thread")))
        threads = [t for t in THREADS if t]
        self._fth = QComboBox(); self._fth.addItems([a.t("filter_all")] + threads)
        self._fth.setFixedWidth(160); self._fth.currentIndexChanged.connect(lambda: self._refresh())
        thf.addWidget(self._fth); tb.addLayout(thf)
        # Diameter
        df = QVBoxLayout()
        df.addWidget(QLabel(a.t("filter_diameter")))
        self._fd = QComboBox(); self._fd.addItems(DIAMETERS)
        self._fd.setFixedWidth(80); self._fd.currentIndexChanged.connect(lambda: self._search_timer.start())
        df.addWidget(self._fd); tb.addLayout(df)
        # Gender
        gf = QVBoxLayout()
        gf.addWidget(QLabel(a.t("filter_gender")))
        self._fg = QComboBox()
        self._fg.addItems([a.t("gender_all"), a.t("gender_male"), a.t("gender_female")])
        self._fg.setFixedWidth(90); self._fg.currentIndexChanged.connect(lambda: self._refresh())
        gf.addWidget(self._fg); tb.addLayout(gf)
        # Optical length range
        olf = QVBoxLayout()
        olf.addWidget(QLabel(a.t("optical_length")))
        olr = QHBoxLayout()
        self._fol_min = QLineEdit(); self._fol_min.setFixedWidth(50)
        self._fol_min.textChanged.connect(lambda: self._search_timer.start())
        self._fol_max = QLineEdit(); self._fol_max.setFixedWidth(50)
        self._fol_max.textChanged.connect(lambda: self._search_timer.start())
        olr.addWidget(self._fol_min); olr.addWidget(QLabel("-")); olr.addWidget(self._fol_max)
        olf.addLayout(olr); tb.addLayout(olf)
        # Owned + reset
        of = QVBoxLayout()
        self._fo = QCheckBox(a.t("filter_owned"))
        self._fo.stateChanged.connect(lambda: self._refresh())
        of.addWidget(self._fo)
        reset_btn = QPushButton(a.t("reset_filters")); reset_btn.setProperty("small", True)
        reset_btn.clicked.connect(self._reset); of.addWidget(reset_btn)
        tb.addLayout(of); tb.addStretch()
        main_layout.addLayout(tb)
        # Action toolbar
        tb2 = QHBoxLayout()
        btns = [
            ("add_part", self._add, True, "Add a new part", "Ajouter une nouvelle pièce"),
            ("edit_part", self._edit, False, "Edit selected part", "Modifier la pièce sélectionnée"),
            ("duplicate_part", self._dup, False, "Duplicate selected part", "Dupliquer la pièce sélectionnée"),
            ("delete_part", self._del, False, "Delete selected part", "Supprimer la pièce sélectionnée"),
        ]
        for key, cmd, accent, tip_en, tip_fr in btns:
            b = QPushButton(a.t(key)); b.setProperty("accent", accent)
            b.clicked.connect(cmd)
            b.setToolTip(tip_fr if a.lang == "fr" else tip_en)
            tb2.addWidget(b)
        # Separator + qty
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.VLine); sep.setStyleSheet(f"color: {C['separator']};")
        tb2.addWidget(sep)
        tb2.addWidget(QLabel(a.t("qty") + ":"))
        b_minus = QPushButton("−"); b_minus.setProperty("small", True); b_minus.setFixedWidth(30)
        b_minus.clicked.connect(self._qty_minus)
        b_minus.setToolTip("Diminuer la quantité" if a.lang == "fr" else "Decrease quantity")
        tb2.addWidget(b_minus)
        b_plus = QPushButton("+"); b_plus.setProperty("small", True); b_plus.setFixedWidth(30)
        b_plus.clicked.connect(self._qty_plus)
        b_plus.setToolTip("Augmenter la quantité" if a.lang == "fr" else "Increase quantity")
        tb2.addWidget(b_plus)
        tb2.addStretch()
        main_layout.addLayout(tb2)
        # Treeview
        cols = ["brand","name","type","mm","mass","t_thread","t_g","c_thread","c_g","rev","bf","qty","notes"]
        hdrs = [a.t("part_brand"), a.t("part_name"), a.t("part_type"), "mm", "g",
                a.t("tside"), "", a.t("cside"), "", a.t("reversible"), a.t("bf_role"), a.t("qty"), a.t("part_notes")]
        widths = [90, 220, 115, 58, 50, 100, 55, 100, 55, 55, 60, 42, 140]
        self.tree = _DraggableTree()
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnCount(len(cols))
        self.tree.setHeaderLabels(hdrs)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setRootIsDecorated(False)
        for i, w in enumerate(widths):
            self.tree.setColumnWidth(i, w)
        self.tree.header().sectionClicked.connect(self._sort)
        self.tree.itemDoubleClicked.connect(lambda: self._edit())
        self.tree.setDragEnabled(True)
        main_layout.addWidget(self.tree)
        # Status bar
        sf2 = QHBoxLayout()
        self._status = QLabel("")
        sf2.addWidget(self._status)
        sf2.addStretch()
        self._drag_hint = QLabel(self.app.t("drag_hint"))
        self._drag_hint.setStyleSheet(f"color: {C['fg_dim']}; font-size: 8pt;")
        sf2.addWidget(self._drag_hint)
        main_layout.addLayout(sf2)

    def _reset(self):
        self._search_edit.clear(); self._fb.setCurrentIndex(0); self._ft.setCurrentIndex(0)
        self._fth.setCurrentIndex(0); self._fd.setCurrentIndex(0); self._fg.setCurrentIndex(0)
        self._fol_min.clear(); self._fol_max.clear(); self._fo.setChecked(False)
        self._refresh()

    _MAX_DISPLAY = 500

    def _refresh(self):
        self.tree.clear()
        lu = self.app.data.get("length_unit", "mm")
        mu = self.app.data.get("mass_unit", "g")
        s = self._search_edit.text().lower()
        all_ = self.app.t("filter_all")
        fb = self._fb.currentText(); fb_active = fb != all_
        ft = self._ft.currentText(); ft_active = ft != all_
        fth = self._fth.currentText(); fth_active = fth != all_
        fd = self._fd.currentText(); fd_active = fd != "All"
        fg = self._fg.currentText()
        fg_active = fg != self.app.t("gender_all")
        fg_gen = ("Male" if fg == self.app.t("gender_male") else "Female") if fg_active else ""
        owned_only = self._fo.isChecked()
        try: fol_min = float(self._fol_min.text().replace(",", "."))
        except ValueError: fol_min = None
        try: fol_max = float(self._fol_max.text().replace(",", "."))
        except ValueError: fol_max = None
        _ttype = self.app._ttype
        items = []
        for i, p in enumerate(self.app.data["parts"]):
            if owned_only and p.get("qty",0) <= 0: continue
            if s and s not in p.get("name","").lower() and s not in p.get("brand","").lower(): continue
            if fb_active and p.get("brand","") != fb: continue
            if ft_active and _ttype(p.get("type","")) != ft: continue
            if fth_active and fth not in (p.get("tside_thread",""), p.get("cside_thread","")): continue
            if fd_active and fd not in (_extract_diam(p.get("tside_thread","")),
                                        _extract_diam(p.get("cside_thread",""))): continue
            if fg_active and fg_gen not in (p.get("tside_gender",""), p.get("cside_gender","")): continue
            ol = p.get("optical_length", 0)
            if fol_min is not None and ol < fol_min: continue
            if fol_max is not None and ol > fol_max: continue
            items.append((i, p))
        total_matched = len(items)
        key_map = {"brand": lambda ip: ip[1].get("brand","").lower(),
                   "name": lambda ip: ip[1].get("name","").lower(),
                   "type": lambda ip: ip[1].get("type",""),
                   "mm": lambda ip: ip[1].get("optical_length",0),
                   "mass": lambda ip: ip[1].get("mass",0),
                   "qty": lambda ip: ip[1].get("qty",0)}
        if self._sort_col is not None and self._sort_col < len(["brand","name","type","mm","mass","","","","","","","qty"]):
            col_names = ["brand","name","type","mm","mass","","","","","","","qty"]
            cn = col_names[self._sort_col] if self._sort_col < len(col_names) else ""
            fn = key_map.get(cn)
            if fn:
                items.sort(key=fn, reverse=self._sort_rev)
        else:
            items.sort(key=lambda ip: (ip[1].get("brand","").lower(), ip[1].get("name","").lower()))
        display = items[:self._MAX_DISPLAY]
        self.tree.setUpdatesEnabled(False)
        for row, (i, p) in enumerate(display):
            ol = p.get("optical_length",0); ms = p.get("mass",0)
            vals = [p.get("brand",""), p.get("name",""), _ttype(p.get("type","")),
                    _fmt_len(ol,lu) if ol else "", _fmt_mass(ms,mu) if ms else "",
                    p.get("tside_thread",""), p.get("tside_gender",""),
                    p.get("cside_thread",""), p.get("cside_gender",""),
                    "Y" if p.get("reversible") else "", p.get("bf_role",""),
                    str(p.get("qty",0)), p.get("notes","")[:40]]
            item = QTreeWidgetItem(vals)
            item.setData(0, Qt.ItemDataRole.UserRole, i)
            tags = ["odd" if row%2==0 else "even",
                    "owned" if p.get("qty",0) > 0 else "notowned"]
            _style_tree_item(item, tags, len(vals))
            self.tree.addTopLevelItem(item)
        self.tree.setUpdatesEnabled(True)
        if total_matched > self._MAX_DISPLAY:
            self._status.setText(f"{self._MAX_DISPLAY} / {total_matched} " + self.app.t("total_parts", n=total_matched))
        else:
            self._status.setText(self.app.t("total_parts", n=len(display)))

    def _sort(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col; self._sort_rev = False
        self._refresh()

    def _sel_idx(self):
        items = self.tree.selectedItems()
        if not items:
            return None
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def _add(self):
        self.app._part_dlg(None, on_done=self._refresh)

    def _edit(self):
        i = self._sel_idx()
        if i is not None and i < len(self.app.data["parts"]):
            self.app._part_dlg(i, on_done=self._refresh)

    def _dup(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        np = copy.deepcopy(self.app.data["parts"][i])
        np["name"] += " (copy)"
        self.app.data["parts"].append(np)
        self.app._save(); self._refresh()

    def _del(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        nm = self.app.data["parts"][i].get("name","")
        if QMessageBox.question(self, self.app.t("confirm_delete"),
                                self.app.t("confirm_delete_msg", name=nm)) == QMessageBox.StandardButton.Yes:
            self.app.data["parts"].pop(i)
            self.app._save(); self._refresh()

    def _qty_plus(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        self.app.data["parts"][i]["qty"] = self.app.data["parts"][i].get("qty",0) + 1
        self.app._save(); self._refresh()

    def _qty_minus(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        q = self.app.data["parts"][i].get("qty",0) - 1
        self.app.data["parts"][i]["qty"] = max(0, q)
        self.app._save(); self._refresh()


# ═══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = load_data()
        self.lang = self.data.get("language", "fr")
        if not self.data["parts"]:
            self.data["parts"] = [dict(p, qty=0) for p in REFERENCE_DB]
            save_data(self.data)
        elif REFERENCE_DB:
            added, purged = _merge_reference_db(self.data)
            if added or purged:
                save_data(self.data)
        self._catalog_win = None
        self._fits_win = None
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(300)
        self._save_timer.timeout.connect(self._flush_save)
        self._parts_search_cache = None
        self._tooltips = []
        self._update_thread = None
        self._update_queue = queue.Queue()
        self._update_dl_queue = queue.Queue()
        self.setAcceptDrops(True)
        self._build_ui()
        self._apply_language()
        self.galaxy = GalaxyCursor(self)
        QTimer.singleShot(2000, self._check_updates_startup)
        QTimer.singleShot(3000, self._check_crash_on_startup)

    # ── debounced save ──
    def _save(self):
        self._save_timer.start()

    def _flush_save(self):
        self._parts_search_cache = None
        save_data(self.data)

    def _get_parts_search_cache(self):
        if self._parts_search_cache is None:
            self._parts_search_cache = [
                (j, (p.get("brand","") + " " + p.get("name","")).lower(), p)
                for j, p in enumerate(self.data["parts"])
            ]
        return self._parts_search_cache

    def _invalidate_parts_cache(self):
        self._parts_search_cache = None

    def t(self, key, **kw):
        e = TR.get(key, {}); s = e.get(self.lang, e.get("en", key))
        return s.format(**kw) if kw else s

    def _ttype(self, k):
        return self.t(k) if k in TR else k

    def _tip(self, w, en, fr=None):
        if fr is None: fr = en
        self._tooltips.append((w, en, fr))
        w.setToolTip(fr if self.lang == "fr" else en)

    # ── UI skeleton ──
    def _build_ui(self):
        self.setWindowTitle(self.t("app_title"))
        ui = self.data.get("ui", {})
        geo = ui.get("window_geometry", "1400x1100")
        try:
            parts = geo.replace("+", "x").split("x")
            w, h = int(parts[0]), int(parts[1])
            h = max(h, 1100)
            self.resize(w, h)
            if len(parts) >= 4:
                self.move(int(parts[2]), int(parts[3]))
        except (ValueError, IndexError):
            self.resize(1400, 1100)
        self.setMinimumSize(1050, 1100)

        central = QWidget()
        self.setCentralWidget(central)
        ml = QVBoxLayout(central)
        ml.setContentsMargins(6, 4, 6, 2)
        ml.setSpacing(6)

        # Menu bar (rebuilt in _apply_language)
        self.menu = self.menuBar()

        # Main toolbar
        tb = QHBoxLayout()
        self.btn_open_cat = QPushButton(self.t("open_catalog"))
        self.btn_open_cat.setProperty("accent", True)
        self.btn_open_cat.clicked.connect(self._open_catalog)
        self._tip(self.btn_open_cat, "Open the parts catalog in a large separate window",
                  "Ouvrir le catalogue de pièces dans une grande fenêtre séparée")
        tb.addWidget(self.btn_open_cat)

        self.btn_new_part = QPushButton(self.t("new_part"))
        self.btn_new_part.clicked.connect(self._new_part)
        self._tip(self.btn_new_part, "Create a new custom part",
                  "Créer une nouvelle pièce personnalisée")
        tb.addWidget(self.btn_new_part)
        tb.addStretch()

        self.btn_fits = QPushButton(self.t("fits_btn"))
        self.btn_fits.setProperty("fits", True)
        self.btn_fits.clicked.connect(self._open_fits_analyzer)
        self._tip(self.btn_fits, "Analyze a FITS/XISF image to diagnose backfocus errors",
                  "Analyser une image FITS/XISF pour diagnostiquer les erreurs de backfocus")
        tb.addWidget(self.btn_fits)
        ml.addLayout(tb)

        # Config panel
        self._build_config_panel(ml)

        # Coffee link
        coffee = QLabel("☕")
        coffee.setStyleSheet(f"color: {C['fg_dim']}; font-size: 7pt;")
        coffee.setCursor(Qt.CursorShape.PointingHandCursor)
        coffee.mousePressEvent = lambda _: __import__('webbrowser').open(
            "https://buymeacoffee.com/orlytourbou")
        ml.addWidget(coffee, alignment=Qt.AlignmentFlag.AlignRight)

        QTimer.singleShot(0, self._refresh_cfgs)

    def _build_config_panel(self, parent_layout):
        self.splitter_h = QSplitter(Qt.Orientation.Horizontal)
        parent_layout.addWidget(self.splitter_h, 1)

        # ── left: config list ──
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)
        lbl = QLabel("Configurations")
        lbl.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {C['accent_purple']};")
        ll.addWidget(lbl)

        bb = QHBoxLayout()
        self.btn_c_add = QPushButton("+")
        self.btn_c_add.setProperty("accent", True); self.btn_c_add.setFixedWidth(30)
        self.btn_c_add.clicked.connect(self._add_config)
        self._tip(self.btn_c_add, "Create a new configuration", "Créer une nouvelle configuration")
        bb.addWidget(self.btn_c_add)
        self.btn_c_edit = QPushButton(self.t("edit_config"))
        self.btn_c_edit.clicked.connect(self._edit_config)
        self._tip(self.btn_c_edit, "Edit configuration", "Modifier la configuration")
        bb.addWidget(self.btn_c_edit)
        self.btn_c_dup = QPushButton("Dup")
        self.btn_c_dup.clicked.connect(self._dup_config)
        self._tip(self.btn_c_dup, "Duplicate configuration", "Dupliquer la configuration")
        bb.addWidget(self.btn_c_dup)
        self.btn_c_del = QPushButton("Del")
        self.btn_c_del.clicked.connect(self._del_config)
        self._tip(self.btn_c_del, "Delete selected configuration",
                  "Supprimer la configuration sélectionnée")
        bb.addWidget(self.btn_c_del)
        bb.addStretch()
        ll.addLayout(bb)

        self.clist = QListWidget()
        self.clist.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.clist.setStyleSheet(
            f"QListWidget {{ background: {C['bg_light']}; color: {C['fg_main']}; "
            f"border: none; font-size: 10pt; }}"
            f"QListWidget::item:selected {{ background: {C['bg_selected']}; "
            f"color: {C['fg_bright']}; }}")
        self.clist.currentRowChanged.connect(self._on_cfg_select)
        self.clist.model().rowsMoved.connect(self._on_cfg_moved)
        ll.addWidget(self.clist)
        self.splitter_h.addWidget(left)
        self.splitter_h.setStretchFactor(0, 0)

        # ── right: editor ──
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(4, 0, 4, 4)

        top = QHBoxLayout()
        self.lbl_target = QLabel(self.t("target_bf"))
        top.addWidget(self.lbl_target)
        self.e_target = QLineEdit("0")
        self.e_target.setFixedWidth(70)
        self.e_target.textChanged.connect(self._calc)
        self._tip(self.e_target, "Target backfocus distance", "Distance de backfocus cible")
        top.addWidget(self.e_target)
        top.addSpacing(14)
        self.lbl_notes = QLabel(self.t("notes"))
        top.addWidget(self.lbl_notes)
        self.e_notes = QLineEdit()
        self.e_notes.textChanged.connect(self._save_cfg)
        top.addWidget(self.e_notes, 1)
        rl.addLayout(top)

        self.splitter_v = QSplitter(Qt.Orientation.Vertical)

        # ── mid: treeview + buttons ──
        mid = QWidget()
        mid_l = QHBoxLayout(mid)
        mid_l.setContentsMargins(0, 0, 0, 0)

        tree_group = QGroupBox(self.t("train_label"))
        tree_gl = QVBoxLayout(tree_group)
        cols = ["#", self.t("part_brand"), self.t("part_name"), self.t("part_type"),
                "mm", self.t("tside"), self.t("cside"), self.t("flip_piece"), "BF", ""]
        self.stree = QTreeWidget()
        self.stree.setHeaderLabels(cols)
        self.stree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.stree.setRootIsDecorated(False)
        self.stree.setAlternatingRowColors(False)
        widths = [30, 75, 170, 95, 48, 110, 110, 42, 58, 85]
        for i, w in enumerate(widths):
            self.stree.setColumnWidth(i, w)
        self.stree.itemDoubleClicked.connect(lambda: self._stack_edit())
        tree_gl.addWidget(self.stree)
        mid_l.addWidget(tree_group, 1)

        # Buttons panel
        bfr = QVBoxLayout()
        btn_spec = [
            ("add_to_stack", self._stack_add, True,
             "Add a part from your catalog to the train",
             "Ajouter une pièce du catalogue au train"),
            ("remove_from_stack", self._stack_rm, False,
             "Remove selected part from train", "Retirer la pièce du train"),
            None,
            ("move_up", self._stack_up, False,
             "Move part up (towards telescope)",
             "Déplacer vers le haut (vers le télescope)"),
            ("move_down", self._stack_dn, False,
             "Move part down (towards camera)",
             "Déplacer vers le bas (vers la caméra)"),
            ("flip_piece", self._stack_flip, False,
             "Flip a reversible part (swap sides)",
             "Retourner une pièce réversible"),
            None,
            ("mark_bf_start", self._mark_bf_start, False,
             "BF measured from camera-side output of this part",
             "BF mesuré depuis la sortie côté caméra de cette pièce"),
            ("mark_bf_end", self._mark_bf_end, False,
             "BF measured to telescope-side input of this part (sensor)",
             "BF mesuré jusqu'à l'entrée côté télescope de cette pièce (capteur)"),
            None,
            ("auto_suggest", self._suggest, True,
             "Find a single part that fills the gap",
             "Trouver une pièce qui comble l'écart"),
            ("auto_complete", self._auto_complete, True,
             "Find combinations of owned parts",
             "Trouver des combinaisons de pièces possédées"),
            None,
            ("insert_ghost", self._stack_add_ghost, False,
             "Insert a ghost placeholder at current position",
             "Insérer un fantôme à la position courante"),
            ("resolve_ghosts", self._resolve_ghosts, False,
             "Find real parts to replace ghost placeholders",
             "Trouver des pièces réelles pour remplacer les fantômes"),
        ]
        for spec in btn_spec:
            if spec is None:
                sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet(f"color: {C['separator']};")
                bfr.addWidget(sep)
            else:
                key, cmd, accent, tip_en, tip_fr = spec
                b = QPushButton(self.t(key))
                if accent: b.setProperty("accent", True)
                b.clicked.connect(cmd)
                setattr(self, f"btn_{key}", b)
                self._tip(b, tip_en, tip_fr)
                bfr.addWidget(b)
        bfr.addStretch()
        mid_l.addLayout(bfr)
        self.splitter_v.addWidget(mid)

        # ── bottom: BF info + diagram ──
        bot = QWidget()
        bot_l = QHBoxLayout(bot)
        bot_l.setContentsMargins(0, 0, 0, 0)

        bf_group = QGroupBox("Backfocus")
        bf_gl = QVBoxLayout(bf_group)
        self.lbl_total = QLabel("")
        self.lbl_bf = QLabel("")
        self.lbl_bf.setStyleSheet(f"font-weight: bold; color: {C['fg_bright']};")
        self.lbl_diff = QLabel("")
        self.lbl_diff.setStyleSheet("font-size: 11pt; font-weight: bold;")
        bf_gl.addWidget(self.lbl_total)
        bf_gl.addWidget(self.lbl_bf)
        bf_gl.addWidget(self.lbl_diff)
        bot_l.addWidget(bf_group)

        self.lbl_diagram = QGroupBox(self.t("diagram"))
        diag_gl = QVBoxLayout(self.lbl_diagram)
        self.diagram = DiagramWidget()
        self.diagram.setMinimumHeight(120)
        self.diagram.itemMoved.connect(self._move_stack_item)
        diag_gl.addWidget(self.diagram)
        bot_l.addWidget(self.lbl_diagram, 1)

        self.splitter_v.addWidget(bot)
        self.splitter_v.setStretchFactor(0, 1)
        self.splitter_v.setStretchFactor(1, 0)
        rl.addWidget(self.splitter_v)

        self.splitter_h.addWidget(right)
        self.splitter_h.setStretchFactor(1, 1)
        QTimer.singleShot(100, self._restore_splitter_positions)

    # ── catalog / FITS ──
    def _open_catalog(self):
        if self._catalog_win and self._catalog_win.isVisible():
            self._catalog_win.raise_()
        else:
            self._catalog_win = CatalogWindow(self)
            self._catalog_win.show()

    def _open_fits_analyzer(self):
        if not _HAS_FITS_ANALYZER:
            QMessageBox.information(self, self.t("fits_analyzer"),
                                    self.t("fits_analyzer_missing_deps"))
            return
        if self._fits_win and self._fits_win.isVisible():
            self._fits_win.raise_()
        else:
            self._fits_win = FITSAnalyzerWindow(self)

    def _new_part(self):
        self._open_catalog()
        self._catalog_win._add()

    # ── config CRUD ──
    def _refresh_cfgs(self):
        self.clist.blockSignals(True)
        self.clist.clear()
        for c in self.data["configurations"]:
            self.clist.addItem(c["name"])
        self.clist.blockSignals(False)
        if self.data["configurations"]:
            self.clist.setCurrentRow(0)
            self._on_cfg_select(0)

    def _cfg_idx(self):
        r = self.clist.currentRow()
        return r if r >= 0 else None

    def _on_cfg_select(self, row=None):
        i = self._cfg_idx()
        if i is None: return
        c = self.data["configurations"][i]
        self.e_target.blockSignals(True)
        self.e_target.setText(str(c.get("target_backfocus", 0)))
        self.e_target.blockSignals(False)
        self.e_notes.blockSignals(True)
        self.e_notes.setText(c.get("notes", ""))
        self.e_notes.blockSignals(False)
        self._refresh_stack()

    def _on_cfg_moved(self, *args):
        # Sync data model with QListWidget order after drag reorder
        new_order = []
        for i in range(self.clist.count()):
            name = self.clist.item(i).text()
            for cfg in self.data["configurations"]:
                if cfg["name"] == name and cfg not in new_order:
                    new_order.append(cfg); break
        if len(new_order) == len(self.data["configurations"]):
            self.data["configurations"] = new_order
            self._save()

    def _add_config(self):
        dlg = QDialog(self); dlg.setWindowTitle(self.t("add_config"))
        dlg.resize(400, 180)
        gl = QGridLayout(dlg)
        gl.addWidget(QLabel(self.t("config_name")), 0, 0)
        ne = QLineEdit(); gl.addWidget(ne, 0, 1)
        gl.addWidget(QLabel(self.t("target_bf")), 1, 0)
        te = QLineEdit("55"); gl.addWidget(te, 1, 1)
        bf = QHBoxLayout()
        ok_btn = QPushButton(self.t("ok")); ok_btn.setProperty("accent", True)
        cancel_btn = QPushButton(self.t("cancel"))
        bf.addWidget(ok_btn); bf.addWidget(cancel_btn)
        gl.addLayout(bf, 2, 0, 1, 2)
        def ok():
            n = ne.text().strip()
            if not n: return
            try: t = float(te.text().replace(",", "."))
            except ValueError: t = 55
            self.data["configurations"].append(
                {"name": n, "target_backfocus": t, "notes": "",
                 "bf_start_idx": -1, "bf_end_idx": -1, "stack": []})
            self._save(); self._refresh_cfgs()
            self.clist.setCurrentRow(len(self.data["configurations"]) - 1)
            self._on_cfg_select(); dlg.accept()
        ok_btn.clicked.connect(ok); cancel_btn.clicked.connect(dlg.reject)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    def _del_config(self):
        i = self._cfg_idx()
        if i is None: return
        nm = self.data["configurations"][i]["name"]
        if QMessageBox.question(self, self.t("confirm_delete"),
                self.t("confirm_delete_msg", name=nm)) == QMessageBox.StandardButton.Yes:
            self.data["configurations"].pop(i)
            self._save(); self._refresh_cfgs()

    def _dup_config(self):
        i = self._cfg_idx()
        if i is None: return
        nc = copy.deepcopy(self.data["configurations"][i])
        nc["name"] += " (copy)"
        self.data["configurations"].append(nc)
        self._save(); self._refresh_cfgs()

    def _edit_config(self):
        i = self._cfg_idx()
        if i is None: return
        cfg = self.data["configurations"][i]
        dlg = QDialog(self); dlg.setWindowTitle(self.t("edit_config"))
        dlg.resize(400, 220)
        gl = QGridLayout(dlg)
        gl.addWidget(QLabel(self.t("config_name")), 0, 0)
        ne = QLineEdit(cfg["name"]); gl.addWidget(ne, 0, 1)
        gl.addWidget(QLabel(self.t("target_bf")), 1, 0)
        te = QLineEdit(str(cfg.get("target_backfocus", 0))); gl.addWidget(te, 1, 1)
        gl.addWidget(QLabel(self.t("notes")), 2, 0)
        note_e = QLineEdit(cfg.get("notes", "")); gl.addWidget(note_e, 2, 1)
        bf = QHBoxLayout()
        ok_btn = QPushButton(self.t("ok")); ok_btn.setProperty("accent", True)
        cancel_btn = QPushButton(self.t("cancel"))
        bf.addWidget(ok_btn); bf.addWidget(cancel_btn)
        gl.addLayout(bf, 3, 0, 1, 2)
        def ok():
            n = ne.text().strip()
            if not n: return
            cfg["name"] = n
            try: cfg["target_backfocus"] = float(te.text().replace(",", "."))
            except ValueError: pass
            cfg["notes"] = note_e.text()
            self._save(); self._refresh_cfgs()
            self.clist.setCurrentRow(i); self._on_cfg_select()
            dlg.accept()
        ok_btn.clicked.connect(ok); cancel_btn.clicked.connect(dlg.reject)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    def _save_cfg(self):
        i = self._cfg_idx()
        if i is None: return
        c = self.data["configurations"][i]
        try: c["target_backfocus"] = float(self.e_target.text().replace(",", "."))
        except ValueError: pass
        c["notes"] = self.e_notes.text()
        self._save()

    # ── stack ──
    def _stree_sel_idx(self):
        items = self.stree.selectedItems()
        if not items: return None
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def _refresh_stack(self):
        i = self._cfg_idx()
        self.stree.clear()
        if i is None: return
        cfg = self.data["configurations"][i]
        stack = cfg.get("stack", [])
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        changed = False
        if bs < 0 or bs >= len(stack):
            for si, item in enumerate(stack):
                if item.get("bf_role") == "start":
                    bs = si; cfg["bf_start_idx"] = si; changed = True; break
        if be < 0 or be >= len(stack):
            for si, item in enumerate(stack):
                if item.get("bf_role") == "end":
                    be = si; cfg["bf_end_idx"] = si; changed = True; break
        if changed:
            self._save()
        lu = self.data.get("length_unit", "mm")
        self.stree.setUpdatesEnabled(False)
        for si, item in enumerate(stack):
            eff = _effective(item)
            compat = ""
            if si > 0:
                prev = _effective(stack[si - 1])
                if prev.get("cside_thread") and eff.get("tside_thread"):
                    ok = _conn_compat(prev.get("cside_thread", ""), prev.get("cside_gender", ""),
                                      eff.get("tside_thread", ""), eff.get("tside_gender", ""))
                    compat = "OK" if ok else "MISMATCH"
            bf_mark = ""
            if si == bs: bf_mark = ">> BF START ↓"
            elif si == be: bf_mark = "↑ BF END <<"
            elif bs >= 0 and be >= 0 and bs < si < be: bf_mark = "…"
            tags = ["odd" if si % 2 == 0 else "even"]
            if item.get("ghost"): tags.append("ghost")
            if 0 <= bs <= be and bs < si <= be: tags.append("bf_zone")
            if si == bs: tags.append("bf_start")
            if si == be: tags.append("bf_end")
            if compat == "MISMATCH": tags.append("mismatch")
            ol = item.get("optical_length", 0)
            vals = [str(si + 1), item.get("brand", ""), item.get("name", ""),
                    self._ttype(item.get("type", "")), _fmt_len(ol, lu),
                    f'{eff.get("tside_thread", "")} {eff.get("tside_gender", "")}'.strip(),
                    f'{eff.get("cside_thread", "")} {eff.get("cside_gender", "")}'.strip(),
                    "FLIP" if item.get("flipped") else "", bf_mark, compat]
            tw_item = QTreeWidgetItem(vals)
            tw_item.setData(0, Qt.ItemDataRole.UserRole, si)
            _style_tree_item(tw_item, tags, len(vals))
            self.stree.addTopLevelItem(tw_item)
        self.stree.setUpdatesEnabled(True)
        self._calc()

    def _stack_add(self):
        ci = self._cfg_idx()
        if ci is None: return
        self._pick_part_dlg(ci)

    def _stack_add_ghost(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]
        stack = cfg.setdefault("stack", [])
        si = self._stree_sel_idx()
        ins_idx = (si + 1) if si is not None else len(stack)
        ghost = self._make_ghost(stack, ins_idx)
        stack.insert(ins_idx, ghost)
        self._save(); self._refresh_stack()

    def _stack_edit(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        cfg = self.data["configurations"][ci]
        stack = cfg.get("stack", [])
        if si >= len(stack): return
        p = stack[si]
        dlg = QDialog(self); dlg.setWindowTitle(self.t("edit_part"))
        _saved = self.data.get("ui", {}).get("part_dlg_geometry", "600x740")
        try:
            pw, ph = (int(v) for v in _saved.split("x")[:2])
            dlg.resize(pw, ph)
        except (ValueError, IndexError):
            dlg.resize(600, 740)
        dlg.setMinimumSize(500, 500)
        gl = QGridLayout(dlg)
        r = 0; vars_ = {}
        def _row(label, key, wf, **kw):
            nonlocal r
            gl.addWidget(QLabel(label), r, 0, Qt.AlignmentFlag.AlignLeft)
            w, var = wf(r, kw); vars_[key] = var; r += 1; return w
        def _entry(row, kw):
            e = QLineEdit(str(kw.get("val", ""))); e.setFixedWidth(kw.get("pw", 200))
            gl.addWidget(e, row, 1, 1, 2); return e, e
        def _combo(row, kw):
            c = QComboBox()
            c.setEditable(not kw.get("ro", False))
            c.addItems([str(v) for v in kw.get("vals", [])])
            val = str(kw.get("val", ""))
            idx = c.findText(val)
            if idx >= 0: c.setCurrentIndex(idx)
            elif not kw.get("ro"): c.setCurrentText(val)
            gl.addWidget(c, row, 1, 1, 2); return c, c
        def _check(row, kw):
            c = QCheckBox(); c.setChecked(kw.get("val", False))
            gl.addWidget(c, row, 1); return c, c
        _all_brands = sorted({"Custom Made"} | _REF_BRANDS |
            {pp.get("brand", "") for pp in self.data["parts"] if pp.get("brand", "")})
        _row(self.t("part_brand"), "brand", _combo, val=p.get("brand", ""), vals=_all_brands)
        _row(self.t("part_name"), "name", _entry, val=p.get("name", ""))
        type_map = {self._ttype(k): k for k in PART_TYPES}
        _row(self.t("part_type"), "type", _combo, val=self._ttype(p.get("type", "")),
             vals=sorted(type_map.keys()), ro=True)
        _row(self.t("optical_length"), "mm", _entry, val=p.get("optical_length", 0), pw=80)
        _row(self.t("mass_label"), "mass", _entry, val=p.get("mass", 0), pw=80)
        _row(self.t("reversible"), "reversible", _check, val=p.get("reversible", False))
        _row(self.t("bf_role"), "bf_role", _combo, val=p.get("bf_role", ""),
             vals=["", "start", "end"], ro=True)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        gl.addWidget(sep, r, 0, 1, 3); r += 1
        sl = QLabel(self.t("tside"))
        sl.setStyleSheet(f"font-weight: bold; color: {C['accent_teal']};")
        gl.addWidget(sl, r, 0, 1, 3); r += 1
        _row(self.t("thread"), "tside_thread", _combo, val=p.get("tside_thread", ""), vals=THREADS)
        _row(self.t("gender"), "tside_gender", _combo, val=p.get("tside_gender", ""),
             vals=GENDERS, ro=True)
        cl = QLabel(self.t("cside"))
        cl.setStyleSheet(f"font-weight: bold; color: {C['accent_teal']};")
        gl.addWidget(cl, r, 0, 1, 3); r += 1
        _row(self.t("thread"), "cside_thread", _combo, val=p.get("cside_thread", ""), vals=THREADS)
        _row(self.t("gender"), "cside_gender", _combo, val=p.get("cside_gender", ""),
             vals=GENDERS, ro=True)
        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        gl.addWidget(sep2, r, 0, 1, 3); r += 1
        # qty
        cat_idx = None
        pn = p.get("name", ""); pb = p.get("brand", "")
        for qi, cp in enumerate(self.data["parts"]):
            if cp.get("name") == pn and cp.get("brand") == pb:
                cat_idx = qi; break
        cat_qty = self.data["parts"][cat_idx].get("qty", 0) if cat_idx is not None else 0
        gl.addWidget(QLabel(self.t("qty")), r, 0)
        qf = QHBoxLayout()
        qty_e = QLineEdit(str(cat_qty)); qty_e.setFixedWidth(40); vars_["qty"] = qty_e
        qm = QPushButton("−"); qm.setFixedWidth(28)
        qm.clicked.connect(lambda: qty_e.setText(str(max(0, _safe_int(qty_e.text()) - 1))))
        qp = QPushButton("+"); qp.setFixedWidth(28)
        qp.clicked.connect(lambda: qty_e.setText(str(_safe_int(qty_e.text()) + 1)))
        qf.addWidget(qm); qf.addWidget(qty_e); qf.addWidget(qp); qf.addStretch()
        gl.addLayout(qf, r, 1, 1, 2); r += 1
        def _do_save():
            try: ol = float(str(vars_["mm"].text()).replace(",", "."))
            except (ValueError, AttributeError): ol = 0
            try: ms = float(str(vars_["mass"].text()).replace(",", "."))
            except (ValueError, AttributeError): ms = 0
            td = type_map.get(vars_["type"].currentText(), p.get("type", "type_adapter"))
            p["brand"] = vars_["brand"].currentText().strip()
            p["name"] = vars_["name"].text().strip()
            p["type"] = td; p["optical_length"] = ol; p["mass"] = ms
            p["reversible"] = vars_["reversible"].isChecked()
            p["bf_role"] = vars_["bf_role"].currentText()
            p["tside_thread"] = vars_["tside_thread"].currentText().strip()
            p["tside_gender"] = vars_["tside_gender"].currentText()
            p["cside_thread"] = vars_["cside_thread"].currentText().strip()
            p["cside_gender"] = vars_["cside_gender"].currentText()
            if p.get("ghost"): p["ghost"] = False
            try: nq = max(0, int(vars_["qty"].text()))
            except ValueError: nq = cat_qty
            if cat_idx is not None:
                self.data["parts"][cat_idx]["qty"] = nq
            self._save(); self._refresh_stack()
            self.data.setdefault("ui", {})["part_dlg_geometry"] = f"{dlg.width()}x{dlg.height()}"
            dlg.accept()
        bf = QHBoxLayout()
        save_btn = QPushButton(self.t("save")); save_btn.setProperty("accent", True)
        save_btn.clicked.connect(_do_save)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(save_btn); bf.addWidget(cancel_btn)
        gl.addLayout(bf, r, 0, 1, 3)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    def _stack_rm(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        cfg = self.data["configurations"][ci]
        if si >= len(cfg.get("stack", [])): return
        cfg["stack"].pop(si)
        for mk in ("bf_start_idx", "bf_end_idx"):
            v = cfg.get(mk, -1)
            if v == si: cfg[mk] = -1
            elif v > si: cfg[mk] = v - 1
        self._save(); self._refresh_stack()

    def _stack_up(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None or si <= 0: return
        st = self.data["configurations"][ci]["stack"]
        st[si], st[si - 1] = st[si - 1], st[si]
        cfg = self.data["configurations"][ci]
        for mk in ("bf_start_idx", "bf_end_idx"):
            v = cfg.get(mk, -1)
            if v == si: cfg[mk] = si - 1
            elif v == si - 1: cfg[mk] = si
        self._save(); self._refresh_stack()
        # Re-select moved item
        for j in range(self.stree.topLevelItemCount()):
            it = self.stree.topLevelItem(j)
            if it.data(0, Qt.ItemDataRole.UserRole) == si - 1:
                self.stree.setCurrentItem(it); break

    def _stack_dn(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        st = self.data["configurations"][ci]["stack"]
        if si >= len(st) - 1: return
        st[si], st[si + 1] = st[si + 1], st[si]
        cfg = self.data["configurations"][ci]
        for mk in ("bf_start_idx", "bf_end_idx"):
            v = cfg.get(mk, -1)
            if v == si: cfg[mk] = si + 1
            elif v == si + 1: cfg[mk] = si
        self._save(); self._refresh_stack()
        for j in range(self.stree.topLevelItemCount()):
            it = self.stree.topLevelItem(j)
            if it.data(0, Qt.ItemDataRole.UserRole) == si + 1:
                self.stree.setCurrentItem(it); break

    def _stack_flip(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        stack = self.data["configurations"][ci].get("stack", [])
        if si >= len(stack): return
        item = stack[si]
        if not item.get("reversible"):
            QMessageBox.information(self, self.t("flip_piece"), self.t("not_reversible"))
            return
        item["flipped"] = not item.get("flipped", False)
        self._save(); self._refresh_stack()

    def _move_stack_item(self, from_idx, to_idx):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        if from_idx == to_idx or from_idx < 0 or from_idx >= len(stack): return
        if to_idx < 0 or to_idx >= len(stack): return
        item = stack.pop(from_idx)
        stack.insert(to_idx, item)
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        for mk, old_v in [("bf_start_idx", bs), ("bf_end_idx", be)]:
            if old_v < 0: continue
            if old_v == from_idx:
                cfg[mk] = to_idx
            elif from_idx < old_v <= to_idx:
                cfg[mk] = old_v - 1
            elif to_idx <= old_v < from_idx:
                cfg[mk] = old_v + 1
        self._save(); self._refresh_stack()

    # ── BF markers ──
    def _mark_bf_start(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        cfg = self.data["configurations"][ci]
        be = cfg.get("bf_end_idx", -1)
        if be >= 0 and si >= be:
            QMessageBox.warning(self, self.t("bf_start"), self.t("bf_start_after_end"))
            return
        cfg["bf_start_idx"] = si
        self._save(); self._refresh_stack()

    def _mark_bf_end(self):
        ci = self._cfg_idx(); si = self._stree_sel_idx()
        if ci is None or si is None: return
        cfg = self.data["configurations"][ci]
        bs = cfg.get("bf_start_idx", -1)
        if bs >= 0 and si <= bs:
            QMessageBox.warning(self, self.t("bf_end"), self.t("bf_end_before_start"))
            return
        cfg["bf_end_idx"] = si
        self._save(); self._refresh_stack()

    # ── resolve ghosts ──
    def _resolve_ghosts(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        ghost_indices = [i for i, item in enumerate(stack) if item.get("ghost")]
        if not ghost_indices:
            QMessageBox.information(self, self.t("resolve_ghosts"), self.t("no_ghosts"))
            return
        gi = ghost_indices[0]; ghost = stack[gi]
        need_tt = ghost.get("tside_thread", ""); need_tg = ghost.get("tside_gender", "")
        need_ct = ghost.get("cside_thread", ""); need_cg = ghost.get("cside_gender", "")
        matches = []
        for pi, p in enumerate(self.data["parts"]):
            if p.get("type") in ("type_telescope", "type_refractor", "type_camera", "type_dslr"):
                continue
            eff = _effective(p)
            pt, pg = eff.get("tside_thread", ""), eff.get("tside_gender", "")
            t_ok = True
            if need_tt and pt:
                if _extract_diam(need_tt) != _extract_diam(pt): t_ok = False
                elif need_tg and pg and need_tg != pg: t_ok = False
            ct, cg = eff.get("cside_thread", ""), eff.get("cside_gender", "")
            c_ok = True
            if need_ct and ct:
                if _extract_diam(need_ct) != _extract_diam(ct): c_ok = False
                elif need_cg and cg and need_cg != cg: c_ok = False
            if t_ok and c_ok and (pt or ct):
                matches.append((pi, p))
        dlg = QDialog(self); dlg.setWindowTitle(self.t("resolve_title"))
        dlg.resize(850, 500)
        vl = QVBoxLayout(dlg)
        vl.addWidget(QLabel(self.t("resolve_need",
            tside=f"{need_tt} {need_tg}".strip() or "?",
            cside=f"{need_ct} {need_cg}".strip() or "?")))
        tree = QTreeWidget()
        cols_h = [self.t("part_brand"), self.t("part_name"), self.t("part_type"),
                  "mm", self.t("tside"), self.t("cside"), self.t("qty")]
        tree.setHeaderLabels(cols_h)
        tree.setRootIsDecorated(False)
        for pi, p in matches:
            eff = _effective(p)
            tw = QTreeWidgetItem([
                p.get("brand", ""), p.get("name", ""), self._ttype(p.get("type", "")),
                f'{p.get("optical_length", 0):.1f}',
                f'{eff.get("tside_thread", "")} {eff.get("tside_gender", "")}'.strip(),
                f'{eff.get("cside_thread", "")} {eff.get("cside_gender", "")}'.strip(),
                str(p.get("qty", 0))])
            tw.setData(0, Qt.ItemDataRole.UserRole, pi)
            tree.addTopLevelItem(tw)
        vl.addWidget(tree)
        if not matches:
            vl.addWidget(QLabel(self.t("resolve_none")))
        def replace():
            sel = tree.selectedItems()
            if not sel: return
            part = copy.deepcopy(self.data["parts"][sel[0].data(0, Qt.ItemDataRole.UserRole)])
            part["flipped"] = False
            stack[gi] = part
            self._save(); self._refresh_stack(); dlg.accept()
        tree.itemDoubleClicked.connect(lambda: replace())
        bf = QHBoxLayout()
        ins_btn = QPushButton(self.t("insert")); ins_btn.setProperty("accent", True)
        ins_btn.clicked.connect(replace)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(ins_btn); bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    # ── pick part / conflict / ghost ──
    def _make_ghost(self, stack, ins_idx):
        ghost = {"brand": "", "name": self.t("ghost_name"), "type": "type_adapter",
                 "optical_length": 0, "mass": 0, "ghost": True, "flipped": False,
                 "tside_thread": "", "tside_gender": "", "cside_thread": "", "cside_gender": "",
                 "reversible": False, "bf_role": ""}
        if ins_idx > 0:
            prev = _effective(stack[ins_idx - 1])
            ct, cg = prev.get("cside_thread", ""), prev.get("cside_gender", "")
            ghost["tside_thread"] = ct
            ghost["tside_gender"] = {"Male": "Female", "Female": "Male"}.get(cg, "")
        if ins_idx < len(stack):
            nxt = _effective(stack[ins_idx])
            tt, tg = nxt.get("tside_thread", ""), nxt.get("tside_gender", "")
            ghost["cside_thread"] = tt
            ghost["cside_gender"] = {"Male": "Female", "Female": "Male"}.get(tg, "")
        return ghost

    def _pick_part_dlg(self, ci):
        dlg = QDialog(self); dlg.setWindowTitle(self.t("add_to_stack"))
        dlg.resize(850, 520)
        vl = QVBoxLayout(dlg)
        ftop = QHBoxLayout()
        ftop.addWidget(QLabel(self.t("search")))
        se = QLineEdit(); se.setFixedWidth(180)
        ftop.addWidget(se)
        ov = QCheckBox(self.t("filter_owned")); ov.setChecked(True)
        ftop.addWidget(ov); ftop.addStretch()
        vl.addLayout(ftop)
        tree = QTreeWidget()
        tree.setHeaderLabels([self.t("part_brand"), self.t("part_name"),
                              self.t("part_type"), "mm", self.t("tside"), self.t("cside")])
        tree.setRootIsDecorated(False)
        vl.addWidget(tree)
        search_timer = QTimer(dlg); search_timer.setSingleShot(True); search_timer.setInterval(200)
        def refresh():
            tree.clear(); s = se.text().lower(); owned_only = ov.isChecked()
            count = 0
            for j, search_text, p in self._get_parts_search_cache():
                if owned_only and p.get("qty", 0) <= 0: continue
                if s and s not in search_text: continue
                tw = QTreeWidgetItem([
                    p.get("brand", ""), p.get("name", ""), self._ttype(p.get("type", "")),
                    f'{p.get("optical_length", 0):.1f}',
                    f'{p.get("tside_thread", "")} {p.get("tside_gender", "")}'.strip(),
                    f'{p.get("cside_thread", "")} {p.get("cside_gender", "")}'.strip()])
                tw.setData(0, Qt.ItemDataRole.UserRole, j)
                tree.addTopLevelItem(tw)
                count += 1
                if count >= 500: break
        search_timer.timeout.connect(refresh)
        se.textChanged.connect(lambda: search_timer.start())
        ov.stateChanged.connect(lambda: refresh())
        refresh()
        def add():
            sel = tree.selectedItems()
            if not sel: return
            pidx = sel[0].data(0, Qt.ItemDataRole.UserRole)
            part = copy.deepcopy(self.data["parts"][pidx]); part["flipped"] = False
            if not self._conflict_ok_with_adjust(part, pidx): return
            stack = self.data["configurations"][ci]["stack"]
            ins = len(stack)
            cc = self._check_conn(stack, ins, part)
            if cc == "ghost":
                ghost = self._make_ghost(stack, ins)
                stack.append(ghost); stack.append(part)
            elif cc == "flip":
                part["flipped"] = not part.get("flipped", False); stack.append(part)
            elif cc == "mark_flip":
                part["reversible"] = True
                part["flipped"] = not part.get("flipped", False)
                self.data["parts"][pidx]["reversible"] = True; stack.append(part)
            elif cc == "edit":
                stack.append(part)
                self._save(); self._refresh_stack(); dlg.accept()
                # Select last item and open editor
                for j in range(self.stree.topLevelItemCount()):
                    it = self.stree.topLevelItem(j)
                    if it.data(0, Qt.ItemDataRole.UserRole) == len(stack) - 1:
                        self.stree.setCurrentItem(it); break
                self._stack_edit(); return
            elif cc:
                stack.append(part)
            else:
                return
            cfg = self.data["configurations"][ci]
            added_idx = len(cfg["stack"]) - 1
            if part.get("bf_role") == "start" and cfg.get("bf_start_idx", -1) < 0:
                cfg["bf_start_idx"] = added_idx
            elif part.get("bf_role") == "end" and cfg.get("bf_end_idx", -1) < 0:
                cfg["bf_end_idx"] = added_idx
            self._save(); self._refresh_stack(); dlg.accept()
        tree.itemDoubleClicked.connect(lambda: add())
        bf = QHBoxLayout()
        ins_btn = QPushButton(self.t("insert")); ins_btn.setProperty("accent", True)
        ins_btn.clicked.connect(add)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(ins_btn); bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    def _conflict_ok(self, part):
        nm = part.get("name", ""); qty = part.get("qty", 0)
        for p in self.data["parts"]:
            if p.get("name") == nm: qty = p.get("qty", 0); break
        if qty <= 0: return True
        total = 0; names = []
        for cfg in self.data["configurations"]:
            for item in cfg.get("stack", []):
                if item.get("name") == nm:
                    total += 1
                    if cfg["name"] not in names: names.append(cfg["name"])
                    break
        if total >= qty and names:
            return QMessageBox.question(self, self.t("conflict_title"),
                self.t("conflict_msg", name=nm, cfgs=", ".join(names),
                        qty=qty, used=total)) == QMessageBox.StandardButton.Yes
        return True

    def _conflict_ok_with_adjust(self, part, part_idx):
        nm = part.get("name", "")
        qty = self.data["parts"][part_idx].get("qty", 0)
        total = 0; cfgs_used = []
        for cfg in self.data["configurations"]:
            count_in = sum(1 for item in cfg.get("stack", []) if item.get("name") == nm)
            if count_in > 0: total += count_in; cfgs_used.append(cfg["name"])
        if qty > 0 and total + 1 <= qty: return True
        new_qty = max(total + 1, 1)
        dlg = QDialog(self); dlg.setWindowTitle(self.t("qty_adjust_title"))
        dlg.resize(440, 240)
        vl = QVBoxLayout(dlg)
        if qty <= 0:
            msg = self.t("qty_not_owned_msg", name=nm)
        else:
            msg = self.t("qty_adjust_msg", name=nm, used=total, qty=qty, new_qty=new_qty)
        ml = QLabel(msg); ml.setWordWrap(True); vl.addWidget(ml)
        qf = QHBoxLayout()
        qf.addWidget(QLabel(self.t("qty_adjust_custom")))
        qe = QLineEdit(str(new_qty)); qe.setFixedWidth(40)
        qm = QPushButton("−"); qm.setFixedWidth(28)
        qm.clicked.connect(lambda: qe.setText(str(max(1, _safe_int(qe.text(), 1) - 1))))
        qp = QPushButton("+"); qp.setFixedWidth(28)
        qp.clicked.connect(lambda: qe.setText(str(_safe_int(qe.text(), 1) + 1)))
        qf.addWidget(qm); qf.addWidget(qe); qf.addWidget(qp); qf.addStretch()
        vl.addLayout(qf)
        if cfgs_used:
            il = QLabel(f"({', '.join(cfgs_used)})"); il.setStyleSheet(f"color: {C['fg_dim']};")
            vl.addWidget(il)
        dlg.result_val = False
        bf = QHBoxLayout()
        def accept():
            try: nq = max(1, int(qe.text()))
            except ValueError: nq = new_qty
            self.data["parts"][part_idx]["qty"] = nq; self._save()
            if self._catalog_win and self._catalog_win.isVisible():
                self._catalog_win._refresh()
            dlg.result_val = True; dlg.accept()
        def add_anyway():
            dlg.result_val = True; dlg.accept()
        ok_btn = QPushButton(self.t("ok") + " + " + self.t("qty"))
        ok_btn.setProperty("accent", True); ok_btn.clicked.connect(accept)
        ins_btn = QPushButton(self.t("insert")); ins_btn.clicked.connect(add_anyway)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(ok_btn); bf.addWidget(ins_btn); bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()
        return dlg.result_val

    def _check_conn(self, stack, ins_idx, part):
        eff_new = _effective(part); problems = []
        if ins_idx > 0:
            prev = stack[ins_idx - 1]; eff_prev = _effective(prev)
            t_a, g_a = eff_prev.get("cside_thread", ""), eff_prev.get("cside_gender", "")
            t_b, g_b = eff_new.get("tside_thread", ""), eff_new.get("tside_gender", "")
            if t_a and t_b:
                if _extract_diam(t_a) != _extract_diam(t_b):
                    problems.append((prev, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(),
                                     self.t("conn_reason_thread", a=t_a, b=t_b)))
                elif g_a and g_b and g_a == g_b:
                    problems.append((prev, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(),
                                     self.t("conn_reason_gender", g=g_a)))
        if ins_idx < len(stack):
            nxt = stack[ins_idx]; eff_nxt = _effective(nxt)
            t_a, g_a = eff_new.get("cside_thread", ""), eff_new.get("cside_gender", "")
            t_b, g_b = eff_nxt.get("tside_thread", ""), eff_nxt.get("tside_gender", "")
            if t_a and t_b:
                if _extract_diam(t_a) != _extract_diam(t_b):
                    problems.append((part, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(),
                                     self.t("conn_reason_thread", a=t_a, b=t_b)))
                elif g_a and g_b and g_a == g_b:
                    problems.append((part, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(),
                                     self.t("conn_reason_gender", g=g_a)))
        if not problems: return True
        flip_fixes = False
        if part.get("type") not in NOT_REVERSIBLE:
            flipped_part = dict(part, flipped=not part.get("flipped", False))
            eff_flip = _effective(flipped_part); flip_problems = []
            if ins_idx > 0:
                prev = stack[ins_idx - 1]; eff_prev = _effective(prev)
                t_a, g_a = eff_prev.get("cside_thread", ""), eff_prev.get("cside_gender", "")
                t_b, g_b = eff_flip.get("tside_thread", ""), eff_flip.get("tside_gender", "")
                if t_a and t_b:
                    if _extract_diam(t_a) != _extract_diam(t_b): flip_problems.append(True)
                    elif g_a and g_b and g_a == g_b: flip_problems.append(True)
            if ins_idx < len(stack):
                nxt = stack[ins_idx]; eff_nxt = _effective(nxt)
                t_a, g_a = eff_flip.get("cside_thread", ""), eff_flip.get("cside_gender", "")
                t_b, g_b = eff_nxt.get("tside_thread", ""), eff_nxt.get("tside_gender", "")
                if t_a and t_b:
                    if _extract_diam(t_a) != _extract_diam(t_b): flip_problems.append(True)
                    elif g_a and g_b and g_a == g_b: flip_problems.append(True)
            flip_fixes = len(flip_problems) == 0
        p_item, p_out, p_in, reason = problems[0]
        prev_name = f'{p_item.get("brand", "")} {p_item.get("name", "")}'.strip()
        new_name = f'{part.get("brand", "")} {part.get("name", "")}'.strip()
        msg = self.t("conn_warn_msg", prev_name=prev_name, prev_conn=p_out,
                      new_name=new_name, new_conn=p_in, reason=reason)
        dlg = QDialog(self); dlg.setWindowTitle(self.t("conn_warn_title"))
        dlg.resize(560, 280)
        vl = QVBoxLayout(dlg)
        ml = QLabel(msg); ml.setWordWrap(True); vl.addWidget(ml)
        dlg.result_val = False
        bf = QHBoxLayout()
        if flip_fixes and part.get("reversible"):
            b = QPushButton(self.t("conn_flip_insert")); b.setProperty("accent", True)
            b.clicked.connect(lambda: (setattr(dlg, 'result_val', "flip"), dlg.accept()))
            bf.addWidget(b)
        elif flip_fixes:
            b = QPushButton(self.t("conn_mark_flip")); b.setProperty("accent", True)
            b.clicked.connect(lambda: (setattr(dlg, 'result_val', "mark_flip"), dlg.accept()))
            bf.addWidget(b)
        for txt, val in [(self.t("insert"), True), (self.t("conn_insert_ghost"), "ghost"),
                         (self.t("conn_edit_part"), "edit")]:
            b = QPushButton(txt)
            b.clicked.connect(lambda checked, v=val: (setattr(dlg, 'result_val', v), dlg.accept()))
            bf.addWidget(b)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()
        return dlg.result_val

    def _handle_catalog_drop(self, part_idx):
        ci = self._cfg_idx()
        if ci is None:
            QMessageBox.information(self, "", self.t("no_config")); return
        if part_idx >= len(self.data["parts"]): return
        part = copy.deepcopy(self.data["parts"][part_idx]); part["flipped"] = False
        if not self._conflict_ok_with_adjust(part, part_idx): return
        cfg = self.data["configurations"][ci]
        be = cfg.get("bf_end_idx", -1)
        ins_idx = (be + 1) if be >= 0 else len(cfg["stack"])
        cc = self._check_conn(cfg["stack"], ins_idx, part)
        def _shift_bf(idx, count=1):
            for mk in ("bf_start_idx", "bf_end_idx"):
                if cfg.get(mk, -1) >= idx: cfg[mk] = cfg[mk] + count
        if cc == "ghost":
            ghost = self._make_ghost(cfg["stack"], ins_idx)
            cfg["stack"].insert(ins_idx, ghost); _shift_bf(ins_idx)
            cfg["stack"].insert(ins_idx + 1, part); _shift_bf(ins_idx + 1)
            added_idx = ins_idx + 1
        elif cc == "flip":
            part["flipped"] = not part.get("flipped", False)
            cfg["stack"].insert(ins_idx, part); _shift_bf(ins_idx)
            added_idx = ins_idx
        elif cc == "mark_flip":
            part["reversible"] = True
            part["flipped"] = not part.get("flipped", False)
            self.data["parts"][part_idx]["reversible"] = True
            cfg["stack"].insert(ins_idx, part); _shift_bf(ins_idx)
            added_idx = ins_idx
        elif cc == "edit":
            cfg["stack"].insert(ins_idx, part); _shift_bf(ins_idx)
            self._save(); self._refresh_stack()
            for j in range(self.stree.topLevelItemCount()):
                it = self.stree.topLevelItem(j)
                if it.data(0, Qt.ItemDataRole.UserRole) == ins_idx:
                    self.stree.setCurrentItem(it); break
            self._stack_edit(); return
        elif cc:
            cfg["stack"].insert(ins_idx, part); _shift_bf(ins_idx)
            added_idx = ins_idx
        else:
            return
        if part.get("bf_role") == "start" and cfg.get("bf_start_idx", -1) < 0:
            cfg["bf_start_idx"] = added_idx
        elif part.get("bf_role") == "end" and cfg.get("bf_end_idx", -1) < 0:
            cfg["bf_end_idx"] = added_idx
        self._save(); self._refresh_stack()

    # ── part dialog (catalog add/edit) ──
    def _part_dlg(self, idx, on_done=None):
        is_edit = idx is not None
        p = self.data["parts"][idx] if is_edit else {
            "brand": "", "name": "", "type": "type_adapter", "optical_length": 0, "mass": 0,
            "tside_thread": "", "tside_gender": "", "cside_thread": "", "cside_gender": "",
            "reversible": True, "bf_role": "", "qty": 0, "notes": ""}
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("edit_part") if is_edit else self.t("add_part"))
        _saved = self.data.get("ui", {}).get("part_dlg_geometry", "600x740")
        try:
            pw, ph = (int(v) for v in _saved.split("x")[:2])
            dlg.resize(pw, ph)
        except (ValueError, IndexError):
            dlg.resize(600, 740)
        dlg.setMinimumSize(500, 500)
        gl = QGridLayout(dlg)
        r = 0; vars_ = {}
        def _row(label, key, wf, **kw):
            nonlocal r
            gl.addWidget(QLabel(label), r, 0, Qt.AlignmentFlag.AlignLeft)
            w, var = wf(r, kw); vars_[key] = var; r += 1; return w
        def _entry(row, kw):
            e = QLineEdit(str(kw.get("val", ""))); e.setFixedWidth(kw.get("pw", 200))
            gl.addWidget(e, row, 1, 1, 2); return e, e
        def _combo(row, kw):
            c = QComboBox(); c.setEditable(not kw.get("ro", False))
            c.addItems([str(v) for v in kw.get("vals", [])])
            val = str(kw.get("val", ""))
            ix = c.findText(val)
            if ix >= 0: c.setCurrentIndex(ix)
            elif not kw.get("ro"): c.setCurrentText(val)
            gl.addWidget(c, row, 1, 1, 2); return c, c
        def _check(row, kw):
            c = QCheckBox(); c.setChecked(kw.get("val", False))
            gl.addWidget(c, row, 1); return c, c

        # brand + auto-fill
        gl.addWidget(QLabel(self.t("part_brand")), r, 0)
        _all_brands = sorted({"Custom Made"} | _REF_BRANDS |
            {pp.get("brand", "") for pp in self.data["parts"] if pp.get("brand", "")})
        bc = QComboBox(); bc.setEditable(True); bc.addItems(_all_brands)
        bc.setCurrentText(p.get("brand", ""))
        gl.addWidget(bc, r, 1); vars_["brand"] = bc
        def _autofill():
            q = (bc.currentText().lower() + " " + vars_.get("name", QLineEdit()).text().lower()).strip()
            if not q: return
            ref = _REF_INDEX.get(q)
            if ref is None:
                ix = bisect.bisect_left(_REF_KEYS_SORTED, q)
                if ix < len(_REF_KEYS_SORTED) and _REF_KEYS_SORTED[ix].startswith(q):
                    ref = _REF_INDEX[_REF_KEYS_SORTED[ix]]
                else:
                    for k in _REF_KEYS_SORTED:
                        if q in k: ref = _REF_INDEX[k]; break
            if ref is None: return
            for k, vk in [("brand", "brand"), ("name", "name"), ("optical_length", "mm"),
                          ("mass", "mass")]:
                w = vars_.get(vk)
                if w is None: continue
                if isinstance(w, QComboBox): w.setCurrentText(str(ref.get(k, "")))
                elif isinstance(w, QLineEdit): w.setText(str(ref.get(k, "")))
            if "type" in vars_:
                vars_["type"].setCurrentText(self._ttype(ref.get("type", "")))
            for side in ("tside_thread", "tside_gender", "cside_thread", "cside_gender"):
                if side in vars_: vars_[side].setCurrentText(ref.get(side, ""))
            if "reversible" in vars_: vars_["reversible"].setChecked(ref.get("reversible", False))
            if "bf_role" in vars_: vars_["bf_role"].setCurrentText(ref.get("bf_role", ""))
        af_btn = QPushButton("Auto-fill"); af_btn.setProperty("accent", True)
        af_btn.clicked.connect(_autofill)
        self._tip(af_btn, "Auto-fill fields from product database",
                  "Remplir depuis la base de produits")
        gl.addWidget(af_btn, r, 2); r += 1

        _row(self.t("part_name"), "name", _entry, val=p.get("name", ""))
        type_map = {self._ttype(k): k for k in PART_TYPES}
        _row(self.t("part_type"), "type", _combo, val=self._ttype(p.get("type", "")),
             vals=sorted(type_map.keys()), ro=True)
        _row(self.t("optical_length"), "mm", _entry, val=p.get("optical_length", 0), pw=80)
        _row(self.t("mass_label"), "mass", _entry, val=p.get("mass", 0), pw=80)
        _row(self.t("reversible"), "reversible", _check, val=p.get("reversible", False))
        _row(self.t("bf_role"), "bf_role", _combo, val=p.get("bf_role", ""),
             vals=["", "start", "end"], ro=True)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        gl.addWidget(sep, r, 0, 1, 3); r += 1
        sl = QLabel(self.t("tside"))
        sl.setStyleSheet(f"font-weight: bold; color: {C['accent_teal']};")
        gl.addWidget(sl, r, 0, 1, 3); r += 1
        _row(self.t("thread"), "tside_thread", _combo, val=p.get("tside_thread", ""), vals=THREADS)
        _row(self.t("gender"), "tside_gender", _combo, val=p.get("tside_gender", ""),
             vals=GENDERS, ro=True)
        cl = QLabel(self.t("cside"))
        cl.setStyleSheet(f"font-weight: bold; color: {C['accent_teal']};")
        gl.addWidget(cl, r, 0, 1, 3); r += 1
        _row(self.t("thread"), "cside_thread", _combo, val=p.get("cside_thread", ""), vals=THREADS)
        _row(self.t("gender"), "cside_gender", _combo, val=p.get("cside_gender", ""),
             vals=GENDERS, ro=True)
        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        gl.addWidget(sep2, r, 0, 1, 3); r += 1
        gl.addWidget(QLabel(self.t("qty")), r, 0)
        qf = QHBoxLayout()
        qe = QLineEdit(str(p.get("qty", 0))); qe.setFixedWidth(40); vars_["qty"] = qe
        qm = QPushButton("−"); qm.setFixedWidth(28)
        qm.clicked.connect(lambda: qe.setText(str(max(0, _safe_int(qe.text()) - 1))))
        qp = QPushButton("+"); qp.setFixedWidth(28)
        qp.clicked.connect(lambda: qe.setText(str(_safe_int(qe.text()) + 1)))
        qf.addWidget(qm); qf.addWidget(qe); qf.addWidget(qp); qf.addStretch()
        gl.addLayout(qf, r, 1, 1, 2); r += 1
        _row(self.t("part_notes"), "notes", _entry, val=p.get("notes", ""), pw=300)
        def _do_save():
            try: ol = float(str(vars_["mm"].text()).replace(",", "."))
            except (ValueError, AttributeError): ol = 0
            try: ms = float(str(vars_["mass"].text()).replace(",", "."))
            except (ValueError, AttributeError): ms = 0
            try: q = max(0, int(vars_["qty"].text()))
            except ValueError: q = 0
            td = type_map.get(vars_["type"].currentText(), "type_adapter")
            np = {"brand": vars_["brand"].currentText().strip(),
                  "name": vars_["name"].text().strip(),
                  "type": td, "optical_length": ol, "mass": ms,
                  "reversible": vars_["reversible"].isChecked(),
                  "bf_role": vars_["bf_role"].currentText(),
                  "tside_thread": vars_["tside_thread"].currentText().strip(),
                  "tside_gender": vars_["tside_gender"].currentText(),
                  "cside_thread": vars_["cside_thread"].currentText().strip(),
                  "cside_gender": vars_["cside_gender"].currentText(),
                  "qty": q, "notes": vars_["notes"].text().strip()}
            if not np["name"]: return
            if is_edit: self.data["parts"][idx] = np
            else: self.data["parts"].append(np)
            self._save()
            if on_done: on_done()
            self.data.setdefault("ui", {})["part_dlg_geometry"] = f"{dlg.width()}x{dlg.height()}"
            dlg.accept()
        bf = QHBoxLayout()
        save_btn = QPushButton(self.t("save")); save_btn.setProperty("accent", True)
        save_btn.clicked.connect(_do_save)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(save_btn); bf.addWidget(cancel_btn)
        gl.addLayout(bf, r, 0, 1, 3)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    # ── calc ──
    def _calc(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        total = sum(it.get("optical_length", 0) for it in stack)
        lu = self.data.get("length_unit", "mm")
        try: target = float(self.e_target.text().replace(",", "."))
        except ValueError: target = 0
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        bf_total = sum(stack[j].get("optical_length", 0) for j in range(bs + 1, be + 1)) \
            if 0 <= bs <= be < len(stack) else total
        diff = bf_total - target
        self.lbl_total.setText(f'{self.t("total_label")} {_fmt_len(total, lu)}')
        if 0 <= bs <= be < len(stack):
            sn = stack[bs].get("name", "?")[:20]
            en = stack[be].get("name", "?")[:20]
            self.lbl_bf.setText(
                f'{self.t("bf_total_label")} {_fmt_len(bf_total, lu)}  ({sn} → {en})')
        else:
            self.lbl_bf.setText(f'{self.t("bf_total_label")} {_fmt_len(bf_total, lu)}')
        if abs(diff) < 0.1:
            self.lbl_diff.setText(f'{self.t("diff_label")} {self.t("status_ok")}')
            self.lbl_diff.setStyleSheet(
                f"font-size: 11pt; font-weight: bold; color: {C['accent_green']};")
        elif diff > 0:
            self.lbl_diff.setText(
                f'{self.t("diff_label")} {self.t("status_long", v=abs(diff))} {lu}')
            self.lbl_diff.setStyleSheet(
                f"font-size: 11pt; font-weight: bold; color: {C['accent_red']};")
        else:
            self.lbl_diff.setText(
                f'{self.t("diff_label")} {self.t("status_short", v=abs(diff))} {lu}')
            self.lbl_diff.setStyleSheet(
                f"font-size: 11pt; font-weight: bold; color: {C['accent_orange']};")
        self._save_cfg()
        self.diagram.set_data(stack, bs, be, target)

    # ── suggest ──
    def _suggest(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        try: target = float(self.e_target.text().replace(",", "."))
        except ValueError: return
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        bf_total = sum(stack[j].get("optical_length", 0) for j in range(bs + 1, be + 1)) \
            if 0 <= bs <= be < len(stack) else sum(it.get("optical_length", 0) for it in stack)
        gap = target - bf_total
        if abs(gap) < 0.05:
            QMessageBox.information(self, self.t("auto_suggest"), self.t("status_ok")); return
        last_idx = be if be >= 0 else len(stack) - 1
        last_cs = last_cg = ""
        if 0 <= last_idx < len(stack):
            eff = _effective(stack[last_idx])
            last_cs = eff.get("cside_thread", ""); last_cg = eff.get("cside_gender", "")
        cands = []
        for pi, p in enumerate(self.data["parts"]):
            if p.get("optical_length", 0) <= 0: continue
            if p.get("type") in ("type_telescope", "type_refractor"): continue
            if p.get("qty", 0) <= 0: continue
            if last_cs and p.get("tside_thread"):
                if not _conn_compat(last_cs, last_cg, p.get("tside_thread", ""),
                                    p.get("tside_gender", "")): continue
            ng = gap - p["optical_length"]
            cands.append({"name": f'{p.get("brand", "")} {p["name"]}'.strip(),
                          "length": p["optical_length"], "new_gap": ng, "part_idx": pi})
        cands.sort(key=lambda cd: abs(cd["new_gap"]))
        dlg = QDialog(self); dlg.setWindowTitle(self.t("suggest_title"))
        dlg.resize(640, 420)
        vl = QVBoxLayout(dlg)
        vl.addWidget(QLabel(self.t("suggest_gap", v=gap)))
        if not cands:
            vl.addWidget(QLabel(self.t("suggest_none")))
            cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
            vl.addWidget(cancel_btn)
            dlg.setStyleSheet(f"background: {C['bg_mid']};")
            _center_dlg(dlg, self); dlg.exec(); return
        tree = QTreeWidget()
        tree.setHeaderLabels([self.t("part_name"), "mm", self.t("suggest_after")])
        tree.setRootIsDecorated(False)
        tree.setColumnWidth(0, 320); tree.setColumnWidth(1, 80)
        for j, cd in enumerate(cands[:40]):
            at = self.t("suggest_perfect") if abs(cd["new_gap"]) < 0.05 else f'{cd["new_gap"]:+.2f} mm'
            tw = QTreeWidgetItem([cd["name"], f'{cd["length"]:.1f}', at])
            tw.setData(0, Qt.ItemDataRole.UserRole, j)
            if abs(cd["new_gap"]) < 0.05:
                for col in range(3):
                    tw.setForeground(col, QColor(C["accent_green"]))
                    tw.setBackground(col, QColor("#244030"))
            tree.addTopLevelItem(tw)
        vl.addWidget(tree)
        def ins():
            sel = tree.selectedItems()
            if not sel: return
            cd = cands[sel[0].data(0, Qt.ItemDataRole.UserRole)]
            part = copy.deepcopy(self.data["parts"][cd["part_idx"]]); part["flipped"] = False
            ghost_idx = None
            lo = (bs + 1 if bs >= 0 else 0); hi = (be if be >= 0 else len(cfg["stack"]))
            for gi in range(lo, hi):
                if gi < len(cfg["stack"]) and cfg["stack"][gi].get("ghost"):
                    ghost_idx = gi; break
            if ghost_idx is not None:
                cfg["stack"][ghost_idx] = part
            else:
                iidx = be if be >= 0 else len(cfg["stack"])
                cfg["stack"].insert(iidx, part)
                for mk in ("bf_start_idx", "bf_end_idx"):
                    if cfg.get(mk, -1) >= iidx: cfg[mk] = cfg[mk] + 1
            self._save(); self._refresh_stack(); dlg.accept()
        tree.itemDoubleClicked.connect(lambda: ins())
        bf = QHBoxLayout()
        ins_btn = QPushButton(self.t("insert")); ins_btn.setProperty("accent", True)
        ins_btn.clicked.connect(ins)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(ins_btn); bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    # ── auto-complete ──
    def _auto_complete(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        if bs < 0 or be < 0 or bs >= len(stack) or be >= len(stack):
            QMessageBox.information(self, self.t("auto_complete"), self.t("ac_need_bf")); return
        try: target = float(self.e_target.text().replace(",", "."))
        except ValueError: return
        bf_total = sum(stack[j].get("optical_length", 0) for j in range(bs + 1, be + 1))
        gap = target - bf_total
        if abs(gap) < 0.1:
            QMessageBox.information(self, self.t("auto_complete"), self.t("status_ok")); return
        dlg = QDialog(self); dlg.setWindowTitle(self.t("ac_title"))
        dlg.resize(700, 520)
        vl = QVBoxLayout(dlg)
        vl.addWidget(QLabel(self.t("suggest_gap", v=gap)))
        chk_f = QHBoxLayout()
        use_other = QCheckBox(self.t("ac_use_other"))
        use_unowned = QCheckBox(self.t("ac_use_unowned"))
        chk_f.addWidget(use_other); chk_f.addWidget(use_unowned); chk_f.addStretch()
        vl.addLayout(chk_f)
        rtree = QTreeWidget()
        rtree.setHeaderLabels(["Combination", "mm", self.t("diff_label")])
        rtree.setRootIsDecorated(False)
        rtree.setColumnWidth(0, 420); rtree.setColumnWidth(1, 80)
        vl.addWidget(rtree)
        solutions = []
        def search():
            nonlocal solutions
            rtree.clear(); solutions = []
            candidates = []; used_names = set()
            if not use_other.isChecked():
                for ocfg in self.data["configurations"]:
                    if ocfg is cfg: continue
                    for item in ocfg.get("stack", []): used_names.add(item.get("name", ""))
            for pi, p in enumerate(self.data["parts"]):
                if not use_unowned.isChecked() and p.get("qty", 0) <= 0: continue
                if p.get("optical_length", 0) <= 0: continue
                if p.get("type") in ("type_telescope", "type_refractor", "type_camera",
                                     "type_dslr"): continue
                if not use_other.isChecked() and p.get("name", "") in used_names: continue
                candidates.append((pi, p))
            if not candidates: return
            candidates.sort(key=lambda x: x[1]["optical_length"])
            abs_gap = abs(gap); max_useful = abs_gap * 1.5; tolerance = 0.5
            for pi, p in candidates:
                ol = p["optical_length"]; rem = gap - ol
                if abs(rem) < abs_gap * 1.5:
                    names = f'{p.get("brand", "")} {p["name"]}'.strip()
                    solutions.append((names, rem, ol, [pi]))
            solutions.sort(key=lambda s: abs(s[1]))
            if not (solutions and abs(solutions[0][1]) < tolerance):
                n = len(candidates)
                for i in range(n):
                    ol_i = candidates[i][1]["optical_length"]
                    if ol_i > max_useful: break
                    for j in range(i + 1, n):
                        total_l = ol_i + candidates[j][1]["optical_length"]
                        if total_l > max_useful and gap > 0: break
                        rem = gap - total_l
                        if abs(rem) < abs_gap * 1.5:
                            names = " + ".join(
                                f'{candidates[k][1].get("brand", "")} {candidates[k][1]["name"]}'.strip()
                                for k in (i, j))
                            solutions.append((names, rem, total_l,
                                              [candidates[i][0], candidates[j][0]]))
                solutions.sort(key=lambda s: abs(s[1]))
                if not (solutions and abs(solutions[0][1]) < tolerance) and n <= 200:
                    count3 = 0
                    for i in range(n):
                        ol_i = candidates[i][1]["optical_length"]
                        if ol_i > max_useful: break
                        for j in range(i + 1, n):
                            ol_ij = ol_i + candidates[j][1]["optical_length"]
                            if ol_ij > max_useful and gap > 0: break
                            for k in range(j + 1, n):
                                total_l = ol_ij + candidates[k][1]["optical_length"]
                                if total_l > max_useful and gap > 0: break
                                rem = gap - total_l
                                if abs(rem) < abs_gap * 1.5:
                                    names = " + ".join(
                                        f'{candidates[m][1].get("brand", "")} {candidates[m][1]["name"]}'.strip()
                                        for m in (i, j, k))
                                    solutions.append((names, rem, total_l,
                                        [candidates[i][0], candidates[j][0], candidates[k][0]]))
                                    count3 += 1
                                    if count3 > 500: break
                            if count3 > 500: break
                        if count3 > 500: break
            solutions.sort(key=lambda s: abs(s[1]))
            for j, (names, rem, total_l, _) in enumerate(solutions[:30]):
                at = self.t("suggest_perfect") if abs(rem) < 0.05 else f'{rem:+.2f} mm'
                tw = QTreeWidgetItem([names, f'{total_l:.1f}', at])
                tw.setData(0, Qt.ItemDataRole.UserRole, j)
                if abs(rem) < 0.05:
                    for col in range(3):
                        tw.setForeground(col, QColor(C["accent_green"]))
                        tw.setBackground(col, QColor("#244030"))
                rtree.addTopLevelItem(tw)
        use_other.stateChanged.connect(lambda: search())
        use_unowned.stateChanged.connect(lambda: search())
        search()
        def apply_sol():
            sel = rtree.selectedItems()
            if not sel: return
            sol = solutions[sel[0].data(0, Qt.ItemDataRole.UserRole)]
            lo = (bs + 1 if bs >= 0 else 0); hi = (be if be >= 0 else len(cfg["stack"]))
            ghosts = [gi for gi in range(lo, hi)
                      if gi < len(cfg["stack"]) and cfg["stack"][gi].get("ghost")]
            ins_idx = be if be >= 0 else len(cfg["stack"])
            for pi in sol[3]:
                part = copy.deepcopy(self.data["parts"][pi]); part["flipped"] = False
                if ghosts:
                    cfg["stack"][ghosts.pop(0)] = part
                else:
                    cfg["stack"].insert(ins_idx, part)
                    for mk in ("bf_start_idx", "bf_end_idx"):
                        if cfg.get(mk, -1) >= ins_idx: cfg[mk] = cfg[mk] + 1
                    ins_idx += 1
            self._save(); self._refresh_stack(); dlg.accept()
        rtree.itemDoubleClicked.connect(lambda: apply_sol())
        bf = QHBoxLayout()
        ins_btn = QPushButton(self.t("insert")); ins_btn.setProperty("accent", True)
        ins_btn.clicked.connect(apply_sol)
        cancel_btn = QPushButton(self.t("cancel")); cancel_btn.clicked.connect(dlg.reject)
        bf.addWidget(ins_btn); bf.addWidget(cancel_btn)
        vl.addLayout(bf)
        dlg.setStyleSheet(f"background: {C['bg_mid']};")
        _center_dlg(dlg, self); dlg.exec()

    # ── export / import ──
    def _export(self):
        i = self._cfg_idx()
        if i is None: return
        cfg = self.data["configurations"][i]
        path, _ = QFileDialog.getSaveFileName(self, "Export", cfg["name"] + ".json",
                                              "JSON (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(cfg, fh, indent=2, ensure_ascii=False)
            except OSError as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh: cfg = json.load(fh)
            except (json.JSONDecodeError, OSError):
                QMessageBox.critical(self, "Error", "Invalid or unreadable JSON file.")
                return
            if "name" in cfg and "stack" in cfg:
                self.data["configurations"].append(cfg)
                self._save(); self._refresh_cfgs()

    def _export_all(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export All", "backfocus_all_data.json",
                                              "JSON (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(self.data, fh, indent=2, ensure_ascii=False)
                QMessageBox.information(self, self.t("export_all"), self.t("export_all_ok"))
            except OSError as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _import_all(self):
        if QMessageBox.question(self, self.t("import_all"),
                self.t("confirm_import_all")) != QMessageBox.StandardButton.Yes:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Import All", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh: imported = json.load(fh)
            except (json.JSONDecodeError, OSError):
                QMessageBox.critical(self, "Error", "Invalid or unreadable JSON file.")
                return
            for k, v in _default_data().items():
                imported.setdefault(k, v)
            if "parts" in imported and "configurations" in imported:
                self.data = imported
                self.lang = self.data.get("language", "fr")
                self._invalidate_parts_cache()
                save_data(self.data, sync=True)
                self._apply_language(); self._refresh_cfgs()
                QMessageBox.information(self, self.t("import_all"), self.t("import_all_ok"))

    def _save_all(self):
        _save_writer.flush_sync()
        save_data(self.data, sync=True)
        QMessageBox.information(self, self.t("save_all"), self.t("save_all_ok"))

    # ── language ──
    def _set_lang(self, lang):
        self.lang = lang; self.data["language"] = lang
        self._save(); self._apply_language()

    def _apply_language(self):
        self.setWindowTitle(self.t("app_title"))
        self.menu.clear()

        fm = self.menu.addMenu(self.t("file"))
        fm.addAction(self.t("save_all"), self._save_all)
        fm.addSeparator()
        fm.addAction(self.t("export_config"), self._export)
        fm.addAction(self.t("import_config"), self._import)
        fm.addSeparator()
        fm.addAction(self.t("export_all"), self._export_all)
        fm.addAction(self.t("import_all"), self._import_all)
        fm.addSeparator()
        fm.addAction(self.t("quit"), self.close)

        vm = self.menu.addMenu(self.t("view"))
        vm.addAction(self.t("open_catalog"), self._open_catalog)
        vm.addSeparator()
        vm.addAction(self.t("fits_analyzer"), self._open_fits_analyzer)

        sm = self.menu.addMenu(self.t("settings"))
        um = sm.addMenu(self.t("units"))
        um.addAction(self.t("length_mm"), lambda: self._set_unit("length_unit", "mm"))
        um.addAction(self.t("length_in"), lambda: self._set_unit("length_unit", "in"))
        um.addSeparator()
        um.addAction(self.t("mass_g"), lambda: self._set_unit("mass_unit", "g"))
        um.addAction(self.t("mass_oz"), lambda: self._set_unit("mass_unit", "oz"))

        hm = self.menu.addMenu(self.t("help_menu"))
        hm.addAction(self.t("user_guide"), lambda: open_help(self, self.lang))
        hm.addAction(self.t("about"), self._about)
        hm.addSeparator()
        hm.addAction(self.t("report_bug"), self._report_bug)
        hm.addSeparator()
        hm.addAction(self.t("check_updates"), self._check_updates_manual)
        hm.addSeparator()
        hm.addAction(self.t("create_shortcut"),
                      lambda: self._create_shortcut_from_menu())

        lm = self.menu.addMenu(self.t("language"))
        lm.addAction("Français", lambda: self._set_lang("fr"))
        lm.addAction("English", lambda: self._set_lang("en"))

        # Update button texts
        self.btn_open_cat.setText(self.t("open_catalog"))
        self.btn_new_part.setText(self.t("new_part"))
        self.btn_fits.setText(self.t("fits_btn"))
        self.lbl_target.setText(self.t("target_bf"))
        self.lbl_notes.setText(self.t("notes"))
        for key in ("add_to_stack", "remove_from_stack", "move_up", "move_down",
                     "flip_piece", "mark_bf_start", "mark_bf_end", "auto_suggest",
                     "auto_complete", "insert_ghost", "resolve_ghosts"):
            btn = getattr(self, f"btn_{key}", None)
            if btn: btn.setText(self.t(key))
        # Update tooltips
        for w, en, fr in self._tooltips:
            try: w.setToolTip(fr if self.lang == "fr" else en)
            except RuntimeError: pass
        self._refresh_stack()

    def _create_shortcut_from_menu(self):
        try:
            from shortcut_helper import create_shortcut_force
            create_shortcut_force("Backfocus Calculator", "backfocus.py", "backfocus.ico")
        except ImportError:
            pass

    def _set_unit(self, key, val):
        self.data[key] = val; self._save(); self._refresh_stack()
        if self._catalog_win and self._catalog_win.isVisible():
            self._catalog_win._refresh()

    def _about(self):
        QMessageBox.information(self, self.t("about"),
            f"Backfocus Calculator v{VERSION}\n\n"
            f"Reference database: {len(REFERENCE_DB)} products\n"
            f"User parts: {len(self.data['parts'])}\n"
            f"Configurations: {len(self.data['configurations'])}\n\n"
            "Dark space theme · Galaxy cursor\n"
            "Bilingual EN/FR · PyQt6")

    # ── crash detection ──
    def _check_crash_on_startup(self):
        if not os.path.exists(_CRASH_FILE):
            return
        try:
            with open(_CRASH_FILE, "r", encoding="utf-8") as f:
                crash_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            try: os.remove(_CRASH_FILE)
            except OSError: pass
            return
        r = QMessageBox.question(self, self.t("crash_detected"),
                self.t("crash_report_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        try: os.remove(_CRASH_FILE)
        except OSError: pass
        if r == QMessageBox.StandardButton.Yes:
            self._send_crash_report(crash_data)

    def _send_crash_report(self, crash_data):
        import urllib.parse, webbrowser
        error_type = _anonymize_path(crash_data.get("error_type", "Unknown"))
        error_msg = _anonymize_path(crash_data.get("error_msg", ""))
        tb = _anonymize_path(crash_data.get("traceback", ""))
        title = f"[Crash] {error_type}: {error_msg}"
        if len(title) > 120: title = title[:117] + "..."
        recent = _anonymize_path(_get_recent_errors(10))
        recent_section = f"## Recent Errors\n\n```\n{recent}\n```\n\n" if recent else ""
        body = (
            f"## Crash Report\n\n**{error_type}:** {error_msg}\n\n"
            f"### Traceback\n\n```\n{tb}```\n\n"
            f"### System Info\n\n"
            f"- **Backfocus Calculator:** v{crash_data.get('version', '?')}\n"
            f"- **OS:** {crash_data.get('os', '?')}\n"
            f"- **Python:** {crash_data.get('python', '?')}\n"
            f"- **Architecture:** {crash_data.get('arch', '?')}\n"
            f"- **Qt:** {crash_data.get('qt', '?')}\n\n"
            f"{recent_section}*Auto-generated crash report*\n")
        params = urllib.parse.urlencode(
            {'title': title, 'body': body, 'labels': 'auto-report,bug'})
        webbrowser.open(f"https://github.com/ARP273-ROSE/backfocus/issues/new?{params}")
        QMessageBox.information(self, self.t("crash_detected"), self.t("crash_report_sent"))

    def _report_bug(self):
        import platform, urllib.parse, webbrowser
        from PyQt6.QtCore import PYQT_VERSION_STR
        try:
            qt_ver = PYQT_VERSION_STR
        except Exception:
            qt_ver = "?"
        sys_info = (
            f"- **Backfocus Calculator:** v{VERSION}\n"
            f"- **OS:** {platform.system()}\n"
            f"- **Python:** {platform.python_version()}\n"
            f"- **Architecture:** {platform.machine()}\n"
            f"- **Qt:** PyQt6 {qt_ver}\n")
        recent = _anonymize_path(_get_recent_errors(10))
        recent_section = f"## Recent Errors\n\n```\n{recent}\n```\n\n" if recent else ""
        body = (
            "## Description\n\n<!-- Describe the bug clearly -->\n\n\n"
            "## Steps to Reproduce\n\n1. \n2. \n3. \n\n"
            "## Expected Behavior\n\n\n\n## Actual Behavior\n\n\n\n"
            f"## System Info\n\n{sys_info}\n{recent_section}"
            "## Screenshots / Logs\n\n<!-- Paste any relevant screenshots or log output -->\n")
        params = urllib.parse.urlencode({'title': '[Bug] ', 'body': body, 'labels': 'bug'})
        webbrowser.open(f"https://github.com/ARP273-ROSE/backfocus/issues/new?{params}")

    # ── auto-update ──
    def _check_updates_startup(self):
        self._update_check_worker_start(silent=True)

    def _check_updates_manual(self):
        self._update_check_worker_start(silent=False)

    def _update_check_worker_start(self, silent):
        if self._update_thread and self._update_thread.is_alive():
            return
        while not self._update_queue.empty():
            self._update_queue.get_nowait()
        self._update_thread = threading.Thread(target=self._update_check_worker, daemon=True)
        self._update_thread.start()
        self._poll_update_check(silent)

    def _update_check_worker(self):
        self._update_queue.put(_check_for_update())

    def _poll_update_check(self, silent):
        try:
            result = self._update_queue.get_nowait()
        except queue.Empty:
            QTimer.singleShot(200, lambda: self._poll_update_check(silent))
            return
        if isinstance(result, dict):
            self._show_update_dialog(result)
        elif not silent:
            if result == "up_to_date":
                QMessageBox.information(self, self.t("help_menu"),
                                        self.t("update_up_to_date", version=VERSION))
            else:
                QMessageBox.warning(self, self.t("help_menu"),
                                    self.t("update_no_connection"))

    def _show_update_dialog(self, info):
        dlg = QDialog(self); dlg.setWindowTitle(self.t("update_title"))
        dlg.resize(520, 400); dlg.setStyleSheet(f"background: #1a1a2e;")
        vl = QVBoxLayout(dlg)
        lbl_avail = QLabel(self.t("update_available"))
        lbl_avail.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4fc3f7;")
        lbl_avail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(lbl_avail)
        vl.addWidget(QLabel(self.t("update_current", current=VERSION)))
        lbl_new = QLabel(self.t("update_new", new=info["version"]))
        lbl_new.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        vl.addWidget(lbl_new)
        vl.addWidget(QLabel(self.t("update_changelog")))
        tb = QTextBrowser()
        tb.setStyleSheet(f"background: #0f0f23; color: #e0e0e0; border: none;")
        tb.setPlainText(info.get("body", ""))
        vl.addWidget(tb)
        bf = QHBoxLayout()
        dl_btn = QPushButton(self.t("update_download"))
        dl_btn.setStyleSheet("background: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        dl_btn.clicked.connect(lambda: (dlg.accept(), self._do_update(info)))
        skip_btn = QPushButton(self.t("update_skip"))
        skip_btn.setStyleSheet("background: #444; color: white; padding: 8px;")
        skip_btn.clicked.connect(dlg.reject)
        bf.addWidget(dl_btn); bf.addWidget(skip_btn)
        vl.addLayout(bf)
        _center_dlg(dlg, self); dlg.exec()

    def _do_update(self, info):
        dlg = QDialog(self); dlg.setWindowTitle(self.t("update_downloading"))
        dlg.resize(340, 120); dlg.setStyleSheet("background: #1a1a2e;")
        vl = QVBoxLayout(dlg)
        self._update_lbl = QLabel(self.t("update_downloading"))
        self._update_lbl.setStyleSheet("color: #e0e0e0;")
        vl.addWidget(self._update_lbl)
        pb = QProgressBar(); pb.setRange(0, 0)  # indeterminate
        vl.addWidget(pb)
        self._update_dlg = dlg
        while not self._update_dl_queue.empty():
            self._update_dl_queue.get_nowait()
        self._update_dl_thread = threading.Thread(
            target=self._update_download_worker, args=(info["zipball_url"],), daemon=True)
        self._update_dl_thread.start()
        self._poll_update_download()
        _center_dlg(dlg, self); dlg.exec()

    def _update_download_worker(self, url):
        try:
            _download_and_apply_update(url)
            self._update_dl_queue.put(None)
        except Exception as e:
            self._update_dl_queue.put(str(e))

    def _poll_update_download(self):
        try:
            error = self._update_dl_queue.get_nowait()
        except queue.Empty:
            QTimer.singleShot(200, self._poll_update_download)
            return
        if error:
            self._update_dlg.accept()
            QMessageBox.critical(self, self.t("help_menu"),
                                 self.t("update_error", err=error))
        else:
            self._update_lbl.setText(self.t("update_restarting"))
            QTimer.singleShot(600, self._restart_app)

    def _restart_app(self):
        _save_writer.flush_sync()
        save_data(self.data, sync=True)
        self.galaxy.stop()
        self.close()
        import subprocess
        if sys.platform == "win32":
            subprocess.Popen([sys.executable] + sys.argv)
            sys.exit(0)
        else:
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except OSError:
                subprocess.Popen([sys.executable] + sys.argv)
                sys.exit(0)

    # ── splitter save/restore ──
    def _restore_splitter_positions(self):
        ui = self.data.get("ui", {})
        sh = ui.get("sash_h")
        if sh is not None:
            total = sum(self.splitter_h.sizes())
            if total > 0:
                self.splitter_h.setSizes([int(sh), total - int(sh)])
        sv = ui.get("sash_v")
        if sv is not None:
            total = sum(self.splitter_v.sizes())
            if total > 0:
                self.splitter_v.setSizes([int(sv), total - int(sv)])

    def _save_ui_state(self):
        ui = self.data.setdefault("ui", {})
        ui["window_geometry"] = f"{self.width()}x{self.height()}+{self.x()}+{self.y()}"
        sizes_h = self.splitter_h.sizes()
        if sizes_h: ui["sash_h"] = sizes_h[0]
        sizes_v = self.splitter_v.sizes()
        if sizes_v: ui["sash_v"] = sizes_v[0]

    # ── drag-and-drop from catalog ──
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        try:
            idx = int(event.mimeData().text())
            self._handle_catalog_drop(idx)
        except (ValueError, IndexError):
            pass

    # ── close ──
    def closeEvent(self, event):
        self._save_timer.stop()
        self._save_ui_state()
        _save_writer.flush_sync()
        save_data(self.data, sync=True)
        self.galaxy.stop()
        event.accept()


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def main():
    sys.excepthook = _global_exception_handler
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    pass

    app = QApplication(sys.argv)
    app.setStyleSheet(_build_stylesheet())

    # App icon (works with PyInstaller frozen exe)
    _ico_path = _resource_path("backfocus.ico")
    _png_path = _resource_path("backfocus.png")
    icon = QIcon()
    if os.path.exists(_ico_path):
        icon.addFile(_ico_path)
    if os.path.exists(_png_path):
        icon.addFile(_png_path)
    if not icon.isNull():
        app.setWindowIcon(icon)

    window = App()
    window.show()
    window.raise_()
    window.activateWindow()

    # Shortcut helper (after window is shown)
    try:
        from shortcut_helper import offer_shortcut
        def _get_cfg(key):
            return window.data.get("ui", {}).get(key)
        def _set_cfg(key, val):
            window.data.setdefault("ui", {})[key] = val
            window._save()
        offer_shortcut("Backfocus Calculator", "backfocus.py", "backfocus.ico",
                        _get_cfg, _set_cfg)
    except ImportError:
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
