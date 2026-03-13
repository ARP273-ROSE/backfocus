#!/usr/bin/env python3
"""
Backfocus Calculator v1 – Bilingual (EN/FR) cross-platform application.
Dark space/cosmos theme · 12 000+ reference DB · Galaxy cursor.
Light convention: Telescope (left) → Camera (right).
"""

# Windows: set AppUserModelID before any GUI import so taskbar uses our icon
import sys
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ARP273.BackfocusCalculator.1")
    except (AttributeError, OSError):
        pass

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, sys, copy, itertools, math, random, bisect, threading, queue

VERSION = "1.4.0"

# ═══════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════
TR = {
    "app_title":         {"en": "Backfocus Calculator", "fr": "Calculateur de Backfocus"},
    # ── menus ──
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
    # ── parts ──
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
    # ── types ──
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
    # ── actions ──
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
    # ── filters ──
    "filter_all":        {"en": "All", "fr": "Tous"},
    "filter_brand":      {"en": "Brand", "fr": "Marque"},
    "filter_type":       {"en": "Type", "fr": "Type"},
    "filter_thread":     {"en": "Thread", "fr": "Filetage"},
    "filter_diameter":   {"en": "Diameter", "fr": "Diamètre"},
    "filter_gender":     {"en": "Gender", "fr": "Genre"},
    "filter_owned":      {"en": "Owned only", "fr": "Possédés"},
    "search":            {"en": "Search…", "fr": "Rechercher…"},
    "reset_filters":     {"en": "Reset", "fr": "Réinit."},
    # ── config / calc ──
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
    # ── conflict / suggest ──
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
    # ── drag & drop ──
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
    # ── auto-update ──
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
    # ── crash report ──
    "crash_detected":    {"en": "Crash Detected", "fr": "Crash détecté"},
    "crash_report_msg":  {"en": "The application crashed during the last session.\n\nWould you like to send an anonymous bug report?",
                          "fr": "L'application a planté lors de la dernière session.\n\nVoulez-vous envoyer un rapport de bug anonyme ?"},
    "crash_report_send": {"en": "Send Report", "fr": "Envoyer le rapport"},
    "crash_report_skip": {"en": "Skip", "fr": "Ignorer"},
    "crash_report_sent": {"en": "Bug report opened in your browser.\nPlease click 'Submit' to send it.",
                          "fr": "Rapport de bug ouvert dans votre navigateur.\nCliquez sur 'Submit' pour l'envoyer."},
    "error_log":         {"en": "Error Log", "fr": "Journal d'erreurs"},
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

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backfocus_data.json")
_CRASH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_crash_report.json")
_ERROR_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backfocus_errors.log")

# ── Reference DB ──
try:
    from reference_data import REFERENCE_DB
except ImportError:
    REFERENCE_DB = []

# ── FITS Analyzer (optional) ──
try:
    from fits_analyzer import FITSAnalyzerWindow
    _HAS_FITS_ANALYZER = True
except ImportError:
    _HAS_FITS_ANALYZER = False

# ── Pre-built index for fast auto-fill lookup ──
_REF_INDEX = {}  # {lowercase_key: ref_entry}
_REF_BRANDS = set()
for _ref in REFERENCE_DB:
    _key = (_ref.get("brand","") + " " + _ref.get("name","")).lower().strip()
    _REF_INDEX[_key] = _ref
    _REF_BRANDS.add(_ref.get("brand",""))
_REF_KEYS_SORTED = sorted(_REF_INDEX.keys())  # for binary search prefix matching

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
    """Center a dialog on its parent, without visible flash."""
    dlg.withdraw()            # hide before computing position
    dlg.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    dw, dh = dlg.winfo_width(), dlg.winfo_height()
    x = px + (pw - dw) // 2
    y = py + (ph - dh) // 2
    dlg.geometry(f"+{max(0,x)}+{max(0,y)}")
    dlg.deiconify()           # show at final position

def _bind_dlg_keys(dlg, ok_func=None):
    """Bind Escape to close and Enter to confirm on a dialog."""
    dlg.bind("<Escape>", lambda _: dlg.destroy())
    if ok_func:
        dlg.bind("<Return>", lambda _: ok_func())

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
        try:
            messagebox.showerror("Save Error", f"Could not save data:\n{e}")
        except Exception:
            pass

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
        """Serialize JSON in caller thread, queue I/O for background."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        # Replace any pending write with the latest version
        try:
            self._queue.get_nowait()
        except queue.Empty:
            pass
        self._queue.put(json_str)

    def flush_sync(self):
        """Block until all pending writes are done."""
        self._done.wait(timeout=5)

_save_writer = _AsyncSaveWriter()

def save_data(data, sync=False):
    """Save data to disk. sync=True blocks until done (use for close/restart)."""
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
    "README.md", ".gitattributes", ".gitignore",
}
_UPDATE_DIR_WHITELIST = {"manual"}

def _parse_version(tag):
    """Parse 'v1.2.3' or '1.2.3' into (1, 2, 3) tuple for comparison."""
    s = tag.strip().lstrip("vV")
    parts = []
    for p in s.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)

def _check_for_update():
    """Check GitHub for a newer release. Returns dict, 'up_to_date', or None."""
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
    except urllib.request.HTTPError as e:
        if e.code == 404:
            return "up_to_date"
        return None
    except (OSError, ValueError, KeyError, TypeError):
        return None

_MAX_UPDATE_SIZE = 50 * 1024 * 1024  # 50 MB

def _download_and_apply_update(zipball_url):
    """Download zipball, extract whitelisted files over the install directory."""
    import urllib.request, zipfile, tempfile, shutil
    app_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_zip = os.path.join(tempfile.mkdtemp(prefix="backfocus_"), "update.zip")
    tmp_dir = tempfile.mkdtemp(prefix="backfocus_extract_")
    try:
        # download with size limit
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
        # validate zip entries before extraction (path traversal + symlink protection)
        real_tmp = os.path.realpath(tmp_dir)
        with zipfile.ZipFile(tmp_zip) as zf:
            for info in zf.infolist():
                if info.filename.startswith('/') or '..' in info.filename:
                    raise ValueError(f"Unsafe zip entry: {info.filename}")
                target = os.path.realpath(os.path.join(tmp_dir, info.filename))
                if not target.startswith(real_tmp + os.sep) and target != real_tmp:
                    raise ValueError(f"Zip path traversal: {info.filename}")
                # reject symlinks (external_attr >> 16 gives Unix mode; 0o120000 = symlink)
                if info.external_attr and (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f"Symlink in zip: {info.filename}")
            zf.extractall(tmp_dir)
        # find the single sub-folder GitHub creates (e.g. ARP273-ROSE-backfocus-abc1234/)
        entries = os.listdir(tmp_dir)
        src_root = os.path.join(tmp_dir, entries[0]) if len(entries) == 1 else tmp_dir
        # copy whitelisted files (skip symlinks)
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
        # cleanup
        parent_zip = os.path.dirname(tmp_zip)
        if os.path.isdir(parent_zip):
            shutil.rmtree(parent_zip, ignore_errors=True)
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

def _merge_reference_db(data):
    """Merge missing REFERENCE_DB entries, update specs, purge removed entries."""
    by_key = {}
    for i, p in enumerate(data["parts"]):
        by_key[(p.get("brand",""), p.get("name",""))] = i
    added = 0
    # Spec fields that get updated from reference (qty/notes preserved)
    SPEC_FIELDS = ("type","optical_length","mass","tside_thread","tside_gender",
                   "cside_thread","cside_gender","reversible","bf_role")
    ref_keys = set()
    for ref in REFERENCE_DB:
        key = (ref.get("brand",""), ref.get("name",""))
        ref_keys.add(key)
        if key in by_key:
            # Update specs from reference (keeps user's qty, notes)
            p = data["parts"][by_key[key]]
            for f in SPEC_FIELDS:
                if f in ref:
                    p[f] = ref[f]
        else:
            data["parts"].append(dict(ref, qty=0))
            added += 1
    # Purge entries removed from reference DB (keep user-created parts with qty>0)
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
    """Parse string to int, return default if invalid."""
    try:
        return int(s)
    except (ValueError, TypeError):
        return default

# ═══════════════════════════════════════════════════════════════════
#  ERROR LOGGING & CRASH CAPTURE
# ═══════════════════════════════════════════════════════════════════
_MAX_ERROR_LOG_BYTES = 100 * 1024  # 100 KB

def _log_error(msg):
    """Append a timestamped line to the error log. Never raises."""
    try:
        from datetime import datetime
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n"
        # Rotation: if log exceeds limit, keep last half
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
    """sys.excepthook replacement — logs crash and saves report file."""
    import traceback
    from datetime import datetime
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    _log_error(f"CRASH: {exc_type.__name__}: {exc_value}\n{tb_str}")
    try:
        crash = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "version": VERSION,
            "os": f"{_platform.system()} {_platform.version()}",
            "python": _platform.python_version(),
            "arch": _platform.machine(),
            "tk": str(tk.TkVersion),
            "error_type": exc_type.__name__,
            "error_msg": str(exc_value),
            "traceback": tb_str,
        }
        with open(_CRASH_FILE, "w", encoding="utf-8") as f:
            json.dump(crash, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

def _get_recent_errors(n=10):
    """Return the last n lines from the error log, or empty string."""
    try:
        if not os.path.exists(_ERROR_LOG):
            return ""
        with open(_ERROR_LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:]).strip()
    except OSError:
        return ""

# ═══════════════════════════════════════════════════════════════════
#  TOOLTIP
# ═══════════════════════════════════════════════════════════════════
class Tooltip:
    DELAY = 550
    def __init__(self, widget, text_en, text_fr=None, app=None):
        self.widget, self.en, self.fr = widget, text_en, text_fr or text_en
        self.app, self.tip, self._id = app, None, None
        widget.bind("<Enter>", self._sched, add="+")
        widget.bind("<Leave>", self._cancel, add="+")
    def _sched(self, _e):
        self._cancel(None)
        self._id = self.widget.after(self.DELAY, self._show)
    def _cancel(self, _e):
        if self._id:
            self.widget.after_cancel(self._id); self._id = None
        if self.tip:
            self.tip.destroy(); self.tip = None
    def _show(self):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        try: self.tip.attributes("-topmost", True)
        except tk.TclError: pass
        txt = self.fr if self.app and self.app.lang == "fr" else self.en
        lbl = tk.Label(self.tip, text=txt, bg=C["bg_hover"], fg=C["fg_bright"],
                       font=(FONT_FAMILY, 8), wraplength=340, padx=8, pady=5,
                       justify=tk.LEFT, relief="solid", bd=1)
        lbl.pack(); self.tip.geometry(f"+{x}+{y}")

# ═══════════════════════════════════════════════════════════════════
#  GALAXY CURSOR
# ═══════════════════════════════════════════════════════════════════
class GalaxyCursor:
    SIZE = 22
    POLL_MS = 33   # ~30 fps – plenty smooth for decorative cursor, halves Tcl overhead
    OFFSET = 20    # distance from pointer so galaxy doesn't overlap cursor
    LERP = 0.45    # slightly faster to compensate for lower poll rate
    def __init__(self, root):
        self.root = root
        self._paused = False
        self._stopped = False
        self._cur_x = 0.0   # current rendered position (float for smooth lerp)
        self._cur_y = 0.0
        self._last_ix = -1  # last rendered integer position (for skip-if-unchanged)
        self._last_iy = -1
        self.win = tk.Toplevel(root); self.win.overrideredirect(True)
        try: self.win.attributes("-topmost", True)
        except tk.TclError: pass
        trans = "#010101"; self.win.configure(bg=trans)
        self.canvas = tk.Canvas(self.win, width=self.SIZE, height=self.SIZE,
                                bg=trans, highlightthickness=0, bd=0)
        self.canvas.pack()
        if sys.platform == "win32":
            try:
                self.win.attributes("-transparentcolor", trans)
                self.win.wm_attributes("-disabled", True)
            except tk.TclError:
                self.win.attributes("-alpha", 0.7)
        else:
            try: self.win.attributes("-alpha", 0.7)
            except tk.TclError: pass
        self._draw()
        self.win.geometry(f"{self.SIZE}x{self.SIZE}+0+0")
        # Use polling timer so galaxy follows mouse across ALL windows
        self._poll()

    def pause(self):
        self._paused = True
        try: self.win.withdraw()
        except tk.TclError: pass

    def resume(self):
        self._paused = False
        try: self.win.deiconify()
        except tk.TclError: pass

    def _draw(self):
        S = self.SIZE; cx, cy = S/2, S/2
        c = self.canvas; rng = random.Random(42)
        # Pixel-art style: use PhotoImage for sharp 1px dots
        self._img = img = tk.PhotoImage(master=self.root, width=S, height=S)
        # Fill transparent
        row = "{" + " ".join(["#010101"]*S) + "}"
        img.put(" ".join([row]*S), to=(0,0))

        def px(x, y, col):
            ix, iy = int(round(x)), int(round(y))
            if 0 <= ix < S and 0 <= iy < S:
                img.put(col, to=(ix, iy))

        # Bulge: 3x3 warm core
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                px(cx+dx, cy+dy, "#3A2A10")
        px(cx, cy, "#C8B060")      # bright nucleus
        px(cx-1, cy, "#786028")
        px(cx+1, cy, "#786028")
        px(cx, cy-1, "#786028")
        px(cx, cy+1, "#786028")

        # Two spiral arms: sharp 1px dots, yellow core → blue-white outer
        arm_pal = ["#B09848","#90A0B0","#78A0C8","#60A0D8","#5098D0"]
        for off in (0, math.pi):
            for i in range(40):
                f = i/40; t = f*2.2*math.pi + off; r2 = 1.8 + f*8.5
                x = cx + r2*math.cos(t); y = cy + r2*math.sin(t)
                ci = min(int(f*len(arm_pal)), len(arm_pal)-1)
                px(x, y, arm_pal[ci])
                # Occasional brighter knot along arm
                if rng.random() < .15:
                    dx, dy2 = rng.choice([-1,0,1]), rng.choice([-1,0,1])
                    px(x+dx, y+dy2, "#88B0D0")

        # Field stars: single bright pixels
        for _ in range(4):
            x, y = rng.uniform(1,S-1), rng.uniform(1,S-1)
            if (x-cx)**2+(y-cy)**2 > 35:
                px(x, y, "#A8B8D0")

        c.create_image(0, 0, image=img, anchor="nw")

    def stop(self):
        self._stopped = True

    def _poll(self):
        if self._stopped:
            return
        if not self._paused:
            try:
                tx = self.root.winfo_pointerx() + self.OFFSET
                ty = self.root.winfo_pointery() + self.OFFSET
                # Smooth interpolation toward target
                self._cur_x += (tx - self._cur_x) * self.LERP
                self._cur_y += (ty - self._cur_y) * self.LERP
                ix, iy = int(self._cur_x), int(self._cur_y)
                # Skip geometry update if rendered position unchanged
                if ix != self._last_ix or iy != self._last_iy:
                    self._last_ix = ix
                    self._last_iy = iy
                    self.win.geometry(f"+{ix}+{iy}")
            except Exception:
                pass
        try:
            self.root.after(self.POLL_MS, self._poll)
        except tk.TclError:
            pass

# ═══════════════════════════════════════════════════════════════════
#  HELP WINDOW
# ═══════════════════════════════════════════════════════════════════
def open_help(parent, lang="en"):
    w = tk.Toplevel(parent); w.title("User Guide" if lang=="en" else "Guide d'utilisation")
    w.geometry("920x720"); w.configure(bg=C["bg_mid"])
    fr = ttk.Frame(w); fr.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    txt = tk.Text(fr, wrap=tk.WORD, bg=C["bg_dark"], fg=C["fg_main"],
                  font=(FONT_FAMILY,10), padx=20, pady=15, insertbackground=C["fg_main"],
                  highlightthickness=0, relief="flat")
    sb = ttk.Scrollbar(fr, orient=tk.VERTICAL, command=txt.yview)
    txt.configure(yscrollcommand=sb.set)
    txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.pack(side=tk.RIGHT, fill=tk.Y)
    for tag, cfg in [("h1",{"font":(FONT_FAMILY,16,"bold"),"foreground":C["accent_blue"],"spacing1":20,"spacing3":10}),
                     ("h2",{"font":(FONT_FAMILY,12,"bold"),"foreground":C["accent_teal"],"spacing1":15,"spacing3":8}),
                     ("h3",{"font":(FONT_FAMILY,10,"bold"),"foreground":C["accent_purple"],"spacing1":10,"spacing3":5}),
                     ("body",{"font":(FONT_FAMILY,10),"foreground":C["fg_main"],"spacing3":4}),
                     ("bullet",{"font":(FONT_FAMILY,10),"foreground":C["fg_main"],"lmargin1":30,"lmargin2":45}),
                     ("accent",{"foreground":C["accent_gold"]}),
                     ("key",{"font":(FONT_MONO,9),"foreground":C["accent_green"]})]:
        txt.tag_configure(tag, **cfg)
    def h(s,t="h1"): txt.insert(tk.END,s+"\n",t)
    def p(s,t="body"): txt.insert(tk.END,s+"\n\n",t)
    def b(s): txt.insert(tk.END,"  \u2022 "+s+"\n","bullet")

    if lang == "fr":
        h(f"Calculateur de Backfocus v{VERSION} \u2014 Guide complet")
        p("Bienvenue ! Cette application vous aide \u00e0 concevoir et v\u00e9rifier vos trains optiques pour l\u2019astrophotographie. Th\u00e8me sombre spatial, curseur galaxie, base de 12 000+ produits r\u00e9els.")

        h("1. D\u00e9marrage rapide","h2")
        b("Au premier lancement, la base de 12 000+ produits est charg\u00e9e automatiquement dans votre catalogue.")
        b("Toutes les donn\u00e9es sont sauvegard\u00e9es automatiquement \u00e0 chaque fermeture dans backfocus_data.json.")
        b("Utilisez le menu Langue pour passer de Fran\u00e7ais \u00e0 English \u00e0 tout moment.")

        h("2. Catalogue de pi\u00e8ces","h2")
        p("Ouvrez le catalogue via le menu Affichage > Catalogue de pi\u00e8ces ou le bouton dans la barre d\u2019outils. Il s\u2019ouvre dans une grande fen\u00eatre s\u00e9par\u00e9e.")
        h("Ajouter / Modifier une pi\u00e8ce","h3")
        b("Cliquez \u00ab Ajouter \u00bb et remplissez : Marque, Nom, Type (22 cat\u00e9gories), Longueur optique (mm), Masse (g).")
        b("Connexions : c\u00f4t\u00e9 t\u00e9lescope et c\u00f4t\u00e9 cam\u00e9ra, chacun avec filetage + genre (M\u00e2le/Femelle).")
        b("Cochez R\u00e9versible si la pi\u00e8ce peut \u00eatre retourn\u00e9e. D\u00e9finissez le R\u00f4le BF (start/end) si applicable.")
        b("Utilisez le bouton \u00ab Auto-fill \u00bb pour remplir tous les champs depuis la base de 12 000+ produits (125 marques).")
        b("Double-cliquez une pi\u00e8ce pour la modifier. Utilisez \u00ab Dupliquer \u00bb pour cr\u00e9er une copie.")
        h("Quantit\u00e9 poss\u00e9d\u00e9e","h3")
        b("Utilisez les boutons +/\u2212 pour ajuster rapidement la quantit\u00e9.")
        b("Les pi\u00e8ces poss\u00e9d\u00e9es (qt\u00e9 > 0) sont affich\u00e9es en dor\u00e9. Les autres sont gris\u00e9es.")
        h("Filtres et tri","h3")
        b("Barre de recherche : filtrez par texte (marque/nom).")
        b("Filtres combinables : type, diam\u00e8tre de filetage, genre (M/F), poss\u00e9d\u00e9es uniquement.")
        b("Cliquez sur les en-t\u00eates de colonnes pour trier par n\u2019importe quel crit\u00e8re (clic r\u00e9p\u00e9t\u00e9 = inverser).")
        b("Bouton \u00ab R\u00e9init. \u00bb pour effacer tous les filtres.")

        h("3. Configurations","h2")
        p("La fen\u00eatre principale est d\u00e9di\u00e9e aux configurations de trains optiques.")
        h("Cr\u00e9er une configuration","h3")
        b("Cliquez \u00ab + \u00bb pour cr\u00e9er une nouvelle configuration.")
        b("Donnez un nom (ex: \u00ab RC10 + ASI 6200 \u00bb) et un backfocus cible en mm (ex: 55).")
        b("Ajoutez des notes pour m\u00e9moriser des d\u00e9tails (champ Notes).")
        h("Construire le train optique","h3")
        b("Cliquez \u00ab Ajouter pi\u00e8ce \u00bb pour ins\u00e9rer une pi\u00e8ce de votre catalogue.")
        b("Le t\u00e9lescope est en haut (gauche), la cam\u00e9ra en bas (droite) \u2014 convention du chemin lumineux.")
        b("Utilisez Haut/Bas pour r\u00e9ordonner les pi\u00e8ces dans le train.")
        b("Utilisez \u00ab Retourner \u00bb pour inverser une pi\u00e8ce r\u00e9versible (\u00e9change T-side/C-side).")
        b("Utilisez \u00ab Retirer \u00bb pour enlever une pi\u00e8ce du train.")
        b("Dupliquer, Renommer ou Supprimer une configuration via les boutons du panneau gauche.")

        h("4. Pi\u00e8ces fant\u00f4mes","h2")
        p("Quand vous ajoutez une pi\u00e8ce dont les connexions sont incompatibles avec la pr\u00e9c\u00e9dente, l\u2019appli propose :")
        b("Retourner et ins\u00e9rer : retourne la pi\u00e8ce si elle est r\u00e9versible.")
        b("Ins\u00e9rer quand m\u00eame : ignore l\u2019incompatibilit\u00e9.")
        b("Ins\u00e9rer un fant\u00f4me : place un adaptateur fant\u00f4me (orange, \u00ab ? Adaptateur manquant \u00bb) entre les deux pi\u00e8ces.")
        b("Modifier la pi\u00e8ce : ouvre l\u2019\u00e9diteur pour corriger les connexions.")
        p("Le fant\u00f4me repr\u00e9sente une bague d\u2019adaptation \u00e0 trouver. Ses connexions sont d\u00e9duites des pi\u00e8ces voisines.")
        b("R\u00e9soudre : cliquez \u00ab R\u00e9soudre fant\u00f4mes \u00bb \u2192 l\u2019appli cherche les pi\u00e8ces compatibles dans votre catalogue.")
        b("La pi\u00e8ce choisie remplace le fant\u00f4me \u00e0 sa position exacte dans le train.")
        b("Vous pouvez aussi ins\u00e9rer un fant\u00f4me manuellement avec le bouton \u00ab Ins\u00e9rer fant\u00f4me \u00bb.")

        h("5. Zone de backfocus","h2")
        b("S\u00e9lectionnez la pi\u00e8ce o\u00f9 commence le BF (ex: r\u00e9ducteur) et cliquez \u00ab D\u00e9but BF \u00bb.")
        b("S\u00e9lectionnez la pi\u00e8ce o\u00f9 finit le BF (ex: cam\u00e9ra) et cliquez \u00ab Fin BF \u00bb.")
        b("Le BF calcul\u00e9 = somme des longueurs optiques apr\u00e8s le marqueur de d\u00e9but jusqu\u2019au marqueur de fin. La pi\u00e8ce de d\u00e9but sert de point z\u00e9ro (sa longueur n\u2019est pas compt\u00e9e).")
        b("L\u2019\u00e9cart est affich\u00e9 en couleur : vert (OK, < 0.1 mm), orange (court), rouge (long).")
        b("La zone BF est mise en surbrillance dans le tableau et le diagramme.")

        h("6. Suggestions & Auto-compl\u00e9tion","h2")
        h("Suggestion simple","h3")
        b("\u00ab Sugg\u00e9rer pi\u00e8ce \u00bb cherche UNE pi\u00e8ce poss\u00e9d\u00e9e qui comblerait l\u2019\u00e9cart.")
        b("V\u00e9rifie la compatibilit\u00e9 de connexion avec la derni\u00e8re pi\u00e8ce du train.")
        b("R\u00e9sultats tri\u00e9s par proximit\u00e9, correspondances parfaites en vert.")
        h("Auto-compl\u00e9tion combinatoire","h3")
        b("\u00ab Auto-compl\u00e9ter \u00bb cherche des combinaisons de 1, 2 ou 3 pi\u00e8ces poss\u00e9d\u00e9es.")
        b("Option pour autoriser/interdire les pi\u00e8ces d\u00e9j\u00e0 utilis\u00e9es dans d\u2019autres configs.")
        b("Double-cliquez ou cliquez \u00ab Ins\u00e9rer \u00bb pour appliquer la solution.")

        h("7. Compatibilit\u00e9 des connexions","h2")
        p("L\u2019application v\u00e9rifie automatiquement entre chaque paire de pi\u00e8ces adjacentes :")
        b("Le diam\u00e8tre de filetage doit correspondre (ex: M42 \u2194 M42).")
        b("Les genres doivent \u00eatre oppos\u00e9s (M\u00e2le \u2194 Femelle).")
        b("Les incompatibilit\u00e9s sont signal\u00e9es par \u00ab MISMATCH \u00bb en rouge.")
        h("Types de connexion support\u00e9s","h3")
        b("Filetages m\u00e9triques : M42/T2, M48, M54, M56, M63, M68, M72, M81, M82, M84, M92, M117.")
        b("Montures photo : EOS, Canon RF, Nikon F, Nikon Z, Sony E, Fuji X, MFT, Pentax K.")
        b("Coulants : 1.25\", 2\". Baril : CS. Ba\u00efonnette : SC (Schmidt-Cassegrain).")
        b("Fixations par vis : ZWO 6-bolt, ZWO 4-bolt, QHY 4-bolt.")

        h("8. Unit\u00e9s de mesure","h2")
        b("Menu Param\u00e8tres > Unit\u00e9s de mesure.")
        b("Longueurs : mm ou pouces. Masse : grammes ou onces.")
        b("Le changement s\u2019applique partout (catalogue + configurations).")

        h("9. Sauvegarde & Export","h2")
        h("Sauvegarde automatique","h3")
        b("Toutes les donn\u00e9es sont sauvegard\u00e9es automatiquement \u00e0 chaque fermeture.")
        b("Fichier : backfocus_data.json (m\u00eame r\u00e9pertoire que l\u2019application).")
        b("\u00ab Tout enregistrer \u00bb (menu Fichier) pour sauvegarder manuellement \u00e0 tout moment.")
        h("Export / Import de configuration","h3")
        b("\u00ab Exporter la configuration \u00bb : sauvegarde la config active en JSON.")
        b("\u00ab Importer la configuration \u00bb : charge une config depuis un fichier JSON.")
        h("Export / Import de toutes les donn\u00e9es","h3")
        b("\u00ab Exporter toutes les donn\u00e9es \u00bb : sauvegarde TOUT (pi\u00e8ces + configs + r\u00e9glages) en un seul fichier.")
        b("\u00ab Importer toutes les donn\u00e9es \u00bb : remplace toutes vos donn\u00e9es par un fichier export\u00e9 (avec confirmation).")
        b("Id\u00e9al pour transf\u00e9rer vos donn\u00e9es entre ordinateurs ou faire une sauvegarde compl\u00e8te.")

        h("10. Diagramme visuel","h2")
        b("Le diagramme en bas de l\u2019\u00e9cran repr\u00e9sente le train optique en couleurs.")
        b("Chaque couleur correspond \u00e0 un type de pi\u00e8ce (rouge = t\u00e9lescope, bleu = cam\u00e9ra, vert = r\u00e9ducteur, etc.).")
        b("La zone de backfocus est mise en surbrillance.")
        b("Une ligne pointill\u00e9e rouge indique la cible de backfocus.")

        h("11. Raccourcis clavier","h2")
        b("Entr\u00e9e : confirmer dans toutes les fen\u00eatres de dialogue.")
        b("\u00c9chap : fermer/annuler toutes les fen\u00eatres de dialogue.")
        b("Double-clic sur une pi\u00e8ce du catalogue : modifier.")
        b("Double-clic dans la liste de suggestions : ins\u00e9rer.")

        h("12. 22 types de pi\u00e8ces","h2")
        b("T\u00e9lescope, Lunette, Objectif photo, Cam\u00e9ra astro, Reflex/Hybride, Oculaire.")
        b("Barlow, R\u00e9ducteur, Aplanisseur, Extenseur, Correcteur de coma.")
        b("Roue \u00e0 filtres, Porte-filtre, OAG, Rotateur, Porte-oculaire, Renvoi coud\u00e9.")
        b("Bague d\u2019adaptation, Espaceur, Anti-tilt, Lunette guide, Miroir basculant.")

        h("13. Analyseur FITS / XISF de backfocus","h2")
        p("Ouvrez via le menu Affichage > Analyseur FITS / XISF de backfocus. Cet outil analyse une image astro pour diagnostiquer une erreur de backfocus \u00e0 partir du pattern d\u2019allongement des \u00e9toiles.")
        h("Formats support\u00e9s","h3")
        b("FITS : .fits, .fit, .fts (majuscules/minuscules)")
        b("FITS compress\u00e9 (fpack) : .fits.fz, .fit.fz")
        b("XISF (PixInsight) : .xisf")
        b("Images RGB automatiquement converties en luminance.")
        b("Images > 4096\u00d74096 automatiquement binn\u00e9es 2\u00d72.")
        h("Comment \u00e7a marche","h3")
        b("1. Cliquez Parcourir pour charger une image, puis Analyser.")
        b("2. L\u2019outil d\u00e9tecte les \u00e9toiles (DAOStarFinder), ajuste une gaussienne 2D elliptique sur chacune.")
        b("3. Carte FWHM : surface polynomiale du FWHM (plus gros au bord = erreur de BF).")
        b("4. Champ vectoriel : direction d\u2019allongement de chaque \u00e9toile, color\u00e9 radial (vert) vs tangentiel (orange).")
        b("5. Verdict : Correct (vert), Trop court (ajouter espaceurs), ou Trop long (retirer espaceurs).")
        h("Mosa\u00efque 3\u00d73","h3")
        b("L\u2019onglet Mosa\u00efque 3\u00d73 affiche 9 crops de l\u2019image (coins, bords, centre) avec les \u00e9toiles d\u00e9tect\u00e9es entour\u00e9es.")
        b("Chaque tuile indique le FWHM moyen et le nombre d\u2019\u00e9toiles. La bordure est color\u00e9e selon la qualit\u00e9 relative au centre :")
        b("Vert (\u22641.05\u00d7) = excellent, Teal (\u22641.20\u00d7) = bon, Orange (\u22641.40\u00d7) = moyen, Rouge (>1.40\u00d7) = mauvais.")
        b("Inspir\u00e9 de l\u2019Aberration Inspector d\u2019Ekos (KStars).")
        h("Interpr\u00e9tation","h3")
        b("Allongement radial (\u00e9toiles pointant vers le bord) \u2192 backfocus trop court.")
        b("Allongement tangentiel (\u00e9toiles en tourbillon) \u2192 backfocus trop long.")
        b("Note : l\u2019analyse mono-image donne la direction, pas l\u2019\u00e9cart pr\u00e9cis en mm.")

        h("14. Rapports de bugs et capture de crashs","h2")
        p("L\u2019application capture automatiquement les erreurs non g\u00e9r\u00e9es (crashs) et vous aide \u00e0 signaler les probl\u00e8mes.")
        h("Capture automatique","h3")
        b("Toute exception non g\u00e9r\u00e9e est enregistr\u00e9e dans un journal local (backfocus_errors.log).")
        b("Un fichier de rapport (_crash_report.json) est cr\u00e9\u00e9 avec le traceback et les infos syst\u00e8me.")
        b("Le journal est automatiquement tronqu\u00e9 s\u2019il d\u00e9passe 100 Ko.")
        h("D\u00e9tection au red\u00e9marrage","h3")
        b("Au prochain lancement, l\u2019appli d\u00e9tecte le crash et propose d\u2019envoyer un rapport.")
        b("\u00ab Envoyer \u00bb ouvre le navigateur avec une Issue GitHub pr\u00e9-remplie.")
        b("\u00ab Ignorer \u00bb supprime le rapport. Aucune donn\u00e9e n\u2019est envoy\u00e9e automatiquement.")
        h("Rapport manuel","h3")
        b("Menu Aide > Signaler un bug : ouvre un formulaire pr\u00e9-rempli avec les infos syst\u00e8me et les erreurs r\u00e9centes.")

        h("15. Performance et fluidit\u00e9 (v1.4)","h2")
        p("La version 1.4 am\u00e9liore significativement la fluidit\u00e9 de l\u2019interface :")
        b("Sauvegarde asynchrone : l\u2019\u00e9criture sur disque est d\u00e9port\u00e9e sur un thread d\u00e9di\u00e9, \u00e9liminant les micro-blocages de 50\u2013200 ms.")
        b("Curseur galaxie optimis\u00e9 : 30 fps au lieu de 60, skip si position inchang\u00e9e (\u223c50 % d\u2019appels Tcl en moins).")
        b("Quantit\u00e9s +/\u2212 rapides : seule la ligne modifi\u00e9e est mise \u00e0 jour, pas toute la liste.")
        b("Insertion par lots dans le catalogue : un seul redessin au lieu d\u2019un par \u00e9l\u00e9ment.")
        b("Cache de recherche pi\u00e8ces : index pr\u00e9-calcul\u00e9 pour 12 000+ pi\u00e8ces.")
        b("D\u00e9bouncing unifi\u00e9 : une seule minuterie de 300 ms pour toutes les sauvegardes.")

    else:
        h(f"Backfocus Calculator v{VERSION} \u2014 Complete Guide")
        p("Welcome! This application helps you design and verify optical trains for astrophotography. Dark space theme, galaxy cursor, 12,000+ real product database.")

        h("1. Quick Start","h2")
        b("On first launch, the 12,000+ product database is automatically loaded into your catalog.")
        b("All data is saved automatically on close to backfocus_data.json.")
        b("Use the Language menu to switch between English and Fran\u00e7ais at any time.")

        h("2. Parts Catalog","h2")
        p("Open the catalog via View > Parts Catalog or the toolbar button. It opens in a large separate window.")
        h("Adding / Editing a Part","h3")
        b("Click 'Add' and fill in: Brand, Name, Type (22 categories), Optical Length (mm), Mass (g).")
        b("Connections: telescope-side and camera-side, each with thread + gender (Male/Female).")
        b("Check Reversible if the part can be flipped. Set BF Role (start/end) if applicable.")
        b("Use the 'Auto-fill' button to populate all fields from the 12,000+ product database (125 brands).")
        b("Double-click a part to edit it. Use 'Duplicate' to create a copy.")
        h("Owned Quantity","h3")
        b("Use the +/\u2212 buttons to quickly adjust the owned quantity.")
        b("Owned parts (qty > 0) are displayed in gold. Others are dimmed.")
        h("Filters and Sorting","h3")
        b("Search bar: filter by text (brand/name).")
        b("Combinable filters: type, thread diameter, gender (M/F), owned only.")
        b("Click column headers to sort by any criterion (repeat click = reverse order).")
        b("'Reset' button to clear all filters.")

        h("3. Configurations","h2")
        p("The main window is dedicated to optical train configurations.")
        h("Creating a Configuration","h3")
        b("Click '+' to create a new configuration.")
        b("Give it a name (e.g., 'RC10 + ASI 6200') and a target backfocus in mm (e.g., 55).")
        b("Add notes to remember details (Notes field).")
        h("Building the Optical Train","h3")
        b("Click 'Add part' to insert a part from your catalog.")
        b("Telescope is at top (left), camera at bottom (right) \u2014 light path convention.")
        b("Use Up/Down to reorder parts in the train.")
        b("Use 'Flip' to reverse a reversible part (swaps T-side/C-side connections).")
        b("Use 'Remove' to take a part out of the train.")
        b("Duplicate, Rename, or Delete configurations via the left panel buttons.")

        h("4. Ghost Pieces","h2")
        p("When you add a part whose connections are incompatible with the previous one, the app offers:")
        b("Flip and insert: flips the part if it is reversible.")
        b("Insert anyway: ignores the incompatibility.")
        b("Insert placeholder: places a ghost adapter (orange, '? Missing adapter') between the two parts.")
        b("Edit part: opens the editor to fix connections.")
        p("The ghost represents an adapter ring you need to find. Its connections are inferred from neighboring parts.")
        b("Resolve: click 'Resolve ghosts' \u2192 the app searches your catalog for matching parts.")
        b("The chosen part replaces the ghost at its exact position in the train.")
        b("You can also insert a ghost manually with the 'Insert ghost' button.")

        h("5. Backfocus Zone","h2")
        b("Select the part where BF begins (e.g., reducer) and click 'Set BF start'.")
        b("Select the part where BF ends (e.g., camera) and click 'Set BF end'.")
        b("Calculated BF = sum of optical lengths after the start marker up to the end marker. The start piece is the zero point (its length is not counted).")
        b("Gap is color-coded: green (OK, < 0.1 mm), orange (short), red (long).")
        b("The BF zone is highlighted in both the table and the diagram.")

        h("6. Suggest & Auto-complete","h2")
        h("Simple Suggestion","h3")
        b("'Suggest part' finds ONE owned part that would fill the remaining gap.")
        b("Checks connection compatibility with the last part in the train.")
        b("Results sorted by proximity, perfect matches shown in green.")
        h("Combinatorial Auto-complete","h3")
        b("'Auto-complete' searches for combinations of 1, 2, or 3 owned parts.")
        b("Option to allow/disallow parts already used in other configurations.")
        b("Double-click or click 'Insert' to apply the solution.")

        h("7. Connection Compatibility","h2")
        p("The app automatically checks between each pair of adjacent parts:")
        b("Thread diameter must match (e.g., M42 \u2194 M42).")
        b("Genders must be opposite (Male \u2194 Female).")
        b("Incompatibilities are flagged as 'MISMATCH' in red.")
        h("Supported Connection Types","h3")
        b("Metric threads: M42/T2, M48, M54, M56, M63, M68, M72, M81, M82, M84, M92, M117.")
        b("Camera mounts: EOS, Canon RF, Nikon F, Nikon Z, Sony E, Fuji X, MFT, Pentax K.")
        b("Barrels: 1.25\", 2\". C-mount: CS. Bayonet: SC (Schmidt-Cassegrain).")
        b("Bolt mounts: ZWO 6-bolt, ZWO 4-bolt, QHY 4-bolt.")

        h("8. Measurement Units","h2")
        b("Settings > Measurement Units menu.")
        b("Lengths: mm or inches. Mass: grams or ounces.")
        b("The change applies everywhere (catalog + configurations).")

        h("9. Save & Export","h2")
        h("Automatic Save","h3")
        b("All data is saved automatically on close.")
        b("File: backfocus_data.json (same directory as the application).")
        b("'Save All' (File menu) to save manually at any time.")
        h("Configuration Export / Import","h3")
        b("'Export Configuration': saves the active config as JSON.")
        b("'Import Configuration': loads a config from a JSON file.")
        h("Full Data Export / Import","h3")
        b("'Export All Data': saves EVERYTHING (parts + configs + settings) in one file.")
        b("'Import All Data': replaces all your data with an exported file (with confirmation).")
        b("Ideal for transferring data between computers or making a complete backup.")

        h("10. Visual Diagram","h2")
        b("The diagram at the bottom represents the optical train in color.")
        b("Each color corresponds to a part type (red = telescope, blue = camera, green = reducer, etc.).")
        b("The backfocus zone is highlighted.")
        b("A dashed red line indicates the backfocus target.")

        h("11. Keyboard Shortcuts","h2")
        b("Enter: confirm in all dialog windows.")
        b("Escape: close/cancel all dialog windows.")
        b("Double-click a catalog part: edit it.")
        b("Double-click in suggestion list: insert the part.")

        h("12. 22 Part Types","h2")
        b("Telescope, Refractor, Camera Lens, Astro Camera, DSLR/Mirrorless, Eyepiece.")
        b("Barlow, Focal Reducer, Field Flattener, Focal Extender, Coma Corrector.")
        b("Filter Wheel, Filter Holder, OAG, Rotator, Focuser, Diagonal.")
        b("Adapter Ring, Spacer, Anti-tilt, Guide Scope, Flip Mirror.")

        h("13. FITS / XISF Backfocus Analyzer","h2")
        p("Open via View > FITS / XISF Backfocus Analyzer. This tool analyzes an astro image to diagnose backfocus error from the star elongation pattern.")
        h("Supported Formats","h3")
        b("FITS: .fits, .fit, .fts (case-insensitive)")
        b("Compressed FITS (fpack): .fits.fz, .fit.fz")
        b("XISF (PixInsight): .xisf")
        b("RGB images automatically converted to luminance.")
        b("Images > 4096\u00d74096 automatically binned 2\u00d72.")
        h("How It Works","h3")
        b("1. Click Browse to load an image, then Analyze.")
        b("2. The tool detects stars (DAOStarFinder), fits an elliptical 2D Gaussian on each one.")
        b("3. FWHM map: polynomial surface of FWHM (larger at edges = BF error).")
        b("4. Vector field: elongation direction of each star, colored radial (green) vs tangential (orange).")
        b("5. Verdict: Correct (green), Too short (add spacers), or Too long (remove spacers).")
        h("Mosaic 3\u00d73","h3")
        b("The Mosaic 3\u00d73 tab displays 9 image crops (corners, edges, center) with detected stars circled.")
        b("Each tile shows the mean FWHM and star count. The border is color-coded by quality relative to center:")
        b("Green (\u22641.05\u00d7) = excellent, Teal (\u22641.20\u00d7) = good, Orange (\u22641.40\u00d7) = fair, Red (>1.40\u00d7) = poor.")
        b("Inspired by the Ekos (KStars) Aberration Inspector.")
        h("Interpretation","h3")
        b("Radial elongation (stars pointing toward the edge) \u2192 backfocus too short.")
        b("Tangential elongation (swirl pattern) \u2192 backfocus too long.")
        b("Note: single-image analysis gives direction only, not a precise offset in mm.")

        h("14. Bug Reports & Crash Capture","h2")
        p("The application automatically captures unhandled errors (crashes) and helps you report issues.")
        h("Automatic Capture","h3")
        b("Any unhandled exception is logged to a local file (backfocus_errors.log).")
        b("A crash report file (_crash_report.json) is created with the traceback and system info.")
        b("The error log is automatically truncated if it exceeds 100 KB.")
        h("Detection on Restart","h3")
        b("On next launch, the app detects the crash and offers to send a report.")
        b("'Send Report' opens your browser with a pre-filled GitHub Issue.")
        b("'Skip' deletes the report. No data is sent automatically.")
        h("Manual Report","h3")
        b("Help > Report Bug: opens a pre-filled form with system info and recent errors.")

        h("15. Performance & Fluidity (v1.4)","h2")
        p("Version 1.4 significantly improves UI fluidity:")
        b("Async save: disk I/O offloaded to a dedicated thread, eliminating 50\u2013200 ms micro-freezes.")
        b("Galaxy cursor optimized: 30 fps instead of 60, skips if position unchanged (\u223c50% fewer Tcl calls).")
        b("Fast qty +/\u2212: only the affected row is updated, not the entire list.")
        b("Batch insert in catalog: single repaint instead of one per item.")
        b("Parts search cache: pre-built index for 12,000+ parts.")
        b("Unified debounce: single 300 ms timer for all saves.")
    txt.configure(state="disabled")

# ═══════════════════════════════════════════════════════════════════
#  PARTS CATALOG WINDOW
# ═══════════════════════════════════════════════════════════════════
class CatalogWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        self.win.title(app.t("catalog_title"))
        self.win.geometry("1450x860")
        self.win.configure(bg=C["bg_mid"])
        self.win.transient(app.root)
        self._sort_col = None
        self._sort_rev = False
        self._drag_data = None   # part index being dragged
        self._drag_win = None    # floating label during drag
        self._build()
        self._refresh()

    def _build(self):
        a = self.app
        lbl_kw = dict(foreground=C["fg_dim"], font=(FONT_FAMILY,7))

        # ── filter toolbar (labeled groups) ──
        tb = ttk.Frame(self.win); tb.pack(fill=tk.X, padx=8, pady=(6,2))

        # search
        sf = ttk.Frame(tb); sf.pack(side=tk.LEFT, padx=(0,8))
        ttk.Label(sf, text=a.t("search"), **lbl_kw).pack(anchor=tk.W)
        self._search_after = None
        self._sv = tk.StringVar(); self._sv.trace_add("write", lambda *_: self._debounced_refresh())
        self._se = ttk.Entry(sf, textvariable=self._sv, width=20)
        self._se.pack()

        # brand
        bf = ttk.Frame(tb); bf.pack(side=tk.LEFT, padx=3)
        ttk.Label(bf, text=a.t("filter_brand"), **lbl_kw).pack(anchor=tk.W)
        brands = sorted(_REF_BRANDS | {p.get("brand","") for p in a.data["parts"] if p.get("brand","")})
        self._fb = tk.StringVar(value=a.t("filter_all"))
        self._fbcb = ttk.Combobox(bf, textvariable=self._fb, state="readonly", width=14,
                                  values=[a.t("filter_all")] + brands)
        self._fbcb.pack()
        self._fbcb.bind("<<ComboboxSelected>>", lambda *_: self._refresh())

        # type
        tf = ttk.Frame(tb); tf.pack(side=tk.LEFT, padx=3)
        ttk.Label(tf, text=a.t("filter_type"), **lbl_kw).pack(anchor=tk.W)
        self._ft = tk.StringVar(value=a.t("filter_all"))
        self._ftcb = ttk.Combobox(tf, textvariable=self._ft, state="readonly", width=14,
                                  values=[a.t("filter_all")]+sorted([a._ttype(k) for k in PART_TYPES]))
        self._ftcb.pack()
        self._ftcb.bind("<<ComboboxSelected>>", lambda *_: self._refresh())

        # thread
        thf = ttk.Frame(tb); thf.pack(side=tk.LEFT, padx=3)
        ttk.Label(thf, text=a.t("filter_thread"), **lbl_kw).pack(anchor=tk.W)
        threads = [t for t in THREADS if t]  # exclude empty
        self._fth = tk.StringVar(value=a.t("filter_all"))
        self._fthcb = ttk.Combobox(thf, textvariable=self._fth, state="readonly", width=16,
                                   values=[a.t("filter_all")] + threads)
        self._fthcb.pack()
        self._fthcb.bind("<<ComboboxSelected>>", lambda *_: self._refresh())

        # diameter
        df = ttk.Frame(tb); df.pack(side=tk.LEFT, padx=3)
        ttk.Label(df, text=a.t("filter_diameter"), **lbl_kw).pack(anchor=tk.W)
        self._fd = tk.StringVar(value="All")
        self._fdcb = ttk.Combobox(df, textvariable=self._fd, values=DIAMETERS,
                                  state="readonly", width=7)
        self._fdcb.pack()
        self._fd.trace_add("write", lambda *_: self._debounced_refresh())

        # gender
        gf = ttk.Frame(tb); gf.pack(side=tk.LEFT, padx=3)
        ttk.Label(gf, text=a.t("filter_gender"), **lbl_kw).pack(anchor=tk.W)
        self._fg = tk.StringVar(value=a.t("gender_all"))
        self._fgcb = ttk.Combobox(gf, textvariable=self._fg, state="readonly", width=8,
                                  values=[a.t("gender_all"), a.t("gender_male"), a.t("gender_female")])
        self._fgcb.pack()
        self._fgcb.bind("<<ComboboxSelected>>", lambda *_: self._refresh())

        # optical length range
        olf = ttk.Frame(tb); olf.pack(side=tk.LEFT, padx=3)
        ttk.Label(olf, text=a.t("optical_length"), **lbl_kw).pack(anchor=tk.W)
        olr = ttk.Frame(olf); olr.pack()
        self._fol_min = tk.StringVar()
        self._fol_max = tk.StringVar()
        self._fol_min.trace_add("write", lambda *_: self._debounced_refresh())
        self._fol_max.trace_add("write", lambda *_: self._debounced_refresh())
        ttk.Entry(olr, textvariable=self._fol_min, width=5).pack(side=tk.LEFT)
        ttk.Label(olr, text="-").pack(side=tk.LEFT, padx=2)
        ttk.Entry(olr, textvariable=self._fol_max, width=5).pack(side=tk.LEFT)

        # owned + reset
        of = ttk.Frame(tb); of.pack(side=tk.LEFT, padx=(8,3))
        self._fo = tk.BooleanVar(value=False)
        self._fochk = ttk.Checkbutton(of, variable=self._fo, text=a.t("filter_owned"),
                                      command=self._refresh)
        self._fochk.pack(anchor=tk.W, pady=(10,0))
        ttk.Button(of, text=a.t("reset_filters"), command=self._reset,
                   style="Small.TButton").pack(anchor=tk.W, pady=(2,0))

        # ── action toolbar ──
        tb2 = ttk.Frame(self.win); tb2.pack(fill=tk.X, padx=8, pady=(0,4))
        btns = [
            ("add_part",    self._add,  "Accent.TButton", "Add a new part", "Ajouter une nouvelle pi\u00e8ce"),
            ("edit_part",   self._edit, "TButton",        "Edit selected part", "Modifier la pi\u00e8ce s\u00e9lectionn\u00e9e"),
            ("duplicate_part", self._dup, "TButton",      "Duplicate selected part", "Dupliquer la pi\u00e8ce s\u00e9lectionn\u00e9e"),
            ("delete_part", self._del,  "TButton",        "Delete selected part", "Supprimer la pi\u00e8ce s\u00e9lectionn\u00e9e"),
        ]
        for key, cmd, sty, tip_en, tip_fr in btns:
            b = ttk.Button(tb2, text=a.t(key), command=cmd, style=sty)
            b.pack(side=tk.LEFT, padx=2)
            Tooltip(b, tip_en, tip_fr, a)

        # separator
        ttk.Separator(tb2, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        # +/- qty
        ttk.Label(tb2, text=a.t("qty")+":").pack(side=tk.LEFT, padx=(0,4))
        b_minus = ttk.Button(tb2, text="\u2212", width=2, style="Small.TButton", command=self._qty_minus)
        b_minus.pack(side=tk.LEFT, padx=1)
        Tooltip(b_minus, "Decrease owned quantity", "Diminuer la quantit\u00e9 poss\u00e9d\u00e9e", a)
        b_plus = ttk.Button(tb2, text="+", width=2, style="Small.TButton", command=self._qty_plus)
        b_plus.pack(side=tk.LEFT, padx=1)
        Tooltip(b_plus, "Increase owned quantity", "Augmenter la quantit\u00e9 poss\u00e9d\u00e9e", a)

        # ── treeview ──
        cols = ("brand","name","type","mm","mass","t_thread","t_g","c_thread","c_g","rev","bf","qty","notes")
        self.tree = ttk.Treeview(self.win, columns=cols, show="headings", selectmode="browse")
        hdrs = [("brand", a.t("part_brand"), 90), ("name", a.t("part_name"), 220),
                ("type", a.t("part_type"), 115), ("mm", "mm", 58),
                ("mass", "g", 50), ("t_thread", a.t("tside"), 100),
                ("t_g", "", 55), ("c_thread", a.t("cside"), 100),
                ("c_g", "", 55), ("rev", a.t("reversible"), 55),
                ("bf", a.t("bf_role"), 60), ("qty", a.t("qty"), 42),
                ("notes", a.t("part_notes"), 140)]
        for cid, txt, w in hdrs:
            self.tree.heading(cid, text=txt, command=lambda c=cid: self._sort(c))
            self.tree.column(cid, width=w, anchor=tk.CENTER if w < 100 else tk.W)

        self.tree.tag_configure("owned",    foreground=C["accent_gold"])
        self.tree.tag_configure("notowned", foreground=C["notowned_fg"])
        self.tree.tag_configure("odd",      background=C["tree_odd"])
        self.tree.tag_configure("even",     background=C["tree_even"])

        sb = ttk.Scrollbar(self.win, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,0), pady=(0,4))
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,8), pady=(0,4))
        self.tree.bind("<Double-1>", lambda _: self._edit())

        # ── drag-and-drop bindings ──
        self.tree.bind("<ButtonPress-1>", self._drag_start, add="+")
        self.tree.bind("<B1-Motion>", self._drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._drag_end)

        # ── status bar ──
        sf = ttk.Frame(self.win); sf.pack(fill=tk.X, padx=8, pady=(0,6))
        self._status = ttk.Label(sf, text="", style="Calc.TLabel")
        self._status.pack(side=tk.LEFT)
        self._drag_hint = ttk.Label(sf, text=self.app.t("drag_hint"),
                                    foreground=C["fg_dim"], font=(FONT_FAMILY,8))
        self._drag_hint.pack(side=tk.RIGHT, padx=(10,0))

    def _reset(self):
        all_ = self.app.t("filter_all")
        self._sv.set(""); self._fb.set(all_); self._ft.set(all_)
        self._fth.set(all_); self._fd.set("All")
        self._fg.set(self.app.t("gender_all"))
        self._fol_min.set(""); self._fol_max.set("")
        self._fo.set(False); self._refresh()

    _MAX_DISPLAY = 500

    def _debounced_refresh(self):
        if self._search_after:
            self.app.root.after_cancel(self._search_after)
        self._search_after = self.app.root.after(150, self._refresh)

    def _refresh(self):
        self._search_after = None
        self.tree.delete(*self.tree.get_children())
        lu = self.app.data.get("length_unit", "mm")
        mu = self.app.data.get("mass_unit", "g")
        # Pre-compute all filter values once (avoid re-reading tkinter vars per item)
        s = self._sv.get().lower()
        all_ = self.app.t("filter_all")
        fb = self._fb.get(); fb_active = fb != all_
        ft = self._ft.get(); ft_active = ft != all_
        fth = self._fth.get(); fth_active = fth != all_
        fd = self._fd.get(); fd_active = fd != "All"
        fg = self._fg.get()
        fg_active = fg != self.app.t("gender_all")
        fg_gen = ("Male" if fg == self.app.t("gender_male") else "Female") if fg_active else ""
        owned_only = self._fo.get()
        try: fol_min = float(self._fol_min.get().replace(",", "."))
        except ValueError: fol_min = None
        try: fol_max = float(self._fol_max.get().replace(",", "."))
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
                   "qty": lambda ip: ip[1].get("qty",0),
                   "t_thread": lambda ip: ip[1].get("tside_thread",""),
                   "c_thread": lambda ip: ip[1].get("cside_thread",""),
                   "bf": lambda ip: ip[1].get("bf_role",""),
                   "notes": lambda ip: ip[1].get("notes",""),}
        if self._sort_col:
            fn = key_map.get(self._sort_col)
            if fn:
                items.sort(key=fn, reverse=self._sort_rev)
        else:
            # Default sort: brand then name
            items.sort(key=lambda ip: (ip[1].get("brand","").lower(),
                                       ip[1].get("name","").lower()))
        display = items[:self._MAX_DISPLAY]
        # Suppress visual updates during batch insert (hide columns, restore after)
        cols = self.tree["columns"]
        self.tree["displaycolumns"] = []
        _ttype = self.app._ttype
        row = 0
        for i, p in display:
            tags = ("odd" if row%2==0 else "even", "owned" if p.get("qty",0)>0 else "notowned")
            ol = p.get("optical_length",0)
            ms = p.get("mass",0)
            self.tree.insert("", tk.END, iid=str(i), values=(
                p.get("brand",""), p.get("name",""), _ttype(p.get("type","")),
                _fmt_len(ol,lu) if ol else "", _fmt_mass(ms,mu) if ms else "",
                p.get("tside_thread",""), p.get("tside_gender",""),
                p.get("cside_thread",""), p.get("cside_gender",""),
                "Y" if p.get("reversible") else "", p.get("bf_role",""),
                p.get("qty",0), p.get("notes","")[:40],
            ), tags=tags)
            row += 1
        self.tree["displaycolumns"] = list(cols)  # restore columns → single repaint
        if total_matched > self._MAX_DISPLAY:
            self._status.config(text=f"{self._MAX_DISPLAY} / {total_matched} " + self.app.t("total_parts", n=total_matched))
        else:
            self._status.config(text=self.app.t("total_parts", n=row))

    def _sort(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col; self._sort_rev = False
        self._refresh()

    def _sel_idx(self):
        s = self.tree.selection()
        return int(s[0]) if s else None

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
        if messagebox.askyesno(self.app.t("confirm_delete"), self.app.t("confirm_delete_msg", name=nm)):
            self.app.data["parts"].pop(i)
            self.app._save(); self._refresh()

    def _update_qty_row(self, idx):
        """Update a single Treeview row after qty change (avoids full rebuild)."""
        iid = str(idx)
        if not self.tree.exists(iid):
            return  # item not visible (filtered out)
        p = self.app.data["parts"][idx]
        lu = self.app.data.get("length_unit", "mm")
        mu = self.app.data.get("mass_unit", "g")
        ol = p.get("optical_length", 0)
        ms = p.get("mass", 0)
        self.tree.item(iid, values=(
            p.get("brand",""), p.get("name",""), self.app._ttype(p.get("type","")),
            _fmt_len(ol, lu) if ol else "", _fmt_mass(ms, mu) if ms else "",
            p.get("tside_thread",""), p.get("tside_gender",""),
            p.get("cside_thread",""), p.get("cside_gender",""),
            "Y" if p.get("reversible") else "", p.get("bf_role",""),
            p.get("qty", 0), p.get("notes","")[:40],
        ))
        # Update owned/notowned tag while preserving odd/even
        cur_tags = list(self.tree.item(iid, "tags") or ())
        new_tags = [t for t in cur_tags if t not in ("owned", "notowned")]
        new_tags.append("owned" if p.get("qty", 0) > 0 else "notowned")
        self.tree.item(iid, tags=tuple(new_tags))

    def _qty_plus(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        self.app.data["parts"][i]["qty"] = self.app.data["parts"][i].get("qty",0) + 1
        self.app._save(); self._update_qty_row(i)

    def _qty_minus(self):
        i = self._sel_idx()
        if i is None or i >= len(self.app.data["parts"]): return
        q = self.app.data["parts"][i].get("qty",0) - 1
        self.app.data["parts"][i]["qty"] = max(0, q)
        self.app._save()
        # If filter "owned only" is active and qty dropped to 0, need full refresh
        if max(0, q) == 0 and self._fo.get():
            self._refresh()
        else:
            self._update_qty_row(i)

    # ── drag-and-drop ──
    def _drag_start(self, event):
        """Record the part under cursor when drag begins."""
        item = self.tree.identify_row(event.y)
        if not item:
            self._drag_data = None; return
        self._drag_data = int(item)
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._drag_started = False  # only show floating after 5px movement

    def _drag_motion(self, event):
        """Move a floating label to follow the cursor during drag."""
        if self._drag_data is None: return
        # Threshold: require 5px of movement to distinguish drag from click
        if not self._drag_started:
            dx = abs(event.x - self._drag_start_x)
            dy = abs(event.y - self._drag_start_y)
            if dx < 5 and dy < 5: return
            self._drag_started = True
        p = self.app.data["parts"][self._drag_data]
        if self._drag_win is None:
            self._drag_win = tk.Toplevel(self.win)
            self._drag_win.overrideredirect(True)
            try: self._drag_win.attributes("-topmost", True)
            except tk.TclError: pass
            if sys.platform == "win32":
                try: self._drag_win.attributes("-alpha", 0.85)
                except tk.TclError: pass
            name = f'{p.get("brand","")} {p.get("name","")}'.strip()
            ptype = self.app._ttype(p.get("type",""))
            col = TYPE_COLORS.get(p.get("type",""), C["fg_dim"])
            fr = tk.Frame(self._drag_win, bg=col, padx=2, pady=2)
            fr.pack()
            tk.Label(fr, text=f"  {name}  ", bg=C["bg_light"], fg=C["fg_bright"],
                     font=(FONT_FAMILY,9,"bold"), padx=8, pady=4).pack()
            tk.Label(fr, text=f"{ptype} · {p.get('optical_length',0):.1f} mm",
                     bg=C["bg_light"], fg=C["fg_dim"], font=(FONT_FAMILY,7), padx=8, pady=1).pack()
        x = self.win.winfo_pointerx() + 16
        y = self.win.winfo_pointery() + 16
        self._drag_win.geometry(f"+{x}+{y}")

    def _drag_end(self, event):
        """On release, check if cursor is over the main window (anywhere)."""
        if self._drag_win:
            self._drag_win.destroy(); self._drag_win = None
        if self._drag_data is None or not self._drag_started:
            self._drag_data = None; return
        part_idx = self._drag_data
        self._drag_data = None
        # Detect drop target using absolute pointer coordinates
        px, py = self.win.winfo_pointerx(), self.win.winfo_pointery()
        target_widget = None
        try:
            target_widget = self.app.root.winfo_containing(px, py)
        except Exception:
            pass
        if target_widget is None: return
        # Accept drop anywhere inside the main application window
        w = target_widget
        on_main = False
        while w:
            if w is self.app.root:
                on_main = True; break
            try: w = w.master
            except Exception: break
        if not on_main: return
        self.app._handle_catalog_drop(part_idx)


# ═══════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root = root
        self.data = load_data()
        self.lang = self.data.get("language", "fr")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if not self.data["parts"]:
            self.data["parts"] = [dict(p, qty=0) for p in REFERENCE_DB]
            save_data(self.data)
        elif REFERENCE_DB:
            added, purged = _merge_reference_db(self.data)
            if added or purged:
                save_data(self.data)
        self._catalog_win = None
        self._fits_win = None
        self._pending_save = None
        self._parts_search_cache = None  # lazy-built search index for fast filtering
        self._apply_theme()
        self._build_ui()
        self._apply_language()
        self.galaxy = GalaxyCursor(self.root)
        self._win_resize_after = None
        self.root.bind("<Configure>", self._on_root_configure)
        self._update_thread = None
        self._update_queue = queue.Queue()
        self._update_dl_queue = queue.Queue()
        self.root.after(2000, self._check_updates_startup)
        self.root.after(3000, self._check_crash_on_startup)

    def _save(self):
        """Debounced save — coalesces rapid save_data calls into one write."""
        if hasattr(self, '_pending_save') and self._pending_save:
            self.root.after_cancel(self._pending_save)
        self._pending_save = self.root.after(300, self._flush_save)

    def _flush_save(self):
        self._pending_save = None
        self._parts_search_cache = None  # invalidate on data change
        save_data(self.data)

    def _get_parts_search_cache(self):
        """Return pre-built search index: [(idx, search_text_lower, part_dict), ...]"""
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
        Tooltip(w, en, fr, self)

    # ── Theme ──
    @staticmethod
    def _pill_img(root, w, h, r, fill_hex):
        """Create a rounded-rectangle PhotoImage (9-slice friendly)."""
        img = tk.PhotoImage(master=root, width=w, height=h)
        # Fill entire image with the color
        row = "{" + " ".join([fill_hex]*w) + "}"
        img.put(" ".join([row]*h), to=(0,0))
        # Make corner pixels transparent
        for y in range(h):
            for x in range(w):
                dx = max(0, r-x, x-(w-1-r))
                dy = max(0, r-y, y-(h-1-r))
                if dx*dx + dy*dy > r*r:
                    img.transparency_set(x, y, True)
        return img

    def _apply_theme(self):
        self.root.configure(bg=C["bg_dark"])
        s = ttk.Style()
        for th in ("clam","alt","default"):
            if th in s.theme_names(): s.theme_use(th); break

        # ── rounded button images (kept alive on self) ──
        R = 6  # corner radius
        SZ = R*2+4  # min image size for 9-slice
        self._btn_imgs = imgs = {}
        for name, color in [("n", C["btn_bg"]), ("h", C["btn_hover"]),
                            ("a", C["btn_active"]),
                            ("an", C["accent_teal"]), ("ah", C["accent_green"]),
                            ("fn", C["accent_purple"]), ("fh", "#D0ACF0")]:
            imgs[name] = self._pill_img(self.root, SZ, SZ, R, color)
        bd = (R, R, R, R)  # 9-slice border insets
        s.element_create("RoundBtn.bg", "image", imgs["n"],
                         ("active", imgs["h"]), ("pressed", imgs["a"]),
                         border=bd, sticky="nsew")
        s.element_create("AccentBtn.bg", "image", imgs["an"],
                         ("active", imgs["ah"]), ("pressed", imgs["a"]),
                         border=bd, sticky="nsew")

        # ── base defaults ──
        s.configure(".", background=C["bg_mid"], foreground=C["fg_main"],
                    bordercolor=C["border"], darkcolor=C["bg_dark"],
                    lightcolor=C["bg_light"], troughcolor=C["bg_dark"],
                    fieldbackground=C["bg_light"], font=(FONT_FAMILY,9))

        # ── frames & labels ──
        s.configure("TFrame", background=C["bg_mid"])
        s.configure("TLabel", background=C["bg_mid"], foreground=C["fg_main"],
                    padding=(2,2))
        s.configure("Title.TLabel", font=(FONT_FAMILY,12,"bold"),
                    foreground=C["accent_purple"], padding=(4,6))
        s.configure("Section.TLabel", font=(FONT_FAMILY,9,"bold"),
                    foreground=C["accent_teal"], padding=(2,4))
        s.configure("Result.TLabel", font=(FONT_FAMILY,9,"bold"),
                    foreground=C["fg_bright"], padding=(3,3))
        s.configure("Big.TLabel", font=(FONT_FAMILY,11,"bold"), padding=(3,3))
        s.configure("Calc.TLabel", font=(FONT_FAMILY,9), padding=(2,2))

        # ── buttons: rounded pill background ──
        s.layout("TButton", [
            ("RoundBtn.bg", {"sticky":"nsew", "children": [
                ("Button.padding", {"sticky":"nsew", "children": [
                    ("Button.label", {"sticky":"nsew"})
                ]})
            ]})
        ])
        s.configure("TButton", foreground=C["fg_main"], font=(FONT_FAMILY,9),
                    padding=(12,6), anchor="center")
        s.map("TButton", foreground=[("disabled",C["fg_dim"])])

        s.layout("Accent.TButton", [
            ("AccentBtn.bg", {"sticky":"nsew", "children": [
                ("Button.padding", {"sticky":"nsew", "children": [
                    ("Button.label", {"sticky":"nsew"})
                ]})
            ]})
        ])
        s.configure("Accent.TButton", foreground=C["bg_dark"],
                    font=(FONT_FAMILY,9,"bold"), padding=(14,7), anchor="center")

        s.element_create("FITSBtn.bg", "image", imgs["fn"],
                         ("active", imgs["fh"]), ("pressed", imgs["a"]),
                         border=bd, sticky="nsew")
        s.layout("FITS.TButton", [
            ("FITSBtn.bg", {"sticky":"nsew", "children": [
                ("Button.padding", {"sticky":"nsew", "children": [
                    ("Button.label", {"sticky":"nsew"})
                ]})
            ]})
        ])
        s.configure("FITS.TButton", foreground=C["fg_bright"],
                    font=(FONT_FAMILY,10,"bold"), padding=(18,8), anchor="center")

        s.configure("Small.TButton", padding=(6,3), font=(FONT_FAMILY,8))

        # ── entries: softer focus glow ──
        s.configure("TEntry", fieldbackground=C["bg_light"], foreground=C["fg_main"],
                    insertcolor=C["fg_main"], borderwidth=1, relief="flat",
                    padding=(4,4))
        s.map("TEntry",
              fieldbackground=[("focus",C["bg_hover"]),("!focus",C["bg_light"])],
              bordercolor=[("focus",C["accent_purple"]),("!focus",C["border"])])

        # ── comboboxes ──
        s.configure("TCombobox", fieldbackground=C["bg_light"], foreground=C["fg_main"],
                    background=C["btn_bg"], arrowcolor=C["fg_dim"],
                    borderwidth=1, relief="flat", padding=(4,3))
        s.map("TCombobox",
              fieldbackground=[("readonly",C["bg_light"])],
              foreground=[("readonly",C["fg_main"])],
              selectbackground=[("readonly",C["bg_selected"])],
              selectforeground=[("readonly",C["fg_bright"])],
              bordercolor=[("focus",C["accent_purple"]),("!focus",C["border"])])

        # ── checkbuttons: teal indicator ──
        s.configure("TCheckbutton", background=C["bg_mid"], foreground=C["fg_main"],
                    indicatorbackground=C["bg_light"],
                    indicatorforeground=C["accent_teal"], padding=(4,3))
        s.map("TCheckbutton", background=[("active",C["bg_mid"])],
              indicatorbackground=[("selected",C["accent_teal"]),
                                   ("!selected",C["bg_light"])])

        # ── notebook tabs: warmer selected color ──
        s.configure("TNotebook", background=C["bg_dark"], borderwidth=0)
        s.configure("TNotebook.Tab", background=C["tab_inactive"],
                    foreground=C["fg_dim"], padding=(14,7),
                    font=(FONT_FAMILY,10))
        s.map("TNotebook.Tab",
              background=[("selected",C["tab_active"])],
              foreground=[("selected",C["accent_gold"])],
              expand=[("selected",[0,0,0,2])])

        # ── treeviews: taller rows, teal headings ──
        s.configure("Treeview", background=C["tree_odd"], foreground=C["fg_main"],
                    fieldbackground=C["tree_odd"], borderwidth=0,
                    rowheight=28, font=(FONT_FAMILY,9))
        s.configure("Treeview.Heading", background=C["bg_dark"],
                    foreground=C["accent_teal"],
                    font=(FONT_FAMILY,9,"bold"), borderwidth=0,
                    relief="flat", padding=(4,4))
        s.map("Treeview",
              background=[("selected",C["bg_selected"])],
              foreground=[("selected",C["fg_bright"])])
        s.map("Treeview.Heading", background=[("active",C["bg_hover"])])

        # ── scrollbars ──
        s.configure("TScrollbar", background=C["bg_light"],
                    troughcolor=C["bg_dark"], borderwidth=0,
                    arrowcolor=C["fg_dim"])
        s.map("TScrollbar",
              background=[("active",C["bg_hover"]),("!disabled",C["bg_light"])])

        # ── label frames: pink accent ──
        s.configure("TLabelframe", background=C["bg_mid"],
                    bordercolor=C["border"], relief="groove", borderwidth=1)
        s.configure("TLabelframe.Label", background=C["bg_mid"],
                    foreground=C["accent_pink"],
                    font=(FONT_FAMILY,9,"bold"), padding=(4,2))

        # ── separators & progress ──
        s.configure("TSeparator", background=C["separator"])
        s.configure("TProgressbar", background=C["accent_teal"],
                    troughcolor=C["bg_dark"], borderwidth=0)

    # ── UI skeleton ──
    def _build_ui(self):
        self.root.title(self.t("app_title"))
        ui = self.data.get("ui", {})
        geo = ui.get("window_geometry", "1400x1100")
        # Ensure saved geometry isn't too short for current DPI
        try:
            dims = geo.split("+")[0]
            gw, gh = (int(v) for v in dims.split("x"))
            if gh < 1100:
                gh = 1100
                geo = f"{gw}x{gh}" + ("+" + "+".join(geo.split("+")[1:])) if "+" in geo else f"{gw}x{gh}"
        except (ValueError, IndexError):
            pass
        self.root.geometry(geo); self.root.minsize(1050,1100)
        self.menu = tk.Menu(self.root, bg=C["menu_bg"], fg=C["fg_main"],
                            activebackground=C["bg_selected"], activeforeground=C["fg_bright"],
                            bd=0, relief="flat")
        self.root.config(menu=self.menu)

        # ── main toolbar ──
        mtb = ttk.Frame(self.root); mtb.pack(fill=tk.X, padx=6, pady=(4,0))
        self.btn_open_cat = ttk.Button(mtb, text=self.t("open_catalog"), command=self._open_catalog,
                                       style="Accent.TButton")
        self.btn_open_cat.pack(side=tk.LEFT, padx=4)
        self._tip(self.btn_open_cat, "Open the parts catalog in a large separate window",
                  "Ouvrir le catalogue de pi\u00e8ces dans une grande fen\u00eatre s\u00e9par\u00e9e")
        self.btn_new_part = ttk.Button(mtb, text=self.t("new_part"), command=self._new_part)
        self.btn_new_part.pack(side=tk.LEFT, padx=4)
        self._tip(self.btn_new_part, "Create a new custom part",
                  "Cr\u00e9er une nouvelle pi\u00e8ce personnalis\u00e9e")

        # ── FITS analyzer big button (right side) ──
        self.btn_fits = ttk.Button(mtb, text=self.t("fits_btn"),
                                   command=self._open_fits_analyzer,
                                   style="FITS.TButton")
        self.btn_fits.pack(side=tk.RIGHT, padx=(12, 4))
        self._tip(self.btn_fits,
                  "Analyze a FITS/XISF image to diagnose backfocus errors",
                  "Analyser une image FITS/XISF pour diagnostiquer les erreurs de backfocus")

        # ── configuration panel ──
        self.fr_cfg = ttk.Frame(self.root)
        self.fr_cfg.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._build_config_panel()
        # restore saved sash positions after layout is ready
        self.root.after(100, self._restore_sash_positions)

    # ═════════════════════ CONFIG PANEL ═════════════════════
    def _build_config_panel(self):
        fr = self.fr_cfg

        # ── horizontal paned window: config list | editor ──
        self.pw_h = tk.PanedWindow(fr, orient=tk.HORIZONTAL, sashwidth=6,
                                    bg=C["separator"], bd=0, opaqueresize=True)
        self.pw_h.pack(fill=tk.BOTH, expand=True)

        # ── left: config list ──
        left = ttk.Frame(self.pw_h)
        ttk.Label(left, text="Configurations", style="Title.TLabel").pack(pady=(6,4))

        bb = ttk.Frame(left); bb.pack(fill=tk.X, padx=4, pady=6)
        self.btn_c_add = ttk.Button(bb, text="+", width=3, command=self._add_config, style="Accent.TButton")
        self.btn_c_add.pack(side=tk.LEFT, padx=1)
        self._tip(self.btn_c_add, "Create a new configuration", "Créer une nouvelle configuration")
        self.btn_c_edit = ttk.Button(bb, text=self.t("edit_config"), width=4,
                                      command=self._edit_config, style="Small.TButton")
        self.btn_c_edit.pack(side=tk.LEFT, padx=1)
        self._tip(self.btn_c_edit, "Edit configuration", "Modifier la configuration")
        self.btn_c_dup = ttk.Button(bb, text="Dup", width=4, command=self._dup_config,
                                     style="Small.TButton")
        self.btn_c_dup.pack(side=tk.LEFT, padx=1)
        self._tip(self.btn_c_dup, "Duplicate configuration", "Dupliquer la configuration")
        self.btn_c_del = ttk.Button(bb, text="Del", width=4, command=self._del_config,
                                     style="Small.TButton")
        self.btn_c_del.pack(side=tk.LEFT, padx=1)
        self._tip(self.btn_c_del, "Delete selected configuration", "Supprimer la configuration sélectionnée")

        self.clist = tk.Listbox(left, selectmode=tk.SINGLE, bg=C["bg_light"], fg=C["fg_main"],
                                selectbackground=C["bg_selected"], selectforeground=C["fg_bright"],
                                highlightthickness=0, bd=0, relief="flat", font=(FONT_FAMILY,10),
                                exportselection=False)
        self.clist.pack(fill=tk.BOTH, expand=True, pady=6)
        self.clist.bind("<<ListboxSelect>>", self._on_cfg_select)
        # -- drag reorder in config list --
        self._cfg_drop_line = tk.Frame(left, height=2, bg=C["accent_green"])
        self._cfg_drag_idx = None
        self._cfg_dragging = False
        self.clist.bind("<ButtonPress-1>", self._cfg_drag_start, add="+")
        self.clist.bind("<B1-Motion>", self._cfg_drag_motion)
        self.clist.bind("<ButtonRelease-1>", self._cfg_drag_end)

        # ── right: editor ──
        right = ttk.Frame(self.pw_h)
        self.pw_h.add(left, minsize=150, width=220)
        self.pw_h.add(right, minsize=400)

        top = ttk.Frame(right); top.pack(fill=tk.X, pady=(0,6))
        self.lbl_target = ttk.Label(top, text=self.t("target_bf"))
        self.lbl_target.pack(side=tk.LEFT, padx=(0,4))
        self.v_target = tk.StringVar(value="0")
        self.v_target.trace_add("write", lambda *_: self._calc())
        e_target = ttk.Entry(top, textvariable=self.v_target, width=8)
        e_target.pack(side=tk.LEFT, padx=(0,14))
        self._tip(e_target, "Target backfocus distance", "Distance de backfocus cible")
        self.lbl_notes = ttk.Label(top, text=self.t("notes"))
        self.lbl_notes.pack(side=tk.LEFT, padx=(0,4))
        self.v_notes = tk.StringVar()
        self.v_notes.trace_add("write", lambda *_: self._save_cfg())
        ttk.Entry(top, textvariable=self.v_notes, width=35).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── vertical paned window: treeview | diagram ──
        self.pw_v = tk.PanedWindow(right, orient=tk.VERTICAL, sashwidth=6,
                                    bg=C["separator"], bd=0, opaqueresize=True)
        self.pw_v.pack(fill=tk.BOTH, expand=True)

        # ── bottom: backfocus info + diagram ──
        bot = ttk.Frame(self.pw_v)
        cf = ttk.LabelFrame(bot, text="Backfocus")
        cf.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0,6))
        self.lbl_total = ttk.Label(cf, text="", style="Calc.TLabel")
        self.lbl_total.pack(anchor=tk.W, padx=10, pady=2)
        self.lbl_bf = ttk.Label(cf, text="", style="Result.TLabel")
        self.lbl_bf.pack(anchor=tk.W, padx=10, pady=2)
        self.lbl_diff = ttk.Label(cf, text="", style="Big.TLabel")
        self.lbl_diff.pack(anchor=tk.W, padx=10, pady=2)
        df = ttk.LabelFrame(bot, text=self.t("diagram"))
        df.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(df, height=120, bg=C["canvas_bg"], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._drop_highlight = False
        self._diag_ranges = []
        self._diag_drag_idx = None
        self._last_draw_args = None
        self._resize_after_id = None
        self._last_canvas_size = (0, 0)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self._diag_drag_start)
        self.canvas.bind("<B1-Motion>", self._diag_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._diag_drag_end)

        # ── mid (treeview — fills remaining space) ──
        mid = ttk.Frame(self.pw_v)
        self.pw_v.add(mid, minsize=120)
        self.pw_v.add(bot, minsize=80, height=160)

        sf = ttk.LabelFrame(mid, text=self.t("train_label"))
        sf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cols = ("idx","brand","name","type","mm","t_conn","c_conn","flip","bf","compat")
        self.stree = ttk.Treeview(sf, columns=cols, show="headings", selectmode="browse")
        for c, txt, w in [("idx","#",30),("brand",self.t("part_brand"),75),
                          ("name",self.t("part_name"),170),("type",self.t("part_type"),95),
                          ("mm","mm",48),("t_conn",self.t("tside"),110),
                          ("c_conn",self.t("cside"),110),("flip",self.t("flip_piece"),42),
                          ("bf","BF",58),("compat","",85)]:
            self.stree.heading(c, text=txt)
            self.stree.column(c, width=w, anchor=tk.CENTER if w<100 else tk.W)
        self.stree.tag_configure("bf_zone", background=C["bf_zone"])
        self.stree.tag_configure("bf_start", foreground=C["accent_green"])
        self.stree.tag_configure("bf_end", foreground=C["accent_pink"])
        self.stree.tag_configure("mismatch", foreground=C["accent_red"])
        self.stree.tag_configure("ghost", foreground=C["accent_orange"],
                                 background="#342C22")
        self.stree.tag_configure("odd", background=C["tree_odd"])
        self.stree.tag_configure("even", background=C["tree_even"])
        self.stree.bind("<Double-1>", lambda e: self._stack_edit())
        # -- drag reorder in treeview --
        self._tree_drag_iid = None
        self._tree_drop_line = tk.Frame(sf, height=2, bg=C["accent_green"])
        self.stree.bind("<ButtonPress-1>", self._tree_drag_start)
        self.stree.bind("<B1-Motion>", self._tree_drag_motion)
        self.stree.bind("<ButtonRelease-1>", self._tree_drag_end)
        ssb = ttk.Scrollbar(sf, orient=tk.VERTICAL, command=self.stree.yview)
        self.stree.configure(yscrollcommand=ssb.set)
        self.stree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ssb.pack(side=tk.RIGHT, fill=tk.Y)

        # buttons
        bfr = ttk.Frame(mid); bfr.pack(side=tk.LEFT, fill=tk.Y, padx=6)
        btn_spec = [
            ("add_to_stack",      self._stack_add,      "Accent.TButton",
             "Add a part from your catalog to the train","Ajouter une pi\u00e8ce du catalogue au train"),
            ("remove_from_stack", self._stack_rm,        "TButton",
             "Remove selected part from train","Retirer la pi\u00e8ce du train"),
            (None, None, None, None, None),
            ("move_up",           self._stack_up,        "TButton",
             "Move part up (towards telescope)","D\u00e9placer vers le haut (vers le t\u00e9lescope)"),
            ("move_down",         self._stack_dn,        "TButton",
             "Move part down (towards camera)","D\u00e9placer vers le bas (vers la cam\u00e9ra)"),
            ("flip_piece",        self._stack_flip,      "TButton",
             "Flip a reversible part (swap sides)","Retourner une pi\u00e8ce r\u00e9versible"),
            (None, None, None, None, None),
            ("mark_bf_start",     self._mark_bf_start,   "TButton",
             "BF measured from camera-side output of this part","BF mesur\u00e9 depuis la sortie c\u00f4t\u00e9 cam\u00e9ra de cette pi\u00e8ce"),
            ("mark_bf_end",       self._mark_bf_end,     "TButton",
             "BF measured to telescope-side input of this part (sensor)","BF mesur\u00e9 jusqu\u2019\u00e0 l\u2019entr\u00e9e c\u00f4t\u00e9 t\u00e9lescope de cette pi\u00e8ce (capteur)"),
            (None, None, None, None, None),
            ("auto_suggest",      self._suggest,         "Accent.TButton",
             "Find a single part that fills the gap","Trouver une pi\u00e8ce qui comble l\u2019\u00e9cart"),
            ("auto_complete",     self._auto_complete,   "Accent.TButton",
             "Find combinations of owned parts","Trouver des combinaisons de pi\u00e8ces poss\u00e9d\u00e9es"),
            (None, None, None, None, None),
            ("insert_ghost",     self._stack_add_ghost, "TButton",
             "Insert a ghost placeholder at current position",
             "Ins\u00e9rer un fant\u00f4me \u00e0 la position courante"),
            ("resolve_ghosts",   self._resolve_ghosts,  "TButton",
             "Find real parts to replace ghost placeholders",
             "Trouver des pi\u00e8ces r\u00e9elles pour remplacer les fant\u00f4mes"),
        ]
        for spec in btn_spec:
            if spec[0] is None:
                ttk.Separator(bfr, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)
            else:
                key, cmd, sty, tip_en, tip_fr = spec
                b = ttk.Button(bfr, text=self.t(key), command=cmd, style=sty)
                b.pack(fill=tk.X, pady=2)
                setattr(self, f"btn_{key}", b)
                self._tip(b, tip_en, tip_fr)

        _tip_lbl = tk.Label(self.root, text="\u2615", fg=C["fg_dim"], bg=C["bg_dark"],
                            font=(FONT_FAMILY,7), cursor="hand2")
        _tip_lbl.pack(side=tk.BOTTOM, anchor=tk.E, padx=6, pady=(0,2))
        _tip_lbl.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://buymeacoffee.com/orlytourbou"))
        # Defer first config load so the canvas has real dimensions after layout
        self.root.after_idle(self._refresh_cfgs)

    # ── open catalog ──
    def _open_catalog(self):
        if self._catalog_win and self._catalog_win.win.winfo_exists():
            self._catalog_win.win.lift()
        else:
            self._catalog_win = CatalogWindow(self)

    def _open_fits_analyzer(self):
        if not _HAS_FITS_ANALYZER:
            messagebox.showinfo(self.t("fits_analyzer"),
                                self.t("fits_analyzer_missing_deps"))
            return
        if self._fits_win and self._fits_win.win.winfo_exists():
            self._fits_win.win.lift()
        else:
            self._fits_win = FITSAnalyzerWindow(self)

    def _new_part(self):
        self._open_catalog()
        self._catalog_win._add()

    # ── config CRUD ──
    def _refresh_cfgs(self):
        self.clist.delete(0, tk.END)
        for c in self.data["configurations"]:
            self.clist.insert(tk.END, c["name"])
        if self.data["configurations"]:
            self.clist.selection_set(0); self._on_cfg_select(None)

    def _cfg_idx(self):
        s = self.clist.curselection()
        return s[0] if s else None

    def _on_cfg_select(self, _):
        if self._cfg_dragging: return
        i = self._cfg_idx()
        if i is None: return
        c = self.data["configurations"][i]
        self.v_target.set(str(c.get("target_backfocus",0)))
        self.v_notes.set(c.get("notes",""))
        self._refresh_stack()

    def _add_config(self):
        dlg = tk.Toplevel(self.root); dlg.title(self.t("add_config"))
        dlg.geometry("400x180"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        nv = tk.StringVar(); tv = tk.StringVar(value="55")
        ttk.Label(dlg, text=self.t("config_name")).grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)
        ttk.Entry(dlg, textvariable=nv, width=25).grid(row=0,column=1,padx=10,pady=10)
        ttk.Label(dlg, text=self.t("target_bf")).grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)
        ttk.Entry(dlg, textvariable=tv, width=25).grid(row=1,column=1,padx=10,pady=10)
        def ok():
            n = nv.get().strip()
            if not n: return
            try: t = float(tv.get().replace(",","."))
            except ValueError: t = 55
            self.data["configurations"].append({"name":n,"target_backfocus":t,"notes":"",
                                                "bf_start_idx":-1,"bf_end_idx":-1,"stack":[]})
            self._save(); self._refresh_cfgs()
            self.clist.selection_clear(0,tk.END)
            self.clist.selection_set(len(self.data["configurations"])-1)
            self._on_cfg_select(None); dlg.destroy()
        bf = ttk.Frame(dlg); bf.grid(row=2,column=0,columnspan=2,pady=12)
        ttk.Button(bf, text=self.t("ok"), command=ok, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, ok); _center_dlg(dlg, self.root)

    def _del_config(self):
        i = self._cfg_idx()
        if i is None: return
        nm = self.data["configurations"][i]["name"]
        if messagebox.askyesno(self.t("confirm_delete"), self.t("confirm_delete_msg",name=nm)):
            self.data["configurations"].pop(i); self._save(); self._refresh_cfgs()

    def _dup_config(self):
        i = self._cfg_idx()
        if i is None: return
        nc = copy.deepcopy(self.data["configurations"][i]); nc["name"] += " (copy)"
        self.data["configurations"].append(nc); self._save(); self._refresh_cfgs()

    def _edit_config(self):
        i = self._cfg_idx()
        if i is None: return
        cfg = self.data["configurations"][i]
        dlg = tk.Toplevel(self.root); dlg.title(self.t("edit_config"))
        dlg.geometry("400x180"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        nv = tk.StringVar(value=cfg["name"])
        tv = tk.StringVar(value=str(cfg.get("target_backfocus", 0)))
        notesv = tk.StringVar(value=cfg.get("notes", ""))
        ttk.Label(dlg, text=self.t("config_name")).grid(row=0, column=0, padx=10, pady=6, sticky=tk.W)
        ttk.Entry(dlg, textvariable=nv, width=25).grid(row=0, column=1, padx=10, pady=6)
        ttk.Label(dlg, text=self.t("target_bf")).grid(row=1, column=0, padx=10, pady=6, sticky=tk.W)
        ttk.Entry(dlg, textvariable=tv, width=25).grid(row=1, column=1, padx=10, pady=6)
        ttk.Label(dlg, text=self.t("notes")).grid(row=2, column=0, padx=10, pady=6, sticky=tk.W)
        ttk.Entry(dlg, textvariable=notesv, width=25).grid(row=2, column=1, padx=10, pady=6)
        def ok():
            n = nv.get().strip()
            if not n: return
            cfg["name"] = n
            try: cfg["target_backfocus"] = float(tv.get().replace(",", "."))
            except ValueError: pass
            cfg["notes"] = notesv.get()
            self._save(); self._refresh_cfgs()
            self.clist.selection_clear(0, tk.END)
            self.clist.selection_set(i); self._on_cfg_select(None)
            dlg.destroy()
        bf = ttk.Frame(dlg); bf.grid(row=3, column=0, columnspan=2, pady=8)
        ttk.Button(bf, text=self.t("ok"), command=ok, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, ok); _center_dlg(dlg, self.root)

    def _save_cfg(self):
        i = self._cfg_idx()
        if i is None: return
        c = self.data["configurations"][i]
        try: c["target_backfocus"] = float(self.v_target.get().replace(",","."))
        except ValueError: pass
        c["notes"] = self.v_notes.get()
        # Reuse the unified debounced save (coalesces with other saves)
        self._save()

    # ── config list drag reorder ──
    def _cfg_drag_start(self, event):
        idx = self.clist.nearest(event.y)
        if idx >= 0 and idx < self.clist.size():
            self._cfg_drag_idx = idx
            self._cfg_drag_started = False
            self._cfg_drag_y0 = event.y
        else:
            self._cfg_drag_idx = None

    def _cfg_drag_motion(self, event):
        if self._cfg_drag_idx is None: return
        if not self._cfg_drag_started:
            if abs(event.y - self._cfg_drag_y0) < 5: return
            self._cfg_drag_started = True
            self._cfg_dragging = True
            self.clist.itemconfigure(self._cfg_drag_idx, fg=C["fg_dim"])
        target = self.clist.nearest(event.y)
        if target < 0: target = self._cfg_drag_idx
        bbox = self.clist.bbox(target)
        if bbox:
            x, y, w, h = bbox
            ly = y if target < self._cfg_drag_idx else y + h
            self._cfg_drop_line.place(in_=self.clist, x=x, y=ly, width=w, height=2)
        else:
            self._cfg_drop_line.place_forget()

    def _cfg_drag_end(self, event):
        self._cfg_drop_line.place_forget()
        if self._cfg_drag_idx is not None and self._cfg_drag_started:
            target = self.clist.nearest(event.y)
            if target < 0: target = self._cfg_drag_idx
            src = self._cfg_drag_idx
            if target != src:
                cfgs = self.data["configurations"]
                item = cfgs.pop(src)
                cfgs.insert(target, item)
                self._save()
                self._refresh_cfgs()
                self.clist.selection_clear(0, tk.END)
                self.clist.selection_set(target)
                self._on_cfg_select(None)
            else:
                self.clist.itemconfigure(src, fg=C["fg_main"])
        self._cfg_drag_idx = None
        self._cfg_dragging = False

    # ── stack ──
    def _refresh_stack(self):
        i = self._cfg_idx()
        self.stree.delete(*self.stree.get_children())
        if i is None: return
        cfg = self.data["configurations"][i]
        stack = cfg.get("stack",[]); bs = cfg.get("bf_start_idx",-1); be = cfg.get("bf_end_idx",-1)
        # Auto-detect bf_start/end from bf_role if not set
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
        lu = self.data.get("length_unit","mm")
        for si, item in enumerate(stack):
            eff = _effective(item)
            compat = ""
            if si > 0:
                prev = _effective(stack[si-1])
                if prev.get("cside_thread") and eff.get("tside_thread"):
                    ok = _conn_compat(prev.get("cside_thread",""), prev.get("cside_gender",""),
                                      eff.get("tside_thread",""), eff.get("tside_gender",""))
                    compat = "OK" if ok else "MISMATCH"
            bf_mark = ""
            if si == bs: bf_mark = ">> BF START \u2193"
            elif si == be: bf_mark = "\u2191 BF END <<"
            elif bs >= 0 and be >= 0 and bs < si < be: bf_mark = "\u2026"
            tags = ["odd" if si%2==0 else "even"]
            if item.get("ghost"): tags.append("ghost")
            if 0 <= bs <= be and bs < si <= be: tags.append("bf_zone")
            if si == bs: tags.append("bf_start")
            if si == be: tags.append("bf_end")
            if compat == "MISMATCH": tags.append("mismatch")
            ol = item.get("optical_length",0)
            self.stree.insert("", tk.END, iid=str(si), values=(
                si+1, item.get("brand",""), item.get("name",""),
                self._ttype(item.get("type","")), _fmt_len(ol,lu),
                f'{eff.get("tside_thread","")} {eff.get("tside_gender","")}'.strip(),
                f'{eff.get("cside_thread","")} {eff.get("cside_gender","")}'.strip(),
                "FLIP" if item.get("flipped") else "", bf_mark, compat,
            ), tags=tuple(tags))
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
        sel = self.stree.selection()
        ins_idx = (int(sel[0]) + 1) if sel else len(stack)
        ghost = self._make_ghost(stack, ins_idx)
        stack.insert(ins_idx, ghost)
        self._save(); self._refresh_stack()

    def _stack_edit(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        si = int(s[0]); cfg = self.data["configurations"][ci]
        stack = cfg.get("stack", [])
        if si >= len(stack): return
        p = stack[si]
        dlg = tk.Toplevel(self.root); dlg.title(self.t("edit_part"))
        _saved = self.data.get("ui", {}).get("part_dlg_geometry", "600x740")
        dlg.geometry(_saved); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.minsize(500, 500)
        dlg.configure(bg=C["bg_mid"])
        r = 0; vars_ = {}
        def _row(label, key, wf, **kw):
            nonlocal r
            ttk.Label(dlg, text=label).grid(row=r, column=0, sticky=tk.W, padx=10, pady=4)
            w, var = wf(dlg, r, kw); vars_[key] = var; r += 1; return w
        def _entry(par, row, kw):
            v = tk.StringVar(value=str(kw.get("val",""))); e = ttk.Entry(par, textvariable=v, width=kw.get("w",30))
            e.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4); return e, v
        def _combo(par, row, kw):
            v = tk.StringVar(value=kw.get("val",""))
            c = ttk.Combobox(par, textvariable=v, values=kw.get("vals",[]),
                             state="readonly" if kw.get("ro") else "normal", width=kw.get("w",20))
            c.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4); return c, v
        def _check(par, row, kw):
            v = tk.BooleanVar(value=kw.get("val",False)); c = ttk.Checkbutton(par, variable=v)
            c.grid(row=row, column=1, sticky=tk.W, padx=10, pady=4); return c, v
        _all_brands = sorted({"Custom Made"} | _REF_BRANDS | {pp.get("brand","") for pp in self.data["parts"] if pp.get("brand","")})
        _row(self.t("part_brand"), "brand", _combo, val=p.get("brand",""), vals=_all_brands, w=20)
        _row(self.t("part_name"), "name", _entry, val=p.get("name",""), w=30)
        type_map = {self._ttype(k): k for k in PART_TYPES}
        _row(self.t("part_type"), "type", _combo, val=self._ttype(p.get("type","")),
             vals=sorted(type_map.keys()), ro=True, w=18)
        _row(self.t("optical_length"), "mm", _entry, val=p.get("optical_length",0), w=10)
        _row(self.t("mass_label"), "mass", _entry, val=p.get("mass",0), w=10)
        _row(self.t("reversible"), "reversible", _check, val=p.get("reversible",False))
        _row(self.t("bf_role"), "bf_role", _combo, val=p.get("bf_role",""), vals=["","start","end"], w=10)
        ttk.Separator(dlg, orient=tk.HORIZONTAL).grid(row=r, column=0, columnspan=3, sticky=tk.EW, padx=10, pady=8); r += 1
        ttk.Label(dlg, text=self.t("tside"), style="Section.TLabel").grid(row=r, column=0, columnspan=3, sticky=tk.W, padx=10); r += 1
        _row(self.t("thread"), "tside_thread", _combo, val=p.get("tside_thread",""), vals=THREADS, w=22)
        _row(self.t("gender"), "tside_gender", _combo, val=p.get("tside_gender",""), vals=GENDERS, ro=True, w=10)
        ttk.Label(dlg, text=self.t("cside"), style="Section.TLabel").grid(row=r, column=0, columnspan=3, sticky=tk.W, padx=10); r += 1
        _row(self.t("thread"), "cside_thread", _combo, val=p.get("cside_thread",""), vals=THREADS, w=22)
        _row(self.t("gender"), "cside_gender", _combo, val=p.get("cside_gender",""), vals=GENDERS, ro=True, w=10)
        ttk.Separator(dlg, orient=tk.HORIZONTAL).grid(row=r, column=0, columnspan=3, sticky=tk.EW, padx=10, pady=8); r += 1
        # qty with +/- buttons — find matching catalog part
        cat_idx = None
        pn = p.get("name",""); pb = p.get("brand","")
        for qi, cp in enumerate(self.data["parts"]):
            if cp.get("name") == pn and cp.get("brand") == pb:
                cat_idx = qi; break
        cat_qty = self.data["parts"][cat_idx].get("qty", 0) if cat_idx is not None else 0
        ttk.Label(dlg, text=self.t("qty")).grid(row=r, column=0, sticky=tk.W, padx=10, pady=4)
        qf = ttk.Frame(dlg); qf.grid(row=r, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4)
        qty_var = tk.StringVar(value=str(cat_qty)); vars_["qty"] = qty_var
        ttk.Button(qf, text="\u2212", width=2, style="Small.TButton",
                   command=lambda: qty_var.set(str(max(0, _safe_int(qty_var.get())-1)))).pack(side=tk.LEFT, padx=(0,2))
        ttk.Entry(qf, textvariable=qty_var, width=4).pack(side=tk.LEFT)
        ttk.Button(qf, text="+", width=2, style="Small.TButton",
                   command=lambda: qty_var.set(str(_safe_int(qty_var.get())+1))).pack(side=tk.LEFT, padx=(2,0))
        r += 1
        def _save():
            try: ol = float(str(vars_["mm"].get()).replace(",","."))
            except ValueError: ol = 0
            try: ms = float(str(vars_["mass"].get()).replace(",","."))
            except ValueError: ms = 0
            td = type_map.get(vars_["type"].get(), p.get("type","type_adapter"))
            p["brand"] = vars_["brand"].get().strip()
            p["name"] = vars_["name"].get().strip()
            p["type"] = td; p["optical_length"] = ol; p["mass"] = ms
            p["reversible"] = vars_["reversible"].get()
            p["bf_role"] = vars_["bf_role"].get()
            p["tside_thread"] = vars_["tside_thread"].get().strip()
            p["tside_gender"] = vars_["tside_gender"].get()
            p["cside_thread"] = vars_["cside_thread"].get().strip()
            p["cside_gender"] = vars_["cside_gender"].get()
            if p.get("ghost"): p["ghost"] = False
            # update catalog qty
            try: nq = max(0, int(vars_["qty"].get()))
            except ValueError: nq = cat_qty
            if cat_idx is not None:
                self.data["parts"][cat_idx]["qty"] = nq
            self._save(); self._refresh_stack(); _close_dlg()
        def _close_dlg():
            self.data.setdefault("ui", {})["part_dlg_geometry"] = dlg.geometry()
            dlg.destroy()
        bf = ttk.Frame(dlg); bf.grid(row=r, column=0, columnspan=3, pady=12)
        ttk.Button(bf, text=self.t("save"), command=_save, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=_close_dlg).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg); _center_dlg(dlg, self.root)

    def _stack_rm(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        si = int(s[0]); cfg = self.data["configurations"][ci]
        if si >= len(cfg.get("stack",[])): return
        cfg["stack"].pop(si)
        for mk in ("bf_start_idx","bf_end_idx"):
            v = cfg.get(mk,-1)
            if v == si: cfg[mk] = -1
            elif v > si: cfg[mk] = v-1
        self._save(); self._refresh_stack()

    def _stack_up(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        si = int(s[0]); st = self.data["configurations"][ci]["stack"]
        if si > 0:
            st[si], st[si-1] = st[si-1], st[si]
            cfg = self.data["configurations"][ci]
            for mk in ("bf_start_idx","bf_end_idx"):
                v = cfg.get(mk,-1)
                if v == si: cfg[mk] = si-1
                elif v == si-1: cfg[mk] = si
            self._save(); self._refresh_stack(); self.stree.selection_set(str(si-1))

    def _stack_dn(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        si = int(s[0]); st = self.data["configurations"][ci]["stack"]
        if si < len(st)-1:
            st[si], st[si+1] = st[si+1], st[si]
            cfg = self.data["configurations"][ci]
            for mk in ("bf_start_idx","bf_end_idx"):
                v = cfg.get(mk,-1)
                if v == si: cfg[mk] = si+1
                elif v == si+1: cfg[mk] = si
            self._save(); self._refresh_stack(); self.stree.selection_set(str(si+1))

    def _stack_flip(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        si = int(s[0]); stack = self.data["configurations"][ci].get("stack",[])
        if si >= len(stack): return
        item = stack[si]
        if not item.get("reversible"):
            messagebox.showinfo(self.t("flip_piece"), self.t("not_reversible")); return
        item["flipped"] = not item.get("flipped",False)
        self._save(); self._refresh_stack()

    # ── drag reorder helpers ──
    def _move_stack_item(self, from_idx, to_idx):
        """Move stack item from from_idx to to_idx, updating bf markers."""
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        if from_idx == to_idx: return
        if from_idx < 0 or from_idx >= len(stack): return
        if to_idx < 0 or to_idx >= len(stack): return
        item = stack.pop(from_idx)
        stack.insert(to_idx, item)
        # update bf markers
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
        self.stree.selection_set(str(to_idx))

    # ── treeview drag reorder ──
    def _tree_drag_start(self, event):
        iid = self.stree.identify_row(event.y)
        if iid:
            self._tree_drag_iid = iid
            self._tree_drag_started = False
            self._tree_drag_y0 = event.y
            self._tree_drag_target = None
        else:
            self._tree_drag_iid = None

    def _tree_drag_motion(self, event):
        if self._tree_drag_iid is None: return
        if not self._tree_drag_started:
            if abs(event.y - self._tree_drag_y0) < 5: return
            self._tree_drag_started = True
            # dim the source row
            self.stree.tag_configure("_dragging", foreground=C["fg_dim"])
            cur_tags = list(self.stree.item(self._tree_drag_iid, "tags") or ())
            if "_dragging" not in cur_tags: cur_tags.append("_dragging")
            self.stree.item(self._tree_drag_iid, tags=cur_tags)
        target = self.stree.identify_row(event.y)
        if not target: target = self._tree_drag_iid
        self._tree_drag_target = target
        # position insertion line
        src = int(self._tree_drag_iid); dst = int(target)
        bbox = self.stree.bbox(target)
        if bbox:
            x, y, w, h = bbox
            # line goes above if moving up, below if moving down or same
            ly = y if dst < src else y + h
            self._tree_drop_line.place(in_=self.stree, x=x, y=ly, width=w, height=2)
        else:
            self._tree_drop_line.place_forget()

    def _tree_drag_end(self, event):
        self._tree_drop_line.place_forget()
        if self._tree_drag_iid is not None and self._tree_drag_started:
            target = self._tree_drag_target
            if target and target != self._tree_drag_iid:
                self._move_stack_item(int(self._tree_drag_iid), int(target))
            else:
                self._refresh_stack()  # remove _dragging tag
        self._tree_drag_iid = None

    # ── diagram drag reorder ──
    def _diag_drag_start(self, event):
        self._diag_drag_idx = None
        self._diag_drag_target = None
        for x0, x1, si in self._diag_ranges:
            if x0 <= event.x <= x1:
                self._diag_drag_idx = si
                self._diag_drag_started = False
                self._diag_drag_x0 = event.x
                break

    def _diag_drag_motion(self, event):
        if self._diag_drag_idx is None: return
        if not getattr(self, "_diag_drag_started", False):
            if abs(event.x - self._diag_drag_x0) < 5: return
            self._diag_drag_started = True
        # find which slot the cursor is over
        target = self._diag_drag_idx
        for x0, x1, si in self._diag_ranges:
            if x0 <= event.x <= x1:
                target = si; break
        self._diag_drag_target = target
        # redraw with visual feedback
        self._diag_draw_drag(event.x)

    def _diag_draw_drag(self, mx):
        """Redraw the diagram with drag visual feedback."""
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack", [])
        if not stack: return
        src = self._diag_drag_idx; tgt = self._diag_drag_target
        bs = cfg.get("bf_start_idx", -1); be = cfg.get("bf_end_idx", -1)
        c = self.canvas; c.delete("all")
        W, H = c.winfo_width(), c.winfo_height()
        margin = 18; avail = W - 2*margin
        vis_total = sum(max(it.get("optical_length",0),2) for it in stack)
        bh = 42; yt = (H - bh) / 2; cr = c.create_rectangle
        x = margin
        insert_x = None
        for si, item in enumerate(stack):
            ol = max(item.get("optical_length",0),2)
            bw = max(ol/vis_total*avail, 8) if vis_total > 0 else 12
            is_src = (si == src)
            # mark insertion point
            if si == tgt and tgt < src:
                insert_x = x
            if is_src:
                # draw dimmed placeholder at original position
                cr(x, yt, x+bw, yt+bh, fill="", outline=C["fg_dim"])
                c.create_line(x+2, yt+bh/2, x+bw-2, yt+bh/2,
                              fill=C["fg_dim"], dash=(3,3))
            else:
                is_ghost = item.get("ghost", False)
                col = C["accent_orange"] if is_ghost else TYPE_COLORS.get(item.get("type",""), C["fg_dim"])
                if 0<=bs<=be and bs<si<=be:
                    cr(x-1,yt-5,x+bw+1,yt+bh+5,fill=C["bf_zone"],outline="",width=0)
                if is_ghost:
                    cr(x,yt,x+bw,yt+bh, fill="", outline=C["accent_orange"], dash=(4,3))
                    c.create_text(x+bw/2,yt+bh/2,text="?",font=(FONT_FAMILY,12,"bold"),fill=C["accent_orange"])
                else:
                    cr(x+1,yt+1,x+bw-1,yt+bh-1, fill=col, outline="", width=0)
                    cr(x,yt,x+bw,yt+bh, fill="", outline=C["border"])
                    if bw > 24:
                        c.create_text(x+bw/2,yt+bh/2,text=item.get("name","")[:16],font=(FONT_FAMILY,7),fill=C["bg_dark"])
                c.create_text(x+bw/2,yt+bh+12,text=f'{item.get("optical_length",0):.1f}',font=(FONT_FAMILY,7),fill=C["fg_dim"])
            if si == tgt and tgt >= src:
                insert_x = x + bw
            x += bw
        # draw insertion marker line
        if insert_x is not None and src != tgt:
            c.create_line(insert_x, yt-8, insert_x, yt+bh+8,
                          fill=C["accent_green"], width=3)
            c.create_polygon(insert_x-5, yt-8, insert_x+5, yt-8, insert_x, yt-2,
                             fill=C["accent_green"])
            c.create_polygon(insert_x-5, yt+bh+8, insert_x+5, yt+bh+8, insert_x, yt+bh+2,
                             fill=C["accent_green"])
        # draw floating piece at cursor
        if src < len(stack):
            item = stack[src]
            ol = max(item.get("optical_length",0),2)
            fw = max(ol/vis_total*avail, 8) if vis_total > 0 else 12
            fx = mx - fw/2
            fy = yt - 4
            is_ghost = item.get("ghost", False)
            col = C["accent_orange"] if is_ghost else TYPE_COLORS.get(item.get("type",""), C["fg_dim"])
            cr(fx, fy, fx+fw, fy+bh, fill=col, outline=C["accent_green"])
            if fw > 24:
                c.create_text(fx+fw/2, fy+bh/2, text=item.get("name","")[:16],
                              font=(FONT_FAMILY,7,"bold"), fill=C["fg_bright"])
        c.create_text(margin, yt-12, text="Telescope", font=(FONT_FAMILY,7), fill=C["fg_dim"], anchor=tk.W)
        c.create_text(W-margin, yt-12, text="Camera", font=(FONT_FAMILY,7), fill=C["fg_dim"], anchor=tk.E)

    def _diag_drag_end(self, event):
        if self._diag_drag_idx is not None and getattr(self, "_diag_drag_started", False):
            tgt = self._diag_drag_target
            if tgt is not None and tgt != self._diag_drag_idx:
                self._move_stack_item(self._diag_drag_idx, tgt)
            else:
                self._refresh_stack()  # redraw clean
        self._diag_drag_idx = None
        self._diag_drag_target = None

    def _mark_bf_start(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        idx = int(s[0]); cfg = self.data["configurations"][ci]
        be = cfg.get("bf_end_idx", -1)
        if be >= 0 and idx >= be:
            messagebox.showwarning(self.t("bf_start"), self.t("bf_start_after_end")); return
        cfg["bf_start_idx"] = idx
        self._save(); self._refresh_stack()

    def _mark_bf_end(self):
        ci = self._cfg_idx(); s = self.stree.selection()
        if ci is None or not s: return
        idx = int(s[0]); cfg = self.data["configurations"][ci]
        bs = cfg.get("bf_start_idx", -1)
        if bs >= 0 and idx <= bs:
            messagebox.showwarning(self.t("bf_end"), self.t("bf_end_before_start")); return
        cfg["bf_end_idx"] = idx
        self._save(); self._refresh_stack()

    # ── resolve ghosts ──
    def _resolve_ghosts(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack",[])
        ghost_indices = [i for i, item in enumerate(stack) if item.get("ghost")]
        if not ghost_indices:
            messagebox.showinfo(self.t("resolve_ghosts"), self.t("no_ghosts")); return
        # Resolve first ghost found
        gi = ghost_indices[0]; ghost = stack[gi]
        need_tt = ghost.get("tside_thread",""); need_tg = ghost.get("tside_gender","")
        need_ct = ghost.get("cside_thread",""); need_cg = ghost.get("cside_gender","")
        need_str = f"{need_tt} {need_tg}".strip() + " \u2192 " + f"{need_ct} {need_cg}".strip()
        # Search database for matching adapters
        matches = []
        for pi, p in enumerate(self.data["parts"]):
            if p.get("type") in ("type_telescope","type_refractor","type_camera","type_dslr"):
                continue
            eff = _effective(p)
            t_ok = _conn_compat(need_tt, need_tg, eff.get("tside_thread",""), eff.get("tside_gender","")) if need_tt else True
            # For tside match: ghost tside is what it needs to RECEIVE, part tside is what IT presents
            # Ghost tside_thread = left neighbor's cside → part must accept that on its tside
            pt, pg = eff.get("tside_thread",""), eff.get("tside_gender","")
            t_ok = True
            if need_tt and pt:
                if _extract_diam(need_tt) != _extract_diam(pt):
                    t_ok = False
                elif need_tg and pg and need_tg != pg:
                    # Ghost says it needs Female tside → part must have Female tside
                    t_ok = False
            ct, cg = eff.get("cside_thread",""), eff.get("cside_gender","")
            c_ok = True
            if need_ct and ct:
                if _extract_diam(need_ct) != _extract_diam(ct):
                    c_ok = False
                elif need_cg and cg and need_cg != cg:
                    c_ok = False
            if t_ok and c_ok and (pt or ct):
                matches.append((pi, p))
        # Show resolution dialog
        dlg = tk.Toplevel(self.root); dlg.title(self.t("resolve_title"))
        dlg.geometry("850x500"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        ttk.Label(dlg, text=self.t("resolve_need", tside=f"{need_tt} {need_tg}".strip() or "?",
                  cside=f"{need_ct} {need_cg}".strip() or "?"),
                  style="Result.TLabel").pack(padx=10, pady=8)
        cols = ("brand","name","type","mm","t_conn","c_conn","qty")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        for c, txt, w in [("brand",self.t("part_brand"),90),("name",self.t("part_name"),220),
                          ("type",self.t("part_type"),100),("mm","mm",55),
                          ("t_conn",self.t("tside"),130),("c_conn",self.t("cside"),130),
                          ("qty",self.t("qty"),42)]:
            tree.heading(c, text=txt); tree.column(c, width=w, anchor=tk.CENTER if w<80 else tk.W)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        if not matches:
            ttk.Label(dlg, text=self.t("resolve_none"), foreground=C["fg_dim"]).pack(pady=10)
        for pi, p in matches:
            eff = _effective(p)
            tree.insert("", tk.END, iid=str(pi), values=(
                p.get("brand",""), p.get("name",""), self._ttype(p.get("type","")),
                f'{p.get("optical_length",0):.1f}',
                f'{eff.get("tside_thread","")} {eff.get("tside_gender","")}'.strip(),
                f'{eff.get("cside_thread","")} {eff.get("cside_gender","")}'.strip(),
                p.get("qty",0)))
        def replace():
            sel = tree.selection()
            if not sel: return
            part = copy.deepcopy(self.data["parts"][int(sel[0])]); part["flipped"] = False
            stack[gi] = part
            self._save(); self._refresh_stack(); dlg.destroy()
        tree.bind("<Double-1>", lambda _: replace())
        bf = ttk.Frame(dlg); bf.pack(pady=10)
        ttk.Button(bf, text=self.t("insert"), command=replace,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, replace); _center_dlg(dlg, self.root)

    # ── pick part ──
    def _pick_part_dlg(self, ci):
        dlg = tk.Toplevel(self.root); dlg.title(self.t("add_to_stack"))
        dlg.geometry("850x520"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        ftop = ttk.Frame(dlg); ftop.pack(fill=tk.X, padx=10, pady=6)
        sv = tk.StringVar()
        ttk.Label(ftop, text=self.t("search")).pack(side=tk.LEFT)
        ttk.Entry(ftop, textvariable=sv, width=22).pack(side=tk.LEFT, padx=6)
        ov = tk.BooleanVar(value=True)
        ttk.Checkbutton(ftop, text=self.t("filter_owned"), variable=ov,
                        command=lambda: refresh()).pack(side=tk.LEFT, padx=10)
        cols = ("brand","name","type","mm","t_conn","c_conn")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        for c, txt, w in [("brand",self.t("part_brand"),85),("name",self.t("part_name"),220),
                          ("type",self.t("part_type"),110),("mm","mm",55),
                          ("t_conn",self.t("tside"),150),("c_conn",self.t("cside"),150)]:
            tree.heading(c, text=txt); tree.column(c, width=w, anchor=tk.CENTER if w<80 else tk.W)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        _pick_search_after = [None]
        def refresh(*_):
            tree.delete(*tree.get_children())
            s = sv.get().lower()
            owned_only = ov.get()
            count = 0
            for j, search_text, p in self._get_parts_search_cache():
                if owned_only and p.get("qty",0) <= 0: continue
                if s and s not in search_text: continue
                tree.insert("", tk.END, iid=str(j), values=(
                    p.get("brand",""), p.get("name",""), self._ttype(p.get("type","")),
                    f'{p.get("optical_length",0):.1f}',
                    f'{p.get("tside_thread","")} {p.get("tside_gender","")}'.strip(),
                    f'{p.get("cside_thread","")} {p.get("cside_gender","")}'.strip()))
                count += 1
                if count >= 500:
                    break
        def _debounced_refresh(*_):
            if _pick_search_after[0]:
                dlg.after_cancel(_pick_search_after[0])
            _pick_search_after[0] = dlg.after(200, refresh)
        sv.trace_add("write", _debounced_refresh); refresh()
        def add():
            sel = tree.selection()
            if not sel: return
            pidx = int(sel[0])
            part = copy.deepcopy(self.data["parts"][pidx]); part["flipped"] = False
            if not self._conflict_ok_with_adjust(part, pidx): return
            stack = self.data["configurations"][ci]["stack"]
            ins = len(stack)
            cc = self._check_conn(stack, ins, part)
            if cc == "ghost":
                ghost = self._make_ghost(stack, ins)
                stack.append(ghost); stack.append(part)
            elif cc == "flip":
                part["flipped"] = not part.get("flipped", False)
                stack.append(part)
            elif cc == "mark_flip":
                part["reversible"] = True
                part["flipped"] = not part.get("flipped", False)
                self.data["parts"][pidx]["reversible"] = True
                stack.append(part)
            elif cc == "edit":
                stack.append(part)
                self._save(); self._refresh_stack(); dlg.destroy()
                self.stree.selection_set(str(len(stack) - 1))
                self._stack_edit()
                return
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
            self._save(); self._refresh_stack(); dlg.destroy()
        tree.bind("<Double-1>", lambda _: add())
        bf = ttk.Frame(dlg); bf.pack(pady=10)
        ttk.Button(bf, text=self.t("insert"), command=add, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, add); _center_dlg(dlg, self.root)

    def _conflict_ok(self, part):
        nm = part.get("name",""); qty = part.get("qty",0)
        for p in self.data["parts"]:
            if p.get("name") == nm: qty = p.get("qty",0); break
        if qty <= 0: return True
        total = 0; names = []
        for cfg in self.data["configurations"]:
            for item in cfg.get("stack",[]):
                if item.get("name") == nm:
                    total += 1
                    if cfg["name"] not in names: names.append(cfg["name"])
                    break
        if total >= qty and names:
            return messagebox.askyesno(self.t("conflict_title"),
                self.t("conflict_msg",name=nm,cfgs=", ".join(names),qty=qty,used=total))
        return True

    # ── drag-and-drop handler ──
    def _handle_catalog_drop(self, part_idx):
        """Handle a part dropped from the catalog onto the train."""
        ci = self._cfg_idx()
        if ci is None:
            messagebox.showinfo("", self.t("no_config")); return
        if part_idx >= len(self.data["parts"]): return
        part = copy.deepcopy(self.data["parts"][part_idx])
        part["flipped"] = False
        # Check quantity conflict with adjustment popup
        if not self._conflict_ok_with_adjust(part, part_idx): return
        cfg = self.data["configurations"][ci]
        be = cfg.get("bf_end_idx", -1)
        ins_idx = (be + 1) if be >= 0 else len(cfg["stack"])
        cc = self._check_conn(cfg["stack"], ins_idx, part)
        def _shift_bf(idx, count=1):
            for mk in ("bf_start_idx", "bf_end_idx"):
                if cfg.get(mk, -1) >= idx:
                    cfg[mk] = cfg[mk] + count
        if cc == "ghost":
            ghost = self._make_ghost(cfg["stack"], ins_idx)
            cfg["stack"].insert(ins_idx, ghost)
            _shift_bf(ins_idx)
            cfg["stack"].insert(ins_idx + 1, part)
            _shift_bf(ins_idx + 1)
            added_idx = ins_idx + 1
        elif cc == "flip":
            part["flipped"] = not part.get("flipped", False)
            cfg["stack"].insert(ins_idx, part)
            _shift_bf(ins_idx)
            added_idx = ins_idx
        elif cc == "mark_flip":
            part["reversible"] = True
            part["flipped"] = not part.get("flipped", False)
            self.data["parts"][part_idx]["reversible"] = True
            cfg["stack"].insert(ins_idx, part)
            _shift_bf(ins_idx)
            added_idx = ins_idx
        elif cc == "edit":
            cfg["stack"].insert(ins_idx, part)
            _shift_bf(ins_idx)
            self._save(); self._refresh_stack()
            self.stree.selection_set(str(ins_idx))
            self._stack_edit()
            return
        elif cc:
            cfg["stack"].insert(ins_idx, part)
            _shift_bf(ins_idx)
            added_idx = ins_idx
        else:
            return
        # Auto-detect bf_role
        if part.get("bf_role") == "start" and cfg.get("bf_start_idx", -1) < 0:
            cfg["bf_start_idx"] = added_idx
        elif part.get("bf_role") == "end" and cfg.get("bf_end_idx", -1) < 0:
            cfg["bf_end_idx"] = added_idx
        self._save(); self._refresh_stack()

    def _conflict_ok_with_adjust(self, part, part_idx):
        """Check qty conflict; if exceeded or not owned, offer a popup to adjust quantity."""
        nm = part.get("name","")
        qty = self.data["parts"][part_idx].get("qty", 0)
        # Count total usage across all configurations
        total = 0; cfgs_used = []
        for cfg in self.data["configurations"]:
            count_in = sum(1 for item in cfg.get("stack",[]) if item.get("name") == nm)
            if count_in > 0:
                total += count_in
                cfgs_used.append(cfg["name"])
        if qty > 0 and total + 1 <= qty:
            return True  # still within owned quantity
        # Not owned or quantity exceeded -> show adjustment popup
        new_qty = max(total + 1, 1)
        dlg = tk.Toplevel(self.root); dlg.title(self.t("qty_adjust_title"))
        dlg.geometry("440x240"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        result = [False]
        if qty <= 0:
            msg = self.t("qty_not_owned_msg", name=nm)
        else:
            msg = self.t("qty_adjust_msg", name=nm, used=total, qty=qty, new_qty=new_qty)
        ttk.Label(dlg, text=msg, wraplength=400, justify=tk.LEFT).pack(padx=16, pady=(16,8))
        # Custom quantity entry
        qf = ttk.Frame(dlg); qf.pack(padx=16, pady=4, anchor=tk.W)
        ttk.Label(qf, text=self.t("qty_adjust_custom")).pack(side=tk.LEFT)
        qv = tk.StringVar(value=str(new_qty))
        ttk.Button(qf, text="\u2212", width=2, style="Small.TButton",
                   command=lambda: qv.set(str(max(1, _safe_int(qv.get(), 1)-1)))).pack(side=tk.LEFT, padx=(6,2))
        ttk.Entry(qf, textvariable=qv, width=4).pack(side=tk.LEFT)
        ttk.Button(qf, text="+", width=2, style="Small.TButton",
                   command=lambda: qv.set(str(_safe_int(qv.get(), 1)+1))).pack(side=tk.LEFT, padx=(2,0))
        # Info: used in configs
        if cfgs_used:
            info = ", ".join(cfgs_used)
            ttk.Label(dlg, text=f"({info})", foreground=C["fg_dim"],
                      wraplength=400).pack(padx=16, pady=2, anchor=tk.W)
        bf = ttk.Frame(dlg); bf.pack(pady=16)
        def accept():
            try: nq = max(1, int(qv.get()))
            except ValueError: nq = new_qty
            self.data["parts"][part_idx]["qty"] = nq
            self._save()
            if self._catalog_win and self._catalog_win.win.winfo_exists():
                self._catalog_win._refresh()
            result[0] = True; dlg.destroy()
        def add_anyway():
            result[0] = True; dlg.destroy()
        def cancel():
            result[0] = False; dlg.destroy()
        ttk.Button(bf, text=self.t("ok") + " + " + self.t("qty"),
                   command=accept, style="Accent.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("insert"),
                   command=add_anyway).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("cancel"), command=cancel).pack(side=tk.LEFT, padx=4)
        _bind_dlg_keys(dlg, accept); _center_dlg(dlg, self.root)
        dlg.wait_window()
        return result[0]

    def _check_conn(self, stack, ins_idx, part):
        """Check connection compatibility. Returns True, False, or 'ghost'."""
        eff_new = _effective(part)
        problems = []
        # Check left neighbor (previous piece's cside → new piece's tside)
        if ins_idx > 0:
            prev = stack[ins_idx - 1]
            eff_prev = _effective(prev)
            t_a, g_a = eff_prev.get("cside_thread",""), eff_prev.get("cside_gender","")
            t_b, g_b = eff_new.get("tside_thread",""), eff_new.get("tside_gender","")
            if t_a and t_b:
                if _extract_diam(t_a) != _extract_diam(t_b):
                    reason = self.t("conn_reason_thread", a=t_a, b=t_b)
                    problems.append((prev, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(), reason))
                elif g_a and g_b and g_a == g_b:
                    reason = self.t("conn_reason_gender", g=g_a)
                    problems.append((prev, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(), reason))
        # Check right neighbor (new piece's cside → next piece's tside)
        if ins_idx < len(stack):
            nxt = stack[ins_idx]
            eff_nxt = _effective(nxt)
            t_a, g_a = eff_new.get("cside_thread",""), eff_new.get("cside_gender","")
            t_b, g_b = eff_nxt.get("tside_thread",""), eff_nxt.get("tside_gender","")
            if t_a and t_b:
                if _extract_diam(t_a) != _extract_diam(t_b):
                    reason = self.t("conn_reason_thread", a=t_a, b=t_b)
                    problems.append((part, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(), reason))
                elif g_a and g_b and g_a == g_b:
                    reason = self.t("conn_reason_gender", g=g_a)
                    problems.append((part, f"{t_a} {g_a}".strip(), f"{t_b} {g_b}".strip(), reason))
        if not problems:
            return True
        # Try flipped version if type allows it
        flip_fixes = False
        if part.get("type") not in NOT_REVERSIBLE:
            flipped_part = dict(part, flipped=not part.get("flipped", False))
            eff_flip = _effective(flipped_part)
            flip_problems = []
            if ins_idx > 0:
                prev = stack[ins_idx - 1]
                eff_prev = _effective(prev)
                t_a, g_a = eff_prev.get("cside_thread",""), eff_prev.get("cside_gender","")
                t_b, g_b = eff_flip.get("tside_thread",""), eff_flip.get("tside_gender","")
                if t_a and t_b:
                    if _extract_diam(t_a) != _extract_diam(t_b):
                        flip_problems.append(True)
                    elif g_a and g_b and g_a == g_b:
                        flip_problems.append(True)
            if ins_idx < len(stack):
                nxt = stack[ins_idx]
                eff_nxt = _effective(nxt)
                t_a, g_a = eff_flip.get("cside_thread",""), eff_flip.get("cside_gender","")
                t_b, g_b = eff_nxt.get("tside_thread",""), eff_nxt.get("tside_gender","")
                if t_a and t_b:
                    if _extract_diam(t_a) != _extract_diam(t_b):
                        flip_problems.append(True)
                    elif g_a and g_b and g_a == g_b:
                        flip_problems.append(True)
            flip_fixes = len(flip_problems) == 0
        # Dialog: Flip & insert / Insert anyway / Insert ghost / Edit part / Cancel
        p_item, p_out, p_in, reason = problems[0]
        prev_name = f'{p_item.get("brand","")} {p_item.get("name","")}'.strip()
        new_name = f'{part.get("brand","")} {part.get("name","")}'.strip()
        msg = self.t("conn_warn_msg", prev_name=prev_name, prev_conn=p_out,
                      new_name=new_name, new_conn=p_in, reason=reason)
        dlg = tk.Toplevel(self.root); dlg.title(self.t("conn_warn_title"))
        dlg.geometry("560x280"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.configure(bg=C["bg_mid"])
        result = [False]
        ttk.Label(dlg, text=msg, wraplength=520, justify=tk.LEFT).pack(padx=16, pady=(16,10))
        bf = ttk.Frame(dlg); bf.pack(pady=12)
        def do_flip():
            result[0] = "flip"; dlg.destroy()
        def do_mark_flip():
            result[0] = "mark_flip"; dlg.destroy()
        def do_insert():
            result[0] = True; dlg.destroy()
        def do_ghost():
            result[0] = "ghost"; dlg.destroy()
        def do_edit():
            result[0] = "edit"; dlg.destroy()
        def do_cancel():
            result[0] = False; dlg.destroy()
        if flip_fixes and part.get("reversible"):
            ttk.Button(bf, text=self.t("conn_flip_insert"), command=do_flip,
                       style="Accent.TButton").pack(side=tk.LEFT, padx=4)
        elif flip_fixes:
            ttk.Button(bf, text=self.t("conn_mark_flip"), command=do_mark_flip,
                       style="Accent.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("insert"), command=do_insert).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("conn_insert_ghost"), command=do_ghost).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("conn_edit_part"), command=do_edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=self.t("cancel"), command=do_cancel).pack(side=tk.LEFT, padx=4)
        dlg.bind("<Escape>", lambda _: do_cancel())
        _center_dlg(dlg, self.root); dlg.wait_window()
        return result[0]

    def _make_ghost(self, stack, ins_idx):
        """Create a ghost placeholder with connections inferred from neighbors."""
        ghost = {"brand": "", "name": self.t("ghost_name"), "type": "type_adapter",
                 "optical_length": 0, "mass": 0, "ghost": True, "flipped": False,
                 "tside_thread": "", "tside_gender": "", "cside_thread": "", "cside_gender": "",
                 "reversible": False, "bf_role": ""}
        # Left neighbor → ghost tside must accept its cside
        if ins_idx > 0:
            prev = _effective(stack[ins_idx - 1])
            ct, cg = prev.get("cside_thread",""), prev.get("cside_gender","")
            ghost["tside_thread"] = ct
            ghost["tside_gender"] = {"Male":"Female","Female":"Male"}.get(cg, "")
        # Right neighbor → ghost cside must feed its tside
        if ins_idx < len(stack):
            nxt = _effective(stack[ins_idx])
            tt, tg = nxt.get("tside_thread",""), nxt.get("tside_gender","")
            ghost["cside_thread"] = tt
            ghost["cside_gender"] = {"Male":"Female","Female":"Male"}.get(tg, "")
        return ghost

    # ── part dialog ──
    def _part_dlg(self, idx, on_done=None):
        is_edit = idx is not None
        p = self.data["parts"][idx] if is_edit else {
            "brand":"","name":"","type":"type_adapter","optical_length":0,"mass":0,
            "tside_thread":"","tside_gender":"","cside_thread":"","cside_gender":"",
            "reversible":True,"bf_role":"","qty":0,"notes":""}
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("edit_part") if is_edit else self.t("add_part"))
        _saved = self.data.get("ui", {}).get("part_dlg_geometry", "600x740")
        dlg.geometry(_saved); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set()
        dlg.minsize(500, 500)
        dlg.configure(bg=C["bg_mid"])
        r = 0; vars_ = {}
        def _row(label, key, wf, **kw):
            nonlocal r
            ttk.Label(dlg, text=label).grid(row=r, column=0, sticky=tk.W, padx=10, pady=4)
            w, var = wf(dlg, r, kw); vars_[key] = var; r += 1; return w
        def _entry(par, row, kw):
            v = tk.StringVar(value=str(kw.get("val",""))); e = ttk.Entry(par, textvariable=v, width=kw.get("w",30))
            e.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4); return e, v
        def _combo(par, row, kw):
            v = tk.StringVar(value=kw.get("val",""))
            c = ttk.Combobox(par, textvariable=v, values=kw.get("vals",[]),
                             state="readonly" if kw.get("ro") else "normal", width=kw.get("w",20))
            c.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4); return c, v
        def _check(par, row, kw):
            v = tk.BooleanVar(value=kw.get("val",False)); c = ttk.Checkbutton(par, variable=v)
            c.grid(row=row, column=1, sticky=tk.W, padx=10, pady=4); return c, v

        # brand + auto-fill
        ttk.Label(dlg, text=self.t("part_brand")).grid(row=r, column=0, sticky=tk.W, padx=10, pady=4)
        brand_var = tk.StringVar(value=p.get("brand",""))
        _all_brands = sorted({"Custom Made"} | _REF_BRANDS | {p.get("brand","") for p in self.data["parts"] if p.get("brand","")})
        bc = ttk.Combobox(dlg, textvariable=brand_var, width=20,
                          values=_all_brands)
        bc.grid(row=r, column=1, sticky=tk.W, padx=10, pady=4); vars_["brand"] = brand_var
        def _autofill():
            q = (brand_var.get().lower()+" "+vars_.get("name",tk.StringVar()).get().lower()).strip()
            if not q: return
            # Fast lookup: try exact match first, then prefix via bisect, then substring fallback
            ref = _REF_INDEX.get(q)
            if ref is None:
                # Prefix search via sorted keys
                idx = bisect.bisect_left(_REF_KEYS_SORTED, q)
                if idx < len(_REF_KEYS_SORTED) and _REF_KEYS_SORTED[idx].startswith(q):
                    ref = _REF_INDEX[_REF_KEYS_SORTED[idx]]
                else:
                    # Substring fallback (only if prefix fails)
                    for k in _REF_KEYS_SORTED:
                        if q in k:
                            ref = _REF_INDEX[k]; break
            if ref is None: return
            for k, vk in [("brand","brand"),("name","name"),("optical_length","mm"),("mass","mass")]:
                if vk in vars_: vars_[vk].set(str(ref.get(k,"")))
            if "type" in vars_: vars_["type"].set(self._ttype(ref.get("type","")))
            for side in ("tside_thread","tside_gender","cside_thread","cside_gender"):
                if side in vars_: vars_[side].set(ref.get(side,""))
            if "reversible" in vars_: vars_["reversible"].set(ref.get("reversible",False))
            if "bf_role" in vars_: vars_["bf_role"].set(ref.get("bf_role",""))
        af_btn = ttk.Button(dlg, text="Auto-fill", command=_autofill, style="Accent.TButton")
        af_btn.grid(row=r, column=2, padx=6, pady=4)
        self._tip(af_btn, "Auto-fill fields from product database", "Remplir depuis la base de produits")
        r += 1

        _row(self.t("part_name"), "name", _entry, val=p.get("name",""), w=30)
        type_map = {self._ttype(k): k for k in PART_TYPES}
        _row(self.t("part_type"), "type", _combo, val=self._ttype(p.get("type","")),
             vals=sorted(type_map.keys()), ro=True, w=18)
        _row(self.t("optical_length"), "mm", _entry, val=p.get("optical_length",0), w=10)
        _row(self.t("mass_label"), "mass", _entry, val=p.get("mass",0), w=10)
        _row(self.t("reversible"), "reversible", _check, val=p.get("reversible",False))
        _row(self.t("bf_role"), "bf_role", _combo, val=p.get("bf_role",""), vals=["","start","end"], w=10)

        ttk.Separator(dlg, orient=tk.HORIZONTAL).grid(row=r, column=0, columnspan=3, sticky=tk.EW, padx=10, pady=8); r += 1
        ttk.Label(dlg, text=self.t("tside"), style="Section.TLabel").grid(row=r, column=0, columnspan=3, sticky=tk.W, padx=10); r += 1
        _row(self.t("thread"), "tside_thread", _combo, val=p.get("tside_thread",""), vals=THREADS, w=22)
        _row(self.t("gender"), "tside_gender", _combo, val=p.get("tside_gender",""), vals=GENDERS, ro=True, w=10)
        ttk.Label(dlg, text=self.t("cside"), style="Section.TLabel").grid(row=r, column=0, columnspan=3, sticky=tk.W, padx=10); r += 1
        _row(self.t("thread"), "cside_thread", _combo, val=p.get("cside_thread",""), vals=THREADS, w=22)
        _row(self.t("gender"), "cside_gender", _combo, val=p.get("cside_gender",""), vals=GENDERS, ro=True, w=10)

        ttk.Separator(dlg, orient=tk.HORIZONTAL).grid(row=r, column=0, columnspan=3, sticky=tk.EW, padx=10, pady=8); r += 1
        ttk.Label(dlg, text=self.t("qty")).grid(row=r, column=0, sticky=tk.W, padx=10, pady=4)
        _qf = ttk.Frame(dlg); _qf.grid(row=r, column=1, columnspan=2, sticky=tk.W, padx=10, pady=4)
        _qv = tk.StringVar(value=str(p.get("qty", 0))); vars_["qty"] = _qv
        ttk.Button(_qf, text="\u2212", width=2, style="Small.TButton",
                   command=lambda: _qv.set(str(max(0, _safe_int(_qv.get())-1)))).pack(side=tk.LEFT, padx=(0,2))
        ttk.Entry(_qf, textvariable=_qv, width=4).pack(side=tk.LEFT)
        ttk.Button(_qf, text="+", width=2, style="Small.TButton",
                   command=lambda: _qv.set(str(_safe_int(_qv.get())+1))).pack(side=tk.LEFT, padx=(2,0))
        r += 1
        _row(self.t("part_notes"), "notes", _entry, val=p.get("notes",""), w=40)

        def _save():
            try: ol = float(str(vars_["mm"].get()).replace(",","."))
            except ValueError: ol = 0
            try: ms = float(str(vars_["mass"].get()).replace(",","."))
            except ValueError: ms = 0
            try: q = max(0, int(vars_["qty"].get()))
            except ValueError: q = 0
            td = type_map.get(vars_["type"].get(), "type_adapter")
            np = {"brand": vars_["brand"].get().strip(), "name": vars_["name"].get().strip(),
                  "type": td, "optical_length": ol, "mass": ms,
                  "reversible": vars_["reversible"].get(), "bf_role": vars_["bf_role"].get(),
                  "tside_thread": vars_["tside_thread"].get().strip(),
                  "tside_gender": vars_["tside_gender"].get(),
                  "cside_thread": vars_["cside_thread"].get().strip(),
                  "cside_gender": vars_["cside_gender"].get(),
                  "qty": q, "notes": vars_["notes"].get().strip()}
            if not np["name"]: return
            if is_edit: self.data["parts"][idx] = np
            else: self.data["parts"].append(np)
            self._save()
            if on_done: on_done()
            _close_dlg()
        def _close_dlg():
            self.data.setdefault("ui", {})["part_dlg_geometry"] = dlg.geometry()
            dlg.destroy()
        bf = ttk.Frame(dlg); bf.grid(row=r, column=0, columnspan=3, pady=12)
        ttk.Button(bf, text=self.t("save"), command=_save, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=_close_dlg).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg); _center_dlg(dlg, self.root)

    # ── calc ──
    def _calc(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack",[])
        total = sum(it.get("optical_length",0) for it in stack)
        lu = self.data.get("length_unit","mm")
        try: target = float(self.v_target.get().replace(",","."))
        except ValueError: target = 0
        bs = cfg.get("bf_start_idx",-1); be = cfg.get("bf_end_idx",-1)
        bf_total = sum(stack[j].get("optical_length",0) for j in range(bs+1,be+1)) if 0<=bs<=be<len(stack) else total
        diff = bf_total - target
        self.lbl_total.config(text=f'{self.t("total_label")} {_fmt_len(total,lu)}')
        if 0 <= bs <= be < len(stack):
            start_name = stack[bs].get("name", "?")[:20]
            end_name = stack[be].get("name", "?")[:20]
            bf_text = f'{self.t("bf_total_label")} {_fmt_len(bf_total,lu)}  ({start_name} \u2192 {end_name})'
        else:
            bf_text = f'{self.t("bf_total_label")} {_fmt_len(bf_total,lu)}'
        self.lbl_bf.config(text=bf_text)
        if abs(diff) < 0.1:
            self.lbl_diff.config(text=f'{self.t("diff_label")} {self.t("status_ok")}', foreground=C["accent_green"])
        elif diff > 0:
            self.lbl_diff.config(text=f'{self.t("diff_label")} {self.t("status_long",v=abs(diff))} {lu}', foreground=C["accent_red"])
        else:
            self.lbl_diff.config(text=f'{self.t("diff_label")} {self.t("status_short",v=abs(diff))} {lu}', foreground=C["accent_orange"])
        self._save_cfg(); self._draw(stack, bf_total, target, bs, be)

    @staticmethod
    def _rrect(c, x1, y1, x2, y2, r=6, **kw):
        """Draw a rounded rectangle on canvas *c*."""
        r = min(r, abs(x2-x1)/2, abs(y2-y1)/2)
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
               x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
               x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
        return c.create_polygon(pts, smooth=True, **kw)

    def _on_root_configure(self, event):
        """Debounce diagram redraw during window resize."""
        if event.widget is not self.root:
            return
        if self._win_resize_after:
            self.root.after_cancel(self._win_resize_after)
        self._win_resize_after = self.root.after(60, self._on_resize_done)

    def _on_resize_done(self):
        """Redraw diagram after resize settles."""
        self._win_resize_after = None
        if self._last_draw_args:
            self._redraw_from_cache()

    def _on_canvas_resize(self, event):
        """Redraw diagram when canvas is resized."""
        if self._last_draw_args is None:
            return
        w, h = event.width, event.height
        if (w, h) == self._last_canvas_size:
            return  # no actual size change
        self._last_canvas_size = (w, h)
        # Debounce: cancel pending redraw, schedule a new one
        if self._resize_after_id:
            self.canvas.after_cancel(self._resize_after_id)
        self._resize_after_id = self.canvas.after(60, self._redraw_from_cache)

    def _redraw_from_cache(self):
        """Redraw using cached arguments."""
        self._resize_after_id = None
        if self._last_draw_args:
            self._draw(*self._last_draw_args)

    def _draw(self, stack, bf_total, target, bs, be):
        self._last_draw_args = (stack, bf_total, target, bs, be)
        c = self.canvas
        W, H = c.winfo_width(), c.winfo_height()
        if W < 50 or H < 10:
            # Canvas not laid out yet — reschedule
            c.after(50, lambda: self._draw(stack, bf_total, target, bs, be))
            return
        # Batch: suppress redraws until all items are placed
        c.delete("all")
        self._diag_ranges = []
        if not stack:
            c.create_text(W/2,H/2,text="\u2014",fill=C["fg_dim"],font=(FONT_FAMILY,10)); return
        margin = 18; avail = W - 2*margin
        vis_total = sum(max(it.get("optical_length",0),2) for it in stack)
        # Scale relative to target backfocus (with 10% margin), not just the sum of parts
        if target > 0:
            ref = max(target * 1.10, vis_total * 1.05)
        else:
            ref = vis_total  # fallback: no target defined, fill space as before
        x = margin; bh = 42; yt = (H-bh)/2
        cr = c.create_rectangle
        for si, item in enumerate(stack):
            ol = max(item.get("optical_length",0),2)
            bw = max(ol/ref*avail,8) if ref>0 else 12
            is_ghost = item.get("ghost", False)
            col = C["accent_orange"] if is_ghost else TYPE_COLORS.get(item.get("type",""), C["fg_dim"])
            if 0<=bs<=be and bs<si<=be:
                cr(x-1,yt-5,x+bw+1,yt+bh+5,
                   fill=C["bf_zone"], outline="", width=0)
            if is_ghost:
                cr(x,yt,x+bw,yt+bh, fill="", outline=C["accent_orange"], dash=(4,3))
                c.create_text(x+bw/2,yt+bh/2,text="?",font=(FONT_FAMILY,12,"bold"),fill=C["accent_orange"])
            else:
                cr(x+1,yt+1,x+bw-1,yt+bh-1, fill=col, outline="", width=0)
                cr(x,yt,x+bw,yt+bh, fill="", outline=C["border"])
                if bw > 24:
                    c.create_text(x+bw/2,yt+bh/2,text=item.get("name","")[:16],font=(FONT_FAMILY,7),fill=C["bg_dark"])
            c.create_text(x+bw/2,yt+bh+12,text=f'{item.get("optical_length",0):.1f}',font=(FONT_FAMILY,7),fill=C["fg_dim"])
            self._diag_ranges.append((x, x+bw, si))
            x += bw
        c.create_text(margin,yt-12,text="Telescope",font=(FONT_FAMILY,7),fill=C["fg_dim"],anchor=tk.W)
        c.create_text(W-margin,yt-12,text="Camera",font=(FONT_FAMILY,7),fill=C["fg_dim"],anchor=tk.E)
        if 0 <= bs <= be and len(self._diag_ranges) > max(bs, be):
            bx1 = self._diag_ranges[bs][1]   # right edge of BF start piece
            bx2 = self._diag_ranges[be][0]   # left edge of BF end piece
            mid = (bx1 + bx2) / 2
            c.create_text(mid, yt - 12, text="BF", font=(FONT_FAMILY, 8, "bold"),
                          fill=C["accent_green"])
            c.create_line(bx1, yt - 8, bx2, yt - 8, fill=C["accent_green"],
                          width=1, dash=(3, 2))
        if target > 0 and ref > 0:
            tx = margin + (target/ref)*avail
            if margin < tx < W-margin:
                c.create_line(tx,yt-6,tx,yt+bh+6,fill=C["accent_red"],width=2,dash=(4,3))

    # ── suggest ──
    def _suggest(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack",[])
        try: target = float(self.v_target.get().replace(",","."))
        except ValueError: return
        bs = cfg.get("bf_start_idx",-1); be = cfg.get("bf_end_idx",-1)
        bf_total = sum(stack[j].get("optical_length",0) for j in range(bs+1,be+1)) if 0<=bs<=be<len(stack) else sum(it.get("optical_length",0) for it in stack)
        gap = target - bf_total
        if abs(gap) < 0.05:
            messagebox.showinfo(self.t("auto_suggest"), self.t("status_ok")); return
        last_idx = be if be>=0 else len(stack)-1
        last_cs = last_cg = ""
        if 0 <= last_idx < len(stack):
            eff = _effective(stack[last_idx]); last_cs = eff.get("cside_thread",""); last_cg = eff.get("cside_gender","")
        cands = []
        for pi, p in enumerate(self.data["parts"]):
            if p.get("optical_length",0) <= 0 or p.get("type") in ("type_telescope","type_refractor"): continue
            if p.get("qty",0) <= 0: continue
            if last_cs and p.get("tside_thread"):
                if not _conn_compat(last_cs,last_cg,p.get("tside_thread",""),p.get("tside_gender","")): continue
            ng = gap - p["optical_length"]
            cands.append({"name":f'{p.get("brand","")} {p["name"]}'.strip(),"length":p["optical_length"],
                          "new_gap":ng,"part_idx":pi})
        cands.sort(key=lambda cd: abs(cd["new_gap"]))
        dlg = tk.Toplevel(self.root); dlg.title(self.t("suggest_title"))
        dlg.geometry("640x420"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set(); dlg.configure(bg=C["bg_mid"])
        ttk.Label(dlg, text=self.t("suggest_gap",v=gap), style="Result.TLabel").pack(padx=10,pady=6)
        if not cands:
            ttk.Label(dlg, text=self.t("suggest_none")).pack(padx=10,pady=20)
            ttk.Button(dlg, text=self.t("cancel"), command=dlg.destroy).pack(pady=10); return
        cols = ("name","mm","after")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        tree.heading("name",text=self.t("part_name")); tree.heading("mm",text="mm"); tree.heading("after",text=self.t("suggest_after"))
        tree.column("name",width=320); tree.column("mm",width=80,anchor=tk.CENTER); tree.column("after",width=130,anchor=tk.CENTER)
        tree.tag_configure("perfect", background="#244030", foreground=C["accent_green"])
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        for j, cd in enumerate(cands[:40]):
            at = self.t("suggest_perfect") if abs(cd["new_gap"])<0.05 else f'{cd["new_gap"]:+.2f} mm'
            tree.insert("",tk.END,iid=str(j),values=(cd["name"],f'{cd["length"]:.1f}',at),
                        tags=("perfect",) if abs(cd["new_gap"])<0.05 else ())
        def ins():
            sel = tree.selection()
            if not sel: return
            cd = cands[int(sel[0])]; part = copy.deepcopy(self.data["parts"][cd["part_idx"]]); part["flipped"] = False
            # Replace first ghost in BF zone if any, otherwise insert before end
            ghost_idx = None
            lo = (bs+1 if bs >= 0 else 0); hi = (be if be >= 0 else len(cfg["stack"]))
            for gi in range(lo, hi):
                if gi < len(cfg["stack"]) and cfg["stack"][gi].get("ghost"):
                    ghost_idx = gi; break
            if ghost_idx is not None:
                cfg["stack"][ghost_idx] = part
            else:
                ins_idx = be if be >= 0 else len(cfg["stack"])
                cfg["stack"].insert(ins_idx, part)
                for mk in ("bf_start_idx", "bf_end_idx"):
                    if cfg.get(mk, -1) >= ins_idx:
                        cfg[mk] = cfg[mk] + 1
            self._save(); self._refresh_stack(); dlg.destroy()
        tree.bind("<Double-1>", lambda _: ins())
        bf = ttk.Frame(dlg); bf.pack(pady=10)
        ttk.Button(bf, text=self.t("insert"), command=ins, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, ins); _center_dlg(dlg, self.root)

    # ── auto-complete ──
    def _auto_complete(self):
        ci = self._cfg_idx()
        if ci is None: return
        cfg = self.data["configurations"][ci]; stack = cfg.get("stack",[])
        bs = cfg.get("bf_start_idx",-1); be = cfg.get("bf_end_idx",-1)
        # Require both BF start and BF end to be set
        if bs < 0 or be < 0 or bs >= len(stack) or be >= len(stack):
            messagebox.showinfo(self.t("auto_complete"), self.t("ac_need_bf")); return
        try: target = float(self.v_target.get().replace(",","."))
        except ValueError: return
        bf_total = sum(stack[j].get("optical_length",0) for j in range(bs+1,be+1))
        gap = target - bf_total
        if abs(gap) < 0.1:
            messagebox.showinfo(self.t("auto_complete"), self.t("status_ok")); return
        dlg = tk.Toplevel(self.root); dlg.title(self.t("ac_title"))
        dlg.geometry("700x520"); dlg.transient(self.root); dlg.wait_visibility(); dlg.grab_set(); dlg.configure(bg=C["bg_mid"])
        ttk.Label(dlg, text=self.t("suggest_gap",v=gap), style="Result.TLabel").pack(padx=10,pady=6)
        chk_f = ttk.Frame(dlg); chk_f.pack(padx=10, anchor=tk.W)
        use_other = tk.BooleanVar(value=False)
        ttk.Checkbutton(chk_f, text=self.t("ac_use_other"), variable=use_other,
                        command=lambda: search()).pack(anchor=tk.W, pady=2)
        use_unowned = tk.BooleanVar(value=False)
        ttk.Checkbutton(chk_f, text=self.t("ac_use_unowned"), variable=use_unowned,
                        command=lambda: search()).pack(anchor=tk.W, pady=2)
        rf = ttk.Frame(dlg); rf.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        cols = ("combo","total_mm","remaining")
        rtree = ttk.Treeview(rf, columns=cols, show="headings", selectmode="browse")
        rtree.heading("combo",text="Combination"); rtree.heading("total_mm",text="mm"); rtree.heading("remaining",text=self.t("diff_label"))
        rtree.column("combo",width=420); rtree.column("total_mm",width=80,anchor=tk.CENTER); rtree.column("remaining",width=110,anchor=tk.CENTER)
        rtree.tag_configure("perfect", background="#244030", foreground=C["accent_green"])
        rtree.pack(fill=tk.BOTH, expand=True)
        solutions = []
        def search():
            nonlocal solutions
            rtree.delete(*rtree.get_children()); solutions = []
            candidates = []; used_names = set()
            if not use_other.get():
                for ocfg in self.data["configurations"]:
                    if ocfg is cfg: continue
                    for item in ocfg.get("stack",[]): used_names.add(item.get("name",""))
            for pi, p in enumerate(self.data["parts"]):
                if not use_unowned.get() and p.get("qty",0) <= 0: continue
                if p.get("optical_length",0) <= 0: continue
                if p.get("type") in ("type_telescope","type_refractor","type_camera","type_dslr"): continue
                if not use_other.get() and p.get("name","") in used_names: continue
                candidates.append((pi, p))
            if not candidates: return
            # Pre-sort by optical_length for early pruning
            candidates.sort(key=lambda x: x[1]["optical_length"])
            abs_gap = abs(gap)
            max_useful = abs_gap * 1.5  # max total length worth considering
            tolerance = 0.5
            # Size 1: simple loop with early termination (sorted)
            for pi, p in candidates:
                ol = p["optical_length"]
                rem = gap - ol
                if abs(rem) < abs_gap * 1.5:
                    names = f'{p.get("brand","")} {p["name"]}'.strip()
                    solutions.append((names, rem, ol, [pi]))
            solutions.sort(key=lambda s: abs(s[1]))
            if solutions and abs(solutions[0][1]) < tolerance:
                pass  # skip combos of 2 and 3
            else:
                # Size 2: two-pointer pruning on sorted list
                n = len(candidates)
                for i in range(n):
                    ol_i = candidates[i][1]["optical_length"]
                    if ol_i > max_useful: break  # remaining are all larger
                    for j in range(i+1, n):
                        total_l = ol_i + candidates[j][1]["optical_length"]
                        if total_l > max_useful and gap > 0: break
                        rem = gap - total_l
                        if abs(rem) < abs_gap * 1.5:
                            names = " + ".join(f'{candidates[k][1].get("brand","")} {candidates[k][1]["name"]}'.strip() for k in (i,j))
                            solutions.append((names, rem, total_l, [candidates[i][0], candidates[j][0]]))
                solutions.sort(key=lambda s: abs(s[1]))
                if not (solutions and abs(solutions[0][1]) < tolerance) and n <= 200:
                    # Size 3: only if no perfect found yet and reasonable count
                    count3 = 0
                    for i in range(n):
                        ol_i = candidates[i][1]["optical_length"]
                        if ol_i > max_useful: break
                        for j in range(i+1, n):
                            ol_ij = ol_i + candidates[j][1]["optical_length"]
                            if ol_ij > max_useful and gap > 0: break
                            for k in range(j+1, n):
                                total_l = ol_ij + candidates[k][1]["optical_length"]
                                if total_l > max_useful and gap > 0: break
                                rem = gap - total_l
                                if abs(rem) < abs_gap * 1.5:
                                    names = " + ".join(f'{candidates[m][1].get("brand","")} {candidates[m][1]["name"]}'.strip() for m in (i,j,k))
                                    solutions.append((names, rem, total_l, [candidates[i][0], candidates[j][0], candidates[k][0]]))
                                    count3 += 1
                                    if count3 > 500: break  # hard limit
                            if count3 > 500: break
                        if count3 > 500: break
            solutions.sort(key=lambda s: abs(s[1]))
            for j, (names, rem, total_l, _) in enumerate(solutions[:30]):
                at = self.t("suggest_perfect") if abs(rem)<0.05 else f'{rem:+.2f} mm'
                rtree.insert("",tk.END,iid=str(j),values=(names,f'{total_l:.1f}',at),
                             tags=("perfect",) if abs(rem)<0.05 else ())
        search()
        def apply_sol():
            sel = rtree.selection()
            if not sel: return
            sol = solutions[int(sel[0])]
            # Collect ghost indices in BF zone for replacement
            lo = (bs+1 if bs >= 0 else 0); hi = (be if be >= 0 else len(cfg["stack"]))
            ghosts = [gi for gi in range(lo, hi) if gi < len(cfg["stack"]) and cfg["stack"][gi].get("ghost")]
            ins_idx = be if be >= 0 else len(cfg["stack"])
            for pi in sol[3]:
                part = copy.deepcopy(self.data["parts"][pi]); part["flipped"] = False
                if ghosts:
                    cfg["stack"][ghosts.pop(0)] = part
                else:
                    cfg["stack"].insert(ins_idx, part)
                    for mk in ("bf_start_idx", "bf_end_idx"):
                        if cfg.get(mk, -1) >= ins_idx:
                            cfg[mk] = cfg[mk] + 1
                    ins_idx += 1
            self._save(); self._refresh_stack(); dlg.destroy()
        rtree.bind("<Double-1>", lambda _: apply_sol())
        bf = ttk.Frame(dlg); bf.pack(pady=10)
        ttk.Button(bf, text=self.t("insert"), command=apply_sol, style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bf, text=self.t("cancel"), command=dlg.destroy).pack(side=tk.LEFT, padx=10)
        _bind_dlg_keys(dlg, apply_sol); _center_dlg(dlg, self.root)

    # ── export / import ──
    def _export(self):
        i = self._cfg_idx()
        if i is None: return
        cfg = self.data["configurations"][i]
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")],
                                            initialfile=cfg["name"]+".json")
        if path:
            try:
                with open(path,"w",encoding="utf-8") as fh: json.dump(cfg, fh, indent=2, ensure_ascii=False)
            except OSError as e:
                messagebox.showerror("Export Error", str(e))

    def _import(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if path:
            try:
                with open(path,"r",encoding="utf-8") as fh: cfg = json.load(fh)
            except (json.JSONDecodeError, OSError):
                messagebox.showerror("Error", "Invalid or unreadable JSON file."); return
            if "name" in cfg and "stack" in cfg:
                self.data["configurations"].append(cfg); self._save(); self._refresh_cfgs()

    def _export_all(self):
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON","*.json")],
                                            initialfile="backfocus_all_data.json")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(self.data, fh, indent=2, ensure_ascii=False)
                messagebox.showinfo(self.t("export_all"), self.t("export_all_ok"))
            except OSError as e:
                messagebox.showerror("Export Error", str(e))

    def _import_all(self):
        if not messagebox.askyesno(self.t("import_all"), self.t("confirm_import_all")):
            return
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    imported = json.load(fh)
            except (json.JSONDecodeError, OSError):
                messagebox.showerror("Error", "Invalid or unreadable JSON file."); return
            for k, v in _default_data().items():
                imported.setdefault(k, v)
            if "parts" in imported and "configurations" in imported:
                self.data = imported
                self.lang = self.data.get("language", "fr")
                self._invalidate_parts_cache()
                save_data(self.data, sync=True)
                self._apply_language()
                self._refresh_cfgs()
                messagebox.showinfo(self.t("import_all"), self.t("import_all_ok"))

    def _save_all(self):
        _save_writer.flush_sync()
        save_data(self.data, sync=True)
        messagebox.showinfo(self.t("save_all"), self.t("save_all_ok"))

    # ── language ──
    def _set_lang(self, lang):
        self.lang = lang; self.data["language"] = lang
        self._save(); self._apply_language()

    def _apply_language(self):
        self.root.title(self.t("app_title"))
        self.menu.delete(0, tk.END)
        mo = dict(bg=C["menu_bg"], fg=C["fg_main"], activebackground=C["bg_selected"],
                  activeforeground=C["fg_bright"], bd=0, relief="flat")
        fm = tk.Menu(self.menu, tearoff=0, **mo)
        fm.add_command(label=self.t("save_all"), command=self._save_all)
        fm.add_separator()
        fm.add_command(label=self.t("export_config"), command=self._export)
        fm.add_command(label=self.t("import_config"), command=self._import)
        fm.add_separator()
        fm.add_command(label=self.t("export_all"), command=self._export_all)
        fm.add_command(label=self.t("import_all"), command=self._import_all)
        fm.add_separator()
        fm.add_command(label=self.t("quit"), command=self._on_close)
        self.menu.add_cascade(label=self.t("file"), menu=fm)

        vm = tk.Menu(self.menu, tearoff=0, **mo)
        vm.add_command(label=self.t("open_catalog"), command=self._open_catalog)
        vm.add_separator()
        vm.add_command(label=self.t("fits_analyzer"), command=self._open_fits_analyzer)
        self.menu.add_cascade(label=self.t("view"), menu=vm)

        sm = tk.Menu(self.menu, tearoff=0, **mo)
        um = tk.Menu(sm, tearoff=0, **mo)
        um.add_command(label=self.t("length_mm"), command=lambda: self._set_unit("length_unit","mm"))
        um.add_command(label=self.t("length_in"), command=lambda: self._set_unit("length_unit","in"))
        um.add_separator()
        um.add_command(label=self.t("mass_g"), command=lambda: self._set_unit("mass_unit","g"))
        um.add_command(label=self.t("mass_oz"), command=lambda: self._set_unit("mass_unit","oz"))
        sm.add_cascade(label=self.t("units"), menu=um)
        self.menu.add_cascade(label=self.t("settings"), menu=sm)

        hm = tk.Menu(self.menu, tearoff=0, **mo)
        hm.add_command(label=self.t("user_guide"), command=lambda: open_help(self.root, self.lang))
        hm.add_command(label=self.t("about"), command=self._about)
        hm.add_separator()
        hm.add_command(label=self.t("report_bug"), command=self._report_bug)
        hm.add_separator()
        hm.add_command(label=self.t("check_updates"), command=self._check_updates_manual)
        self.menu.add_cascade(label=self.t("help_menu"), menu=hm)

        lm = tk.Menu(self.menu, tearoff=0, **mo)
        lm.add_command(label="Fran\u00e7ais", command=lambda: self._set_lang("fr"))
        lm.add_command(label="English", command=lambda: self._set_lang("en"))
        self.menu.add_cascade(label=self.t("language"), menu=lm)

        self.btn_open_cat.config(text=self.t("open_catalog"))
        self.btn_new_part.config(text=self.t("new_part"))
        self.btn_fits.config(text=self.t("fits_btn"))
        self.lbl_target.config(text=self.t("target_bf"))
        self.lbl_notes.config(text=self.t("notes"))
        for key in ("add_to_stack","remove_from_stack","move_up","move_down",
                     "flip_piece","mark_bf_start","mark_bf_end","auto_suggest","auto_complete",
                     "insert_ghost","resolve_ghosts"):
            btn = getattr(self, f"btn_{key}", None)
            if btn: btn.config(text=self.t(key))
        self._refresh_stack()

    def _set_unit(self, key, val):
        self.data[key] = val; self._save(); self._refresh_stack()
        if self._catalog_win and self._catalog_win.win.winfo_exists():
            self._catalog_win._refresh()

    def _about(self):
        messagebox.showinfo(self.t("about"),
            f"Backfocus Calculator v{VERSION}\n\n"
            f"Reference database: {len(REFERENCE_DB)} products\n"
            f"User parts: {len(self.data['parts'])}\n"
            f"Configurations: {len(self.data['configurations'])}\n\n"
            "Dark space theme \u00b7 Galaxy cursor\n"
            "Bilingual EN/FR")

    # ── crash detection ─────────────────────────────────────────────

    def _check_crash_on_startup(self):
        """If a crash report file exists, offer to send it."""
        if not os.path.exists(_CRASH_FILE):
            return
        try:
            with open(_CRASH_FILE, "r", encoding="utf-8") as f:
                crash_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            try:
                os.remove(_CRASH_FILE)
            except OSError:
                pass
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("crash_detected"))
        dlg.configure(bg=C["bg_dark"])
        dlg.transient(self.root)
        dlg.grab_set()

        # Build content first, then size to fit
        dlg.withdraw()

        tk.Label(dlg, text=self.t("crash_detected"),
                 font=(FONT_FAMILY, 15, "bold"),
                 fg=C["accent_red"], bg=C["bg_dark"]).pack(pady=(24, 10))
        tk.Label(dlg, text=self.t("crash_report_msg"),
                 font=(FONT_FAMILY, 11), fg=C["fg_main"], bg=C["bg_dark"],
                 wraplength=460, justify="center").pack(padx=30, pady=(4, 28))

        btn_frame = tk.Frame(dlg, bg=C["bg_dark"])
        btn_frame.pack(pady=(0, 24))

        def _send():
            dlg.destroy()
            self._send_crash_report(crash_data)

        def _skip():
            dlg.destroy()

        tk.Button(btn_frame, text=self.t("crash_report_send"),
                  font=(FONT_FAMILY, 11, "bold"), fg=C["fg_bright"], bg=C["accent_red"],
                  activebackground=C["accent_orange"], width=18, pady=6,
                  command=_send).pack(side="left", padx=12)
        tk.Button(btn_frame, text=self.t("crash_report_skip"),
                  font=(FONT_FAMILY, 11), fg=C["fg_main"], bg=C["btn_bg"],
                  activebackground=C["btn_hover"], width=14, pady=6,
                  command=_skip).pack(side="left", padx=12)

        # Let tkinter compute the required size, then center on parent
        dlg.update_idletasks()
        _center_dlg(dlg, self.root)
        dlg.resizable(False, False)

        _bind_dlg_keys(dlg)

        # Always remove crash file after handling
        try:
            os.remove(_CRASH_FILE)
        except OSError:
            pass

    def _send_crash_report(self, crash_data):
        """Open browser with a pre-filled GitHub Issue from crash data."""
        import urllib.parse, webbrowser
        error_type = crash_data.get("error_type", "Unknown")
        error_msg = crash_data.get("error_msg", "")
        tb = crash_data.get("traceback", "")
        title = f"[Crash] {error_type}: {error_msg}"
        if len(title) > 120:
            title = title[:117] + "..."

        recent = _get_recent_errors(10)
        recent_section = ""
        if recent:
            recent_section = f"## Recent Errors\n\n```\n{recent}\n```\n\n"

        body = (
            f"## Crash Report\n\n"
            f"**{error_type}:** {error_msg}\n\n"
            f"### Traceback\n\n```\n{tb}```\n\n"
            f"### System Info\n\n"
            f"- **Backfocus Calculator:** v{crash_data.get('version', '?')}\n"
            f"- **OS:** {crash_data.get('os', '?')}\n"
            f"- **Python:** {crash_data.get('python', '?')}\n"
            f"- **Architecture:** {crash_data.get('arch', '?')}\n"
            f"- **Tk:** {crash_data.get('tk', '?')}\n\n"
            f"{recent_section}"
            f"*Auto-generated crash report*\n"
        )
        params = urllib.parse.urlencode({
            'title': title,
            'body': body,
            'labels': 'auto-report,bug',
        })
        webbrowser.open(f"https://github.com/ARP273-ROSE/backfocus/issues/new?{params}")
        messagebox.showinfo(self.t("crash_detected"), self.t("crash_report_sent"))

    # ── bug report ───────────────────────────────────────────────────

    def _report_bug(self):
        import platform, urllib.parse, webbrowser
        sys_info = (
            f"- **Backfocus Calculator:** v{VERSION}\n"
            f"- **OS:** {platform.system()} {platform.version()}\n"
            f"- **Python:** {platform.python_version()}\n"
            f"- **Architecture:** {platform.machine()}\n"
            f"- **Tk:** {tk.TkVersion}\n"
        )
        recent = _get_recent_errors(10)
        recent_section = ""
        if recent:
            recent_section = f"## Recent Errors\n\n```\n{recent}\n```\n\n"
        body = (
            "## Description\n\n"
            "<!-- Describe the bug clearly -->\n\n\n"
            "## Steps to Reproduce\n\n"
            "1. \n2. \n3. \n\n"
            "## Expected Behavior\n\n\n\n"
            "## Actual Behavior\n\n\n\n"
            "## System Info\n\n"
            f"{sys_info}\n"
            f"{recent_section}"
            "## Screenshots / Logs\n\n"
            "<!-- Paste any relevant screenshots or log output -->\n"
        )
        params = urllib.parse.urlencode({
            'title': '[Bug] ',
            'body': body,
            'labels': 'bug',
        })
        webbrowser.open(f"https://github.com/ARP273-ROSE/backfocus/issues/new?{params}")

    # ── auto-update ──────────────────────────────────────────────────

    def _check_updates_startup(self):
        """Non-blocking update check at startup (silent)."""
        self._update_check_worker_start(silent=True)

    def _check_updates_manual(self):
        """Manual update check from Help menu (verbose)."""
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
            self.root.after(200, lambda: self._poll_update_check(silent))
            return
        if isinstance(result, dict):
            self._show_update_dialog(result)
        elif not silent:
            if result == "up_to_date":
                messagebox.showinfo(self.t("help_menu"),
                                    self.t("update_up_to_date", version=VERSION))
            else:
                messagebox.showwarning(self.t("help_menu"),
                                       self.t("update_no_connection"))

    def _show_update_dialog(self, info):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("update_title"))
        dlg.configure(bg="#1a1a2e")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        w, h = 520, 400
        dlg.withdraw()
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        dlg.deiconify()

        fg = "#e0e0e0"
        bg = "#1a1a2e"
        accent = "#4fc3f7"

        tk.Label(dlg, text=self.t("update_available"), font=("Segoe UI", 14, "bold"),
                 fg=accent, bg=bg).pack(pady=(16, 8))
        tk.Label(dlg, text=self.t("update_current", current=VERSION),
                 fg=fg, bg=bg, font=("Segoe UI", 10)).pack()
        tk.Label(dlg, text=self.t("update_new", new=info["version"]),
                 fg=accent, bg=bg, font=("Segoe UI", 10, "bold")).pack(pady=(0, 8))
        tk.Label(dlg, text=self.t("update_changelog"),
                 fg=fg, bg=bg, font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=20)

        frame = tk.Frame(dlg, bg=bg)
        frame.pack(fill="both", expand=True, padx=20, pady=(4, 12))
        txt = tk.Text(frame, wrap="word", bg="#0f0f23", fg=fg, font=("Consolas", 9),
                      relief="flat", borderwidth=0, highlightthickness=0)
        sb = tk.Scrollbar(frame, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", info.get("body", ""))
        txt.configure(state="disabled")

        btn_frame = tk.Frame(dlg, bg=bg)
        btn_frame.pack(pady=(0, 16))
        tk.Button(btn_frame, text=self.t("update_download"), bg="#2e7d32", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=6,
                  command=lambda: [dlg.destroy(), self._do_update(info)]).pack(side="left", padx=8)
        tk.Button(btn_frame, text=self.t("update_skip"), bg="#444", fg="white",
                  font=("Segoe UI", 10), relief="flat", padx=16, pady=6,
                  command=dlg.destroy).pack(side="left", padx=8)

    def _do_update(self, info):
        dlg = tk.Toplevel(self.root)
        dlg.title(self.t("update_downloading"))
        dlg.configure(bg="#1a1a2e")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        w, h = 340, 120
        dlg.withdraw()
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        dlg.deiconify()

        self._update_dlg = dlg
        while not self._update_dl_queue.empty():
            self._update_dl_queue.get_nowait()
        lbl = tk.Label(dlg, text=self.t("update_downloading"), fg="#e0e0e0",
                       bg="#1a1a2e", font=("Segoe UI", 10))
        lbl.pack(pady=(20, 8))
        self._update_lbl = lbl
        pb = ttk.Progressbar(dlg, mode="indeterminate", length=260)
        pb.pack(pady=(0, 10))
        pb.start(15)

        self._update_dl_thread = threading.Thread(
            target=self._update_download_worker, args=(info["zipball_url"],), daemon=True)
        self._update_dl_thread.start()
        self._poll_update_download()

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
            self.root.after(200, self._poll_update_download)
            return
        if error:
            self._update_dlg.destroy()
            messagebox.showerror(self.t("help_menu"),
                                 self.t("update_error", err=error))
        else:
            self._update_lbl.config(text=self.t("update_restarting"))
            self.root.after(600, self._restart_app)

    def _restart_app(self):
        _save_writer.flush_sync()
        save_data(self.data, sync=True)
        self.galaxy.stop()
        self.root.destroy()
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

    def _restore_sash_positions(self):
        """Restore saved pane sash positions after layout is ready."""
        ui = self.data.get("ui", {})
        try:
            sh = ui.get("sash_h")
            if sh is not None:
                self.pw_h.sash_place(0, int(sh), 0)
        except (tk.TclError, ValueError):
            pass
        try:
            sv = ui.get("sash_v")
            if sv is not None:
                self.pw_v.sash_place(0, 0, int(sv))
        except (tk.TclError, ValueError):
            pass

    def _save_ui_state(self):
        """Persist window geometry and pane sash positions."""
        ui = self.data.setdefault("ui", {})
        ui["window_geometry"] = self.root.geometry()
        try:
            ui["sash_h"] = self.pw_h.sash_coord(0)[0]
        except (tk.TclError, IndexError):
            pass
        try:
            ui["sash_v"] = self.pw_v.sash_coord(0)[1]
        except (tk.TclError, IndexError):
            pass

    def _on_close(self):
        # Cancel any pending debounced saves
        if self._pending_save:
            self.root.after_cancel(self._pending_save)
            self._pending_save = None
        self._save_ui_state()
        _save_writer.flush_sync()  # wait for any pending async write
        save_data(self.data, sync=True)  # final save must be synchronous
        self.galaxy.stop()
        self.root.destroy()


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
    root = tk.Tk()
    # App icon (title bar + taskbar)
    _icon_dir = os.path.dirname(os.path.abspath(__file__))
    _png_path = os.path.join(_icon_dir, "backfocus.png")
    try:
        if os.path.exists(_png_path):
            _icon_img = tk.PhotoImage(file=_png_path)
            root.iconphoto(True, _icon_img)
    except tk.TclError:
        pass
    App(root)
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.attributes("-topmost", False))
    root.focus_force()
    root.mainloop()

if __name__ == "__main__":
    main()
