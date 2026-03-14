#!/usr/bin/env python3
"""
FITS / XISF Backfocus Analyzer – single-image diagnostics.

Detects stars, fits elliptical Gaussians, builds FWHM surface map,
and classifies backfocus error direction (too short / too long) via
radial vs tangential elongation pattern analysis.

Supported formats: FITS (.fits .fit .fts), compressed FITS (.fits.fz .fit.fz),
                   XISF (.xisf) — all case-insensitive.

Requires: numpy, scipy, astropy, photutils, matplotlib
"""

import concurrent.futures
import math
import os
import struct
import threading
import xml.etree.ElementTree as ET
import zlib

import numpy as np
from scipy.optimize import curve_fit
from astropy.io import fits
from astropy.stats import sigma_clipped_stats, sigma_clip
from photutils.detection import DAOStarFinder
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.patches import Ellipse
import matplotlib.colors as mcolors

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QLineEdit, QTabWidget, QProgressBar, QTextEdit, QFrame, QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# ═══════════════════════════════════════════════════════════════════
#  TRANSLATIONS (EN / FR)
# ═══════════════════════════════════════════════════════════════════
TR_FITS = {
    "win_title":        {"en": "FITS / XISF Backfocus Analyzer", "fr": "Analyseur FITS / XISF de backfocus"},
    "browse":           {"en": "Browse\u2026", "fr": "Parcourir\u2026"},
    "analyze":          {"en": "Analyze", "fr": "Analyser"},
    "fwhm_est":         {"en": "FWHM est:", "fr": "FWHM est. :"},
    "threshold":        {"en": "Threshold:", "fr": "Seuil :"},
    "no_file":          {"en": "No file selected", "fr": "Aucun fichier s\u00e9lectionn\u00e9"},
    "loading":          {"en": "Loading image\u2026", "fr": "Chargement image\u2026"},
    "detecting":        {"en": "Detecting stars\u2026", "fr": "D\u00e9tection des \u00e9toiles\u2026"},
    "fitting":          {"en": "Fitting PSFs ({n}/{total})\u2026", "fr": "Ajustement PSF ({n}/{total})\u2026"},
    "fitting_parallel": {"en": "Fitting PSFs ({n}/{total}) [{workers} threads]\u2026",
                         "fr": "Ajustement PSF ({n}/{total}) [{workers} threads]\u2026"},
    "building_map":     {"en": "Building FWHM map\u2026", "fr": "Construction carte FWHM\u2026"},
    "classifying":      {"en": "Classifying backfocus\u2026", "fr": "Classification backfocus\u2026"},
    "done":             {"en": "Done.", "fr": "Termin\u00e9."},
    "error":            {"en": "Error: {msg}", "fr": "Erreur : {msg}"},
    "stars_detected":   {"en": "Stars detected: {n}", "fr": "\u00c9toiles d\u00e9tect\u00e9es : {n}"},
    "stars_fitted":     {"en": "Stars fitted: {n}", "fr": "\u00c9toiles ajust\u00e9es : {n}"},
    "mean_fwhm":        {"en": "Mean FWHM: {v:.2f} px", "fr": "FWHM moyen : {v:.2f} px"},
    "fwhm_gradient":    {"en": "FWHM gradient (center\u2192edge): {v:+.1f}%",
                         "fr": "Gradient FWHM (centre\u2192bord) : {v:+.1f}%"},
    "mean_ecc":         {"en": "Mean eccentricity: {v:.3f}", "fr": "Excentricit\u00e9 moy. : {v:.3f}"},
    "verdict_correct":  {"en": "VERDICT: Backfocus appears CORRECT",
                         "fr": "VERDICT : Backfocus semble CORRECT"},
    "verdict_short":    {"en": "VERDICT: Backfocus TOO SHORT \u2192 add spacers",
                         "fr": "VERDICT : Backfocus TROP COURT \u2192 ajouter des espaceurs"},
    "verdict_long":     {"en": "VERDICT: Backfocus TOO LONG \u2192 remove spacers",
                         "fr": "VERDICT : Backfocus TROP LONG \u2192 retirer des espaceurs"},
    "radial_score":     {"en": "Radial score: {v:+.3f}  ({interp})",
                         "fr": "Score radial : {v:+.3f}  ({interp})"},
    "interp_radial":    {"en": "radial elongation", "fr": "allongement radial"},
    "interp_tangential":{"en": "tangential elongation", "fr": "allongement tangentiel"},
    "interp_mixed":     {"en": "mixed / neutral", "fr": "mixte / neutre"},
    "fwhm_map_title":   {"en": "FWHM Map (px)", "fr": "Carte FWHM (px)"},
    "vector_title":     {"en": "PSF Elongation Field", "fr": "Champ d'allongement PSF"},
    "too_few_stars":    {"en": "Too few stars detected ({n}). Try lowering threshold.",
                         "fr": "Trop peu d'\u00e9toiles ({n}). Essayez un seuil plus bas."},
    "file_label":       {"en": "File:", "fr": "Fichier :"},
    "image_size":       {"en": "Image: {w}\u00d7{h}", "fr": "Image : {w}\u00d7{h}"},
    "note_single":      {"en": "Note: Single-image analysis gives direction only, not precise offset.",
                         "fr": "Note : L'analyse mono-image donne la direction, pas l'\u00e9cart pr\u00e9cis."},
    "experimental":     {"en": "\u26a0 EXPERIMENTAL \u2014 For precise backfocus measurement, use HocusFocus with N.I.N.A.",
                         "fr": "\u26a0 EXP\u00c9RIMENTAL \u2014 Pour une mesure pr\u00e9cise du backfocus, utilisez HocusFocus avec N.I.N.A."},
    "warn_not_light":   {"en": "\u26a0 This image appears to be a {frametype} frame, not a Light frame.\n"
                                "Backfocus analysis requires a Light frame with stars.",
                         "fr": "\u26a0 Cette image semble \u00eatre un {frametype}, pas un Light.\n"
                                "L'analyse de backfocus n\u00e9cessite un Light avec des \u00e9toiles."},
    "tab_analysis":     {"en": "Analysis",           "fr": "Analyse"},
    "tab_mosaic":       {"en": "Mosaic 3\u00d73",    "fr": "Mosa\u00efque 3\u00d73"},
    "tile_fwhm":        {"en": "FWHM: {v:.2f}",     "fr": "FWHM : {v:.2f}"},
    "tile_stars":       {"en": "{n} stars",          "fr": "{n} \u00e9toiles"},
    "tile_no_stars":    {"en": "No stars",           "fr": "Aucune \u00e9toile"},
    "tile_center":      {"en": "Center",             "fr": "Centre"},
    "tile_top_left":    {"en": "Top-Left",           "fr": "Haut-G"},
    "tile_top":         {"en": "Top",                "fr": "Haut"},
    "tile_top_right":   {"en": "Top-Right",          "fr": "Haut-D"},
    "tile_left":        {"en": "Left",               "fr": "Gauche"},
    "tile_right":       {"en": "Right",              "fr": "Droite"},
    "tile_bot_left":    {"en": "Bot-Left",           "fr": "Bas-G"},
    "tile_bottom":      {"en": "Bottom",             "fr": "Bas"},
    "tile_bot_right":   {"en": "Bot-Right",          "fr": "Bas-D"},
}

# ═══════════════════════════════════════════════════════════════════
#  DEFAULTS
# ═══════════════════════════════════════════════════════════════════
ANALYSIS_DEFAULTS = {
    "fwhm_est": 5.0,
    "threshold": 8.0,
    "star_limit": 500,
    "edge_margin": 50,
    "box_size": 25,
    "min_stars": 10,
    "retry_threshold": 4.0,
    "max_eccentricity": 0.95,
    "max_chi2": 5.0,
    "progress_interval": 20,
    "ecc_threshold": 0.15,
    "radial_positive_threshold": 0.3,
    "radial_negative_threshold": -0.3,
    "annular_zones": 4,
    "annular_weights": [0.1, 0.2, 0.3, 0.4],
    "grid_size": 50,
    "poly_degree": 2,
    "sigma_clip_iters": 3,
    "sigma_clip_sigma": 2.5,
    "autobin_threshold": 4096,
    "mosaic_tile_fraction": 0.20,
}

import platform as _platform
_os_name = _platform.system()
FONT_FAMILY = "Segoe UI" if _os_name == "Windows" else ("SF Pro Display" if _os_name == "Darwin" else "DejaVu Sans")
FONT_MONO = "Cascadia Code" if _os_name == "Windows" else "DejaVu Sans Mono"

# ═══════════════════════════════════════════════════════════════════
#  DARK SPACE COLOR PALETTE (matches backfocus.py)
# ═══════════════════════════════════════════════════════════════════
_C = {
    "bg_dark":   "#1A1A2A",
    "bg_mid":    "#222234",
    "bg_light":  "#2C2C40",
    "fg_main":   "#D8D8E4",
    "fg_dim":    "#807896",
    "fg_bright": "#F2EEF8",
    "accent_teal":   "#80D8CC",
    "accent_green":  "#96DCAE",
    "accent_red":    "#E08878",
    "accent_orange": "#E4B878",
    "accent_purple": "#C09AE8",
    "border":    "#403850",
    "btn_bg":    "#303044",
    "btn_hover": "#484060",
}

# ═══════════════════════════════════════════════════════════════════
#  ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def _detect_frame_type(header):
    """Check FITS/XISF header for frame type. Returns None if light or unknown."""
    if header is None:
        return None
    for key in ("IMAGETYP", "FRAME", "PICTTYPE"):
        val = ""
        if hasattr(header, "get"):
            val = str(header.get(key, "")).strip().lower()
        elif isinstance(header, dict):
            val = str(header.get(key, "")).strip().lower()
        if not val:
            continue
        for bad in ("flat", "bias", "dark", "offset"):
            if bad in val:
                return val.capitalize()
    return None


def _is_xisf(filepath):
    """Check if file is XISF by magic bytes."""
    try:
        with open(filepath, "rb") as f:
            return f.read(8) == b"XISF0100"
    except OSError:
        return False


def _byte_unshuffle(data_bytes, item_size):
    """Reverse XISF byte-shuffling."""
    n_bytes = len(data_bytes)
    if item_size <= 1 or n_bytes < item_size:
        return data_bytes
    n_elements = n_bytes // item_size
    usable = n_elements * item_size
    arr = np.frombuffer(data_bytes[:usable], dtype=np.uint8)
    unshuffled = arr.reshape(item_size, n_elements).T.tobytes()
    if usable < n_bytes:
        unshuffled += data_bytes[usable:]
    return unshuffled


def _load_xisf(filepath):
    """Load an XISF file, return (2D float64 array, dict header)."""
    with open(filepath, "rb") as f:
        magic = f.read(8)
        if magic != b"XISF0100":
            raise ValueError("Not a valid XISF file (bad magic)")
        header_len, _reserved = struct.unpack("<II", f.read(8))
        xml_bytes = f.read(header_len)

        xml_str = xml_bytes.decode("utf-8", errors="replace")
        import re
        xml_str = re.sub(r'\s+xmlns\s*=\s*["\'][^"\']*["\']', '', xml_str)
        root = ET.fromstring(xml_str)

        img_el = root.find(".//Image")
        if img_el is None:
            raise ValueError("No Image element found in XISF header")

        geom = img_el.get("geometry", "")
        parts = geom.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid XISF geometry: {geom}")
        width = int(parts[0])
        height = int(parts[1])
        channels = int(parts[2]) if len(parts) > 2 else 1

        sample_fmt = img_el.get("sampleFormat", "Float32")
        dtype_map = {
            "UInt8": np.uint8, "UInt16": np.uint16, "UInt32": np.uint32,
            "UInt64": np.uint64, "Int8": np.int8, "Int16": np.int16,
            "Int32": np.int32, "Int64": np.int64,
            "Float32": np.float32, "Float64": np.float64,
        }
        dtype = dtype_map.get(sample_fmt)
        if dtype is None:
            raise ValueError(f"Unsupported XISF sample format: {sample_fmt}")

        color_space = img_el.get("colorSpace", "Gray")
        pixel_storage = img_el.get("pixelStorage", "planar")

        location = img_el.get("location", "")
        compression = img_el.get("compression", "")

        if location.startswith("attachment:"):
            loc_parts = location.split(":")
            offset = int(loc_parts[1])
            size = int(loc_parts[2])
            f.seek(offset)
            raw = f.read(size)
        elif location.startswith("inline:"):
            import base64
            data_el = img_el.find("Data")
            if data_el is not None and data_el.text:
                raw = base64.b64decode(data_el.text.strip())
            else:
                raise ValueError("XISF inline data: no <Data> element found")
        elif location.startswith("embedded:"):
            raise ValueError("XISF embedded blocks not supported")
        else:
            raise ValueError(f"Unsupported XISF location: {location}")

        if compression:
            comp_parts = compression.split(":")
            codec = comp_parts[0].lower()
            uncompressed_size = int(comp_parts[1]) if len(comp_parts) > 1 else 0
            shuffle_item_size = (int(comp_parts[2]) if len(comp_parts) > 2
                                 else np.dtype(dtype).itemsize)

            byte_shuffle = "+sh" in codec
            base_codec = codec.replace("+sh", "")

            if base_codec == "zlib":
                raw = zlib.decompress(raw)
            elif base_codec in ("lz4", "lz4hc"):
                try:
                    import lz4.block
                    raw = lz4.block.decompress(raw, uncompressed_size=uncompressed_size)
                except ImportError:
                    raise ValueError("XISF LZ4 compression: pip install lz4")
            elif base_codec == "zstd":
                try:
                    import zstandard
                    raw = zstandard.ZstdDecompressor().decompress(raw)
                except ImportError:
                    raise ValueError("XISF Zstandard compression: pip install zstandard")
            else:
                raise ValueError(f"Unsupported XISF compression: {codec}")

            if byte_shuffle:
                raw = _byte_unshuffle(raw, shuffle_item_size)

        data = np.frombuffer(raw, dtype=dtype)

        if channels > 1:
            if pixel_storage == "planar":
                data = data.reshape(channels, height, width)
            else:
                data = data.reshape(height, width, channels)
        else:
            data = data.reshape(height, width)

    header = {"XISF": True, "NAXIS1": width, "NAXIS2": height,
              "CHANNELS": channels, "FORMAT": sample_fmt,
              "COLORSPACE": color_space}
    for prop in root.iter("FITSKeyword"):
        header[prop.get("name", "")] = prop.get("value", "")

    return data, header


def load_fits_data(filepath):
    """Load a FITS or XISF image file, return (2D float64 array, header)."""
    name_lower = os.path.basename(filepath).lower()
    if name_lower.endswith(".xisf") or _is_xisf(filepath):
        data, header = _load_xisf(filepath)
    else:
        with fits.open(filepath) as hdul:
            data = None
            header = None
            for hdu in hdul:
                if hdu.data is not None and hdu.data.ndim >= 2:
                    data = hdu.data
                    header = hdu.header
                    break
            if data is None:
                raise ValueError("No image data found in FITS file")

    if data.ndim == 3:
        if data.shape[0] == 3:
            data = 0.299 * data[0] + 0.587 * data[1] + 0.114 * data[2]
        elif data.shape[2] == 3:
            data = 0.299 * data[:, :, 0] + 0.587 * data[:, :, 1] + 0.114 * data[:, :, 2]
        else:
            data = data[0]

    data = data.astype(np.float64)

    nan_mask = np.isnan(data)
    if np.any(nan_mask):
        med = np.nanmedian(data)
        data[nan_mask] = med

    th = ANALYSIS_DEFAULTS["autobin_threshold"]
    if data.shape[0] > th or data.shape[1] > th:
        h, w = data.shape
        h2, w2 = h // 2 * 2, w // 2 * 2
        data = data[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).mean(axis=(1, 3))

    return data, header


def _run_dao(data, fwhm_est, threshold_sigma):
    """Run DAOStarFinder with given parameters."""
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    if std < 1e-10:
        std = np.std(data)
    if std < 1e-10:
        return None, median

    finder = DAOStarFinder(fwhm=fwhm_est, threshold=threshold_sigma * std)
    sources = finder(data - median)
    return sources, median


def detect_stars(data, fwhm_est=None, threshold=None):
    """Detect stars using DAOStarFinder. Returns list of dicts with x, y, flux."""
    if fwhm_est is None:
        fwhm_est = ANALYSIS_DEFAULTS["fwhm_est"]
    if threshold is None:
        threshold = ANALYSIS_DEFAULTS["threshold"]

    margin = ANALYSIS_DEFAULTS["edge_margin"]
    h, w = data.shape
    eff_margin = min(margin, h // 6, w // 6)
    limit = ANALYSIS_DEFAULTS["star_limit"]
    min_stars = ANALYSIS_DEFAULTS["min_stars"]

    fwhm_candidates = [fwhm_est]
    for f in [2.0, 3.0, 5.0, 8.0, 12.0]:
        if abs(f - fwhm_est) > 0.5:
            fwhm_candidates.append(f)

    thresh_candidates = [threshold]
    for t in [5.0, 3.0]:
        if t < threshold and t not in thresh_candidates:
            thresh_candidates.append(t)

    best_sources = None
    best_count = 0

    for fwhm_try in fwhm_candidates:
        for thresh_try in thresh_candidates:
            sources, _ = _run_dao(data, fwhm_try, thresh_try)
            if sources is None or len(sources) == 0:
                continue

            mask = ((sources["xcentroid"] > eff_margin) &
                    (sources["xcentroid"] < w - eff_margin) &
                    (sources["ycentroid"] > eff_margin) &
                    (sources["ycentroid"] < h - eff_margin))
            filtered = sources[mask]

            if len(filtered) > best_count:
                best_sources = filtered
                best_count = len(filtered)

            if best_count >= min_stars:
                break
        if best_count >= min_stars:
            break

    if best_sources is None or len(best_sources) == 0:
        return []

    best_sources.sort("flux")
    best_sources.reverse()
    if len(best_sources) > limit:
        best_sources = best_sources[:limit]

    stars = []
    for row in best_sources:
        stars.append({
            "x": float(row["xcentroid"]),
            "y": float(row["ycentroid"]),
            "flux": float(row["flux"]),
        })
    return stars


def _gaussian_2d(xy, amplitude, x0, y0, sigma_x, sigma_y, theta, offset):
    """Elliptical 2D Gaussian model."""
    x, y = xy
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    a = cos_t**2 / (2 * sigma_x**2) + sin_t**2 / (2 * sigma_y**2)
    b = -math.sin(2 * theta) / (4 * sigma_x**2) + math.sin(2 * theta) / (4 * sigma_y**2)
    c = sin_t**2 / (2 * sigma_x**2) + cos_t**2 / (2 * sigma_y**2)
    dx = x - x0
    dy = y - y0
    return (amplitude * np.exp(-(a * dx**2 + 2 * b * dx * dy + c * dy**2)) + offset).ravel()


def _fit_one_star(args):
    """Fit a single star PSF. Returns result dict or None."""
    star, cutout, x0, y0, box_size, half, xy = args

    bg = np.median(np.concatenate([
        cutout[0, :], cutout[-1, :], cutout[:, 0], cutout[:, -1]
    ]))
    cutout_sub = cutout - bg

    amp_guess = cutout_sub.max()
    if amp_guess <= 0:
        return None

    cx_local = star["x"] - x0
    cy_local = star["y"] - y0
    sig_guess = ANALYSIS_DEFAULTS["fwhm_est"] / 2.355

    p0 = [amp_guess, cx_local, cy_local, sig_guess, sig_guess, 0.0, 0.0]
    bounds_lo = [0, cx_local - half / 2, cy_local - half / 2, 0.5, 0.5, -math.pi, -np.inf]
    bounds_hi = [amp_guess * 3, cx_local + half / 2, cy_local + half / 2,
                 half, half, math.pi, amp_guess]

    try:
        popt, _ = curve_fit(_gaussian_2d, xy, cutout_sub.ravel(),
                            p0=p0, bounds=(bounds_lo, bounds_hi),
                            maxfev=2000)
    except (RuntimeError, ValueError):
        return None

    amp, fit_cx, fit_cy, sigma_x, sigma_y, theta, offset = popt

    fwhm_x = abs(sigma_x) * 2.355
    fwhm_y = abs(sigma_y) * 2.355
    fwhm_major = max(fwhm_x, fwhm_y)
    fwhm_minor = min(fwhm_x, fwhm_y)

    if fwhm_major < 0.5:
        return None

    eccentricity = math.sqrt(1 - (fwhm_minor / fwhm_major) ** 2)

    if fwhm_x >= fwhm_y:
        pa = theta
    else:
        pa = theta + math.pi / 2
    pa = ((pa + math.pi / 2) % math.pi) - math.pi / 2

    model = _gaussian_2d(xy, *popt)
    residuals = cutout_sub.ravel() - model
    chi2 = np.sum(residuals ** 2) / (amp_guess ** 2 + 1e-10) * box_size

    if chi2 > ANALYSIS_DEFAULTS["max_chi2"]:
        return None
    if eccentricity > ANALYSIS_DEFAULTS["max_eccentricity"]:
        return None
    if fwhm_major > box_size / 2:
        return None

    return {
        "x": star["x"],
        "y": star["y"],
        "x_fit": fit_cx + x0,
        "y_fit": fit_cy + y0,
        "fwhm_major": fwhm_major,
        "fwhm_minor": fwhm_minor,
        "fwhm_geom": math.sqrt(fwhm_major * fwhm_minor),
        "eccentricity": eccentricity,
        "position_angle": pa,
        "amplitude": amp,
        "chi2": chi2,
        "flux": star["flux"],
    }


def fit_star_psfs(data, stars, box_size=None, progress_cb=None):
    """Fit elliptical 2D Gaussian to each star. Returns list of result dicts."""
    if box_size is None:
        box_size = ANALYSIS_DEFAULTS["box_size"]

    half = box_size // 2
    h, w = data.shape
    interval = ANALYSIS_DEFAULTS["progress_interval"]

    y_grid, x_grid = np.mgrid[0:box_size, 0:box_size]
    xy = (x_grid.ravel(), y_grid.ravel())

    tasks = []
    for star in stars:
        sx, sy = int(round(star["x"])), int(round(star["y"]))
        x0 = sx - half
        y0 = sy - half
        if x0 < 0 or y0 < 0 or x0 + box_size > w or y0 + box_size > h:
            continue
        cutout = data[y0:y0 + box_size, x0:x0 + box_size].copy()
        tasks.append((star, cutout, x0, y0, box_size, half, xy))

    if not tasks:
        return []

    n_workers = max(1, min(os.cpu_count() or 4, len(tasks), 16))

    if n_workers <= 1 or len(tasks) < 20:
        results = []
        for i, task_args in enumerate(tasks):
            result = _fit_one_star(task_args)
            if result is not None:
                results.append(result)
            if progress_cb and (i + 1) % interval == 0:
                progress_cb(i + 1, len(tasks))
        if progress_cb:
            progress_cb(len(tasks), len(tasks))
        return results

    results = []
    completed = [0]
    lock = threading.Lock()

    def _done_callback(future):
        with lock:
            completed[0] += 1
            r = future.result()
            if r is not None:
                results.append(r)
            if progress_cb and completed[0] % interval == 0:
                progress_cb(completed[0], len(tasks))

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for args in tasks:
            fut = executor.submit(_fit_one_star, args)
            fut.add_done_callback(_done_callback)
            futures.append(fut)
        concurrent.futures.wait(futures)

    if progress_cb:
        progress_cb(len(tasks), len(tasks))

    return results


def build_fwhm_surface(star_fits, image_shape):
    """Build FWHM polynomial surface from fitted stars."""
    if len(star_fits) < 6:
        return None

    h, w = image_shape
    xs = np.array([s["x"] for s in star_fits])
    ys = np.array([s["y"] for s in star_fits])
    fwhms = np.array([s["fwhm_geom"] for s in star_fits])

    xn = (xs - w / 2) / (w / 2)
    yn = (ys - h / 2) / (h / 2)

    A = np.column_stack([np.ones_like(xn), xn, yn, xn**2, xn * yn, yn**2])

    mask = np.ones(len(fwhms), dtype=bool)
    coeffs = None
    for _ in range(ANALYSIS_DEFAULTS["sigma_clip_iters"]):
        Am = A[mask]
        fm = fwhms[mask]
        try:
            coeffs, _, _, _ = np.linalg.lstsq(Am, fm, rcond=None)
        except np.linalg.LinAlgError:
            return None
        residuals = fwhms - A @ coeffs
        clip_result = sigma_clip(residuals, sigma=ANALYSIS_DEFAULTS["sigma_clip_sigma"],
                                 maxiters=1, masked=True)
        mask = ~clip_result.mask

    if coeffs is None:
        return None

    gs = ANALYSIS_DEFAULTS["grid_size"]
    gx = np.linspace(-1, 1, gs)
    gy = np.linspace(-1, 1, gs)
    gx2d, gy2d = np.meshgrid(gx, gy)
    A_grid = np.column_stack([np.ones(gs * gs), gx2d.ravel(), gy2d.ravel(),
                              gx2d.ravel()**2, gx2d.ravel() * gy2d.ravel(),
                              gy2d.ravel()**2])
    fwhm_grid = (A_grid @ coeffs).reshape(gs, gs)

    center_fwhm = max(coeffs[0], 0.1)
    edge_points = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    edge_fwhm_vals = []
    for ex, ey in edge_points:
        val = coeffs[0] + coeffs[1] * ex + coeffs[2] * ey + \
              coeffs[3] * ex**2 + coeffs[4] * ex * ey + coeffs[5] * ey**2
        edge_fwhm_vals.append(val)
    edge_fwhm = np.mean(edge_fwhm_vals)

    gradient_pct = (edge_fwhm - center_fwhm) / (center_fwhm + 1e-10) * 100

    return {
        "coeffs": coeffs,
        "grid": fwhm_grid,
        "grid_extent": [0, w, h, 0],
        "center_fwhm": center_fwhm,
        "edge_fwhm": edge_fwhm,
        "gradient_pct": gradient_pct,
        "mask": mask,
    }


def classify_backfocus_error(star_fits, center):
    """Classify backfocus error via radial vs tangential elongation."""
    cx, cy = center
    ecc_thresh = ANALYSIS_DEFAULTS["ecc_threshold"]
    n_zones = ANALYSIS_DEFAULTS["annular_zones"]
    zone_weights = ANALYSIS_DEFAULTS["annular_weights"]

    max_r = 0
    for s in star_fits:
        r = math.sqrt((s["x"] - cx)**2 + (s["y"] - cy)**2)
        if r > max_r:
            max_r = r

    if max_r < 1:
        return {"score": 0, "verdict": "correct", "zone_scores": [],
                "n_eccentric": 0, "n_total": len(star_fits)}

    zone_sums = [0.0] * n_zones
    zone_counts = [0] * n_zones
    n_eccentric = 0

    for s in star_fits:
        if s["eccentricity"] < ecc_thresh:
            continue

        n_eccentric += 1
        dx = s["x"] - cx
        dy = s["y"] - cy
        r = math.sqrt(dx**2 + dy**2)
        if r < 1:
            continue

        radial_angle = math.atan2(dy, dx)
        pa = s["position_angle"]
        delta = abs(pa - radial_angle)
        delta = delta % math.pi
        if delta > math.pi / 2:
            delta = math.pi - delta

        radial_score = math.cos(2 * delta)
        weighted = radial_score * s["eccentricity"]

        zone_frac = r / max_r
        zone_idx = min(int(zone_frac * n_zones), n_zones - 1)
        zone_sums[zone_idx] += weighted
        zone_counts[zone_idx] += 1

    zone_scores = []
    global_score = 0.0
    total_weight = 0.0
    for z in range(n_zones):
        if zone_counts[z] > 0:
            avg = zone_sums[z] / zone_counts[z]
        else:
            avg = 0.0
        zone_scores.append({"avg": avg, "count": zone_counts[z]})
        global_score += avg * zone_weights[z]
        total_weight += zone_weights[z]

    if total_weight > 0:
        global_score /= total_weight

    pos_thresh = ANALYSIS_DEFAULTS["radial_positive_threshold"]
    neg_thresh = ANALYSIS_DEFAULTS["radial_negative_threshold"]
    if global_score > pos_thresh:
        verdict = "short"
    elif global_score < neg_thresh:
        verdict = "long"
    else:
        verdict = "correct"

    return {
        "score": global_score,
        "verdict": verdict,
        "zone_scores": zone_scores,
        "n_eccentric": n_eccentric,
        "n_total": len(star_fits),
    }


def compute_mosaic_tiles(data, star_fits, image_shape, tile_fraction=None):
    """Compute 9 mosaic tiles (3x3) with star filtering and mean FWHM."""
    if tile_fraction is None:
        tile_fraction = ANALYSIS_DEFAULTS["mosaic_tile_fraction"]

    h, w = image_shape
    th = int(h * tile_fraction)
    tw = int(w * tile_fraction)

    tile_defs = [
        ("tile_top_left",  0, 0, th // 2,       tw // 2),
        ("tile_top",       0, 1, th // 2,       w // 2),
        ("tile_top_right", 0, 2, th // 2,       w - tw // 2),
        ("tile_left",      1, 0, h // 2,        tw // 2),
        ("tile_center",    1, 1, h // 2,        w // 2),
        ("tile_right",     1, 2, h // 2,        w - tw // 2),
        ("tile_bot_left",  2, 0, h - th // 2,   tw // 2),
        ("tile_bottom",    2, 1, h - th // 2,   w // 2),
        ("tile_bot_right", 2, 2, h - th // 2,   w - tw // 2),
    ]

    tiles = []
    for name_key, row, col, cy, cx in tile_defs:
        y0 = max(0, cy - th // 2)
        y1 = min(h, y0 + th)
        x0 = max(0, cx - tw // 2)
        x1 = min(w, x0 + tw)

        crop = data[y0:y1, x0:x1]

        tile_stars = []
        star_xy_local = []
        for s in star_fits:
            sx, sy = s["x"], s["y"]
            if x0 <= sx < x1 and y0 <= sy < y1:
                tile_stars.append(s)
                star_xy_local.append((sx - x0, sy - y0))

        mean_fwhm = None
        if tile_stars:
            mean_fwhm = np.mean([s["fwhm_geom"] for s in tile_stars])

        tiles.append({
            "name_key": name_key,
            "row": row,
            "col": col,
            "crop": crop,
            "crop_bounds": (y0, y1, x0, x1),
            "stars": tile_stars,
            "star_xy_local": star_xy_local,
            "mean_fwhm": mean_fwhm,
            "star_count": len(tile_stars),
            "is_center": (row == 1 and col == 1),
        })

    return tiles


# ═══════════════════════════════════════════════════════════════════
#  UI WINDOW (PyQt6)
# ═══════════════════════════════════════════════════════════════════

class FITSAnalyzerWindow(QDialog):
    """Dialog window for FITS backfocus analysis."""

    def __init__(self, app):
        super().__init__(app if isinstance(app, QWidget) else (app.root if hasattr(app, 'root') else None))
        self.app = app
        self.lang = app.lang
        self._thread = None
        self._results = None
        self._error = None
        self._filepath = None
        self._data = None
        self._header = None
        self._progress = (0, 1)
        self._status_text = ""
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_thread)
        self._build()
        # Keep reference on the app-side so it doesn't get GC'd
        self.win = self  # compatibility alias

    def t(self, key, **kw):
        e = TR_FITS.get(key, {})
        s = e.get(self.lang, e.get("en", key))
        return s.format(**kw) if kw else s

    def _tip(self, widget, en, fr=None):
        """Set bilingual tooltip on a widget."""
        txt = (fr or en) if self.lang == "fr" else en
        widget.setToolTip(txt)

    def closeEvent(self, event):
        """Clean up resources and close window."""
        self._data = None
        self._header = None
        self._results = None
        import matplotlib.pyplot as plt
        plt.close(self._fig_fwhm)
        plt.close(self._fig_vec)
        plt.close(self._fig_mosaic)
        event.accept()

    def winfo_exists(self):
        """Compatibility method for tkinter-style existence check."""
        return self.isVisible()

    def lift(self):
        """Compatibility method for tkinter-style window raise."""
        self.raise_()
        self.activateWindow()

    # ── Build UI ──
    def _build(self):
        self.setWindowTitle(self.t("win_title"))
        self.resize(1200, 820)
        self.setMinimumSize(900, 650)
        self.setStyleSheet(f"background-color: {_C['bg_dark']}; color: {_C['fg_main']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(3)

        # ── Experimental banner ──
        banner = QLabel(self.t("experimental"))
        banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        banner.setStyleSheet(
            f"background-color: #483828; color: {_C['accent_orange']}; "
            f"font-weight: bold; font-size: 10pt; padding: 6px;"
        )
        main_layout.addWidget(banner)

        # ── Toolbar ──
        toolbar = QWidget()
        toolbar.setStyleSheet(f"background-color: {_C['bg_mid']};")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(4, 4, 4, 4)
        tb_layout.setSpacing(4)

        btn_style = (
            f"QPushButton {{ background-color: {_C['btn_bg']}; color: {_C['fg_main']}; "
            f"border: none; padding: 5px 12px; font-size: 9pt; }}"
            f"QPushButton:hover {{ background-color: {_C['btn_hover']}; color: {_C['fg_bright']}; }}"
            f"QPushButton:disabled {{ color: {_C['fg_dim']}; }}"
        )

        self._btn_browse = QPushButton(self.t("browse"))
        self._btn_browse.setStyleSheet(btn_style)
        self._btn_browse.clicked.connect(self._load_file)
        tb_layout.addWidget(self._btn_browse)
        self._tip(self._btn_browse,
                  "Load a FITS, XISF, or compressed FITS image",
                  "Charger une image FITS, XISF ou FITS compress\u00e9e")

        self._btn_analyze = QPushButton(self.t("analyze"))
        self._btn_analyze.setStyleSheet(btn_style)
        self._btn_analyze.setEnabled(False)
        self._btn_analyze.clicked.connect(self._run_analysis)
        tb_layout.addWidget(self._btn_analyze)
        self._tip(self._btn_analyze,
                  "Run star detection, PSF fitting, and backfocus diagnosis",
                  "Lancer la d\u00e9tection d'\u00e9toiles, l'ajustement PSF et le diagnostic")

        tb_layout.addSpacing(20)

        lbl_fwhm = QLabel(self.t("fwhm_est"))
        lbl_fwhm.setStyleSheet(f"color: {_C['fg_main']}; font-size: 9pt; background: transparent;")
        tb_layout.addWidget(lbl_fwhm)
        self._ent_fwhm = QLineEdit(str(ANALYSIS_DEFAULTS["fwhm_est"]))
        self._ent_fwhm.setFixedWidth(50)
        self._ent_fwhm.setStyleSheet(
            f"background-color: {_C['bg_light']}; color: {_C['fg_bright']}; "
            f"border: none; padding: 3px; font-size: 9pt;"
        )
        tb_layout.addWidget(self._ent_fwhm)
        self._tip(self._ent_fwhm,
                  "Estimated star FWHM in pixels (auto-adjusted if detection fails)",
                  "FWHM estim\u00e9 des \u00e9toiles en pixels (ajust\u00e9 auto si d\u00e9tection \u00e9choue)")

        tb_layout.addSpacing(12)

        lbl_thresh = QLabel(self.t("threshold"))
        lbl_thresh.setStyleSheet(f"color: {_C['fg_main']}; font-size: 9pt; background: transparent;")
        tb_layout.addWidget(lbl_thresh)
        self._ent_thresh = QLineEdit(str(ANALYSIS_DEFAULTS["threshold"]))
        self._ent_thresh.setFixedWidth(50)
        self._ent_thresh.setStyleSheet(
            f"background-color: {_C['bg_light']}; color: {_C['fg_bright']}; "
            f"border: none; padding: 3px; font-size: 9pt;"
        )
        tb_layout.addWidget(self._ent_thresh)
        self._tip(self._ent_thresh,
                  "Detection threshold in sigma above background (lower = more stars)",
                  "Seuil de d\u00e9tection en sigma au-dessus du fond (plus bas = plus d'\u00e9toiles)")

        tb_layout.addStretch()

        self._file_label = QLabel(self.t("no_file"))
        self._file_label.setStyleSheet(f"color: {_C['fg_dim']}; font-size: 8pt; background: transparent;")
        self._file_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tb_layout.addWidget(self._file_label)

        main_layout.addWidget(toolbar)

        # ── Plots area (tabbed) ──
        self._notebook = QTabWidget()
        self._notebook.setStyleSheet(f"""
            QTabWidget::pane {{ background: {_C['bg_dark']}; border: none; }}
            QTabBar::tab {{ background: {_C['btn_bg']}; color: {_C['fg_main']};
                           padding: 6px 14px; font-size: 9pt; border: none; }}
            QTabBar::tab:selected {{ background: {_C['bg_mid']}; color: {_C['fg_bright']}; }}
        """)

        # ── Tab 1: Analysis (FWHM map + Vector field) ──
        tab_analysis = QWidget()
        tab_analysis.setStyleSheet(f"background-color: {_C['bg_dark']};")
        tab_layout = QHBoxLayout(tab_analysis)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(3)

        self._fig_fwhm = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=_C["bg_dark"])
        self._ax_fwhm = self._fig_fwhm.add_subplot(111)
        self._canvas_fwhm = FigureCanvasQTAgg(self._fig_fwhm)
        tab_layout.addWidget(self._canvas_fwhm)

        self._fig_vec = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=_C["bg_dark"])
        self._ax_vec = self._fig_vec.add_subplot(111)
        self._canvas_vec = FigureCanvasQTAgg(self._fig_vec)
        tab_layout.addWidget(self._canvas_vec)

        self._notebook.addTab(tab_analysis, self.t("tab_analysis"))

        # ── Tab 2: Mosaic 3x3 ──
        tab_mosaic = QWidget()
        tab_mosaic.setStyleSheet(f"background-color: {_C['bg_dark']};")
        mosaic_layout = QVBoxLayout(tab_mosaic)
        mosaic_layout.setContentsMargins(0, 0, 0, 0)

        self._fig_mosaic = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=_C["bg_dark"])
        self._canvas_mosaic = FigureCanvasQTAgg(self._fig_mosaic)
        mosaic_layout.addWidget(self._canvas_mosaic)

        self._notebook.addTab(tab_mosaic, self.t("tab_mosaic"))

        main_layout.addWidget(self._notebook, stretch=1)

        # ── Diagnostics text ──
        self._diag_text = QTextEdit()
        self._diag_text.setReadOnly(True)
        self._diag_text.setMaximumHeight(110)
        self._diag_text.setStyleSheet(
            f"background-color: {_C['bg_mid']}; color: {_C['fg_main']}; "
            f"border: none; font-family: '{FONT_MONO}'; font-size: 9pt; padding: 6px;"
        )
        main_layout.addWidget(self._diag_text)

        # ── Progress bar ──
        prog_layout = QHBoxLayout()
        prog_layout.setContentsMargins(0, 0, 0, 0)

        self._progressbar = QProgressBar()
        self._progressbar.setRange(0, 100)
        self._progressbar.setValue(0)
        self._progressbar.setStyleSheet(f"""
            QProgressBar {{ background-color: {_C['bg_light']}; border: 1px solid {_C['border']};
                           border-radius: 3px; text-align: center; color: {_C['fg_dim']}; }}
            QProgressBar::chunk {{ background-color: {_C['accent_teal']}; border-radius: 2px; }}
        """)
        prog_layout.addWidget(self._progressbar)

        self._status_label = QLabel("")
        self._status_label.setFixedWidth(220)
        self._status_label.setStyleSheet(f"color: {_C['fg_dim']}; font-size: 8pt; background: transparent;")
        prog_layout.addWidget(self._status_label)

        main_layout.addLayout(prog_layout)

        self._setup_empty_axes()
        self.show()

    def _setup_empty_axes(self):
        """Set up dark-themed empty axes."""
        for ax, title_key in [(self._ax_fwhm, "fwhm_map_title"),
                              (self._ax_vec, "vector_title")]:
            ax.set_facecolor(_C["bg_dark"])
            ax.set_title(self.t(title_key), color=_C["fg_main"], fontsize=10)
            ax.tick_params(colors=_C["fg_dim"], labelsize=7)
            for spine in ax.spines.values():
                spine.set_color(_C["border"])
        self._fig_fwhm.tight_layout()
        self._fig_vec.tight_layout()
        self._canvas_fwhm.draw()
        self._canvas_vec.draw()

        self._fig_mosaic.clf()
        for idx in range(9):
            ax = self._fig_mosaic.add_subplot(3, 3, idx + 1)
            ax.set_facecolor(_C["bg_dark"])
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_color(_C["border"])
        self._fig_mosaic.tight_layout()
        self._canvas_mosaic.draw()

    # ── File loading ──
    def _load_file(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, self.t("browse"), "",
            "All supported (*.fits *.fit *.fts *.fits.fz *.fit.fz *.xisf "
            "*.FITS *.FIT *.FTS *.FITS.fz *.FIT.fz *.XISF);;"
            "FITS files (*.fits *.fit *.fts *.FITS *.FIT *.FTS);;"
            "Compressed FITS (*.fits.fz *.fit.fz *.FITS.fz *.FIT.fz);;"
            "XISF files (*.xisf *.XISF);;"
            "All files (*.*)")
        if not fp:
            return
        self._filepath = fp
        fname = os.path.basename(fp)
        self._file_label.setText(f"{self.t('file_label')} {fname}")
        self._file_label.setStyleSheet(f"color: {_C['fg_bright']}; font-size: 8pt; background: transparent;")
        self._btn_analyze.setEnabled(True)

    # ── Analysis thread management ──
    def _run_analysis(self):
        if self._thread and self._thread.is_alive():
            return
        if not self._filepath:
            return

        self._results = None
        self._error = None
        self._progress = (0, 1)
        self._progressbar.setValue(0)
        self._btn_analyze.setEnabled(False)
        self._btn_browse.setEnabled(False)

        try:
            fwhm_est = float(self._ent_fwhm.text())
        except ValueError:
            fwhm_est = ANALYSIS_DEFAULTS["fwhm_est"]
        try:
            threshold = float(self._ent_thresh.text())
        except ValueError:
            threshold = ANALYSIS_DEFAULTS["threshold"]

        self._worker_params = (fwhm_est, threshold)
        self._thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self._thread.start()
        self._poll_timer.start(100)

    def _analysis_worker(self):
        """Run the full analysis pipeline in a background thread."""
        try:
            fwhm_est, threshold = self._worker_params

            self._status_text = self.t("loading")
            self._progress = (5, 100)
            data, header = load_fits_data(self._filepath)
            self._data = data
            self._header = header

            bad_frame = _detect_frame_type(header)
            if bad_frame:
                self._error = self.t("warn_not_light", frametype=bad_frame)
                return

            self._status_text = self.t("detecting")
            self._progress = (15, 100)
            stars = detect_stars(data, fwhm_est=fwhm_est, threshold=threshold)

            if len(stars) < 3:
                self._error = self.t("too_few_stars", n=len(stars))
                return

            n_workers = max(1, min(os.cpu_count() or 4, len(stars), 16))
            use_parallel = n_workers > 1 and len(stars) >= 20
            fit_msg_key = "fitting_parallel" if use_parallel else "fitting"

            def progress_cb(n, total):
                pct = 20 + int(60 * n / max(total, 1))
                if use_parallel:
                    self._status_text = self.t(fit_msg_key, n=n, total=total,
                                               workers=n_workers)
                else:
                    self._status_text = self.t(fit_msg_key, n=n, total=total)
                self._progress = (pct, 100)

            self._status_text = self.t(fit_msg_key, n=0, total=len(stars),
                                       workers=n_workers) if use_parallel else \
                                self.t(fit_msg_key, n=0, total=len(stars))
            self._progress = (20, 100)
            fitted = fit_star_psfs(data, stars, progress_cb=progress_cb)

            if len(fitted) < 3:
                self._error = self.t("too_few_stars", n=len(fitted))
                return

            self._status_text = self.t("building_map")
            self._progress = (85, 100)
            h, w = data.shape
            surface = build_fwhm_surface(fitted, (h, w))

            self._status_text = self.t("classifying")
            self._progress = (92, 100)
            center = (w / 2, h / 2)
            classification = classify_backfocus_error(fitted, center)

            self._results = {
                "stars_detected": len(stars),
                "star_fits": fitted,
                "surface": surface,
                "classification": classification,
                "image_shape": (h, w),
            }
            self._status_text = self.t("done")
            self._progress = (100, 100)

        except Exception as e:
            self._error = str(e)

    def _poll_thread(self):
        """Poll the analysis thread for progress updates."""
        pct, _ = self._progress
        self._progressbar.setValue(pct)
        self._status_label.setText(self._status_text)

        if self._thread and self._thread.is_alive():
            return  # timer keeps running

        # Thread finished
        self._poll_timer.stop()
        self._btn_browse.setEnabled(True)
        if self._error:
            self._btn_analyze.setEnabled(True)
            self._show_error(self._error)
        elif self._results:
            self._btn_analyze.setEnabled(True)
            self._on_analysis_done()

    def _show_error(self, msg):
        self._diag_text.clear()
        self._diag_text.setHtml(
            f'<span style="color:{_C["accent_red"]}">{self.t("error", msg=msg)}</span>')

    # ── Display results ──
    def _on_analysis_done(self):
        r = self._results
        self._draw_fwhm_map(r)
        self._draw_vector_field(r)
        self._draw_mosaic(r)
        self._update_diagnostics(r)

    def _draw_fwhm_map(self, results):
        """Draw FWHM contour map with star scatter overlay."""
        self._fig_fwhm.clf()
        self._ax_fwhm = self._fig_fwhm.add_subplot(111)
        ax = self._ax_fwhm
        ax.set_facecolor(_C["bg_dark"])
        ax.set_title(self.t("fwhm_map_title"), color=_C["fg_main"], fontsize=10)

        fitted = results["star_fits"]
        surface = results["surface"]
        h, w = results["image_shape"]

        xs = [s["x"] for s in fitted]
        ys = [s["y"] for s in fitted]
        fwhms = [s["fwhm_geom"] for s in fitted]

        if surface is not None:
            extent = [0, w, h, 0]
            im = ax.contourf(surface["grid"], levels=20,
                             extent=extent,
                             cmap="inferno", alpha=0.85)
            cb = self._fig_fwhm.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
            cb.ax.tick_params(labelsize=7, colors=_C["fg_dim"])
            cb.outline.set_edgecolor(_C["border"])

        sc = ax.scatter(xs, ys, c=fwhms, cmap="inferno", s=12,
                        edgecolors=_C["fg_dim"], linewidths=0.3,
                        zorder=5, alpha=0.9)

        if surface is None:
            cb = self._fig_fwhm.colorbar(sc, ax=ax, shrink=0.85, pad=0.02)
            cb.ax.tick_params(labelsize=7, colors=_C["fg_dim"])
            cb.outline.set_edgecolor(_C["border"])

        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.set_aspect("equal")
        ax.tick_params(colors=_C["fg_dim"], labelsize=7)
        for spine in ax.spines.values():
            spine.set_color(_C["border"])

        self._fig_fwhm.tight_layout()
        self._canvas_fwhm.draw()

    def _draw_vector_field(self, results):
        """Draw PSF elongation vector field."""
        self._fig_vec.clf()
        self._ax_vec = self._fig_vec.add_subplot(111)
        ax = self._ax_vec
        ax.set_facecolor(_C["bg_dark"])
        ax.set_title(self.t("vector_title"), color=_C["fg_main"], fontsize=10)

        fitted = results["star_fits"]
        h, w = results["image_shape"]
        cx, cy = w / 2, h / 2

        max_r = math.sqrt(cx**2 + cy**2)
        n_zones = ANALYSIS_DEFAULTS["annular_zones"]
        for i in range(1, n_zones + 1):
            r = max_r * i / n_zones
            circle = matplotlib.patches.Circle((cx, cy), r, fill=False,
                                               edgecolor=_C["border"],
                                               linewidth=0.5,
                                               linestyle="--", alpha=0.5)
            ax.add_patch(circle)

        ax.plot(cx, cy, "+", color=_C["accent_teal"], markersize=10,
                markeredgewidth=1.5, zorder=10)

        ecc_thresh = ANALYSIS_DEFAULTS["ecc_threshold"]

        for s in fitted:
            dx = s["x"] - cx
            dy = s["y"] - cy
            r = math.sqrt(dx**2 + dy**2)
            if r < 1:
                continue

            radial_angle = math.atan2(dy, dx)
            pa = s["position_angle"]
            delta = abs(pa - radial_angle) % math.pi
            if delta > math.pi / 2:
                delta = math.pi - delta

            radial_score = math.cos(2 * delta)

            if radial_score >= 0:
                t = radial_score
                color = (0.53 * (1 - t) + 0.33 * t,
                         0.53 * (1 - t) + 0.78 * t,
                         0.53 * (1 - t) + 0.47 * t)
            else:
                t = -radial_score
                color = (0.53 * (1 - t) + 0.83 * t,
                         0.53 * (1 - t) + 0.66 * t,
                         0.53 * (1 - t) + 0.44 * t)

            if s["eccentricity"] < ecc_thresh:
                ax.plot(s["x"], s["y"], "o", color=_C["fg_dim"],
                        markersize=2, alpha=0.4)
                continue

            length = s["fwhm_major"] * 2.5
            width = s["fwhm_minor"] * 2.5
            angle_deg = math.degrees(pa)
            ell = Ellipse((s["x"], s["y"]), length, width,
                          angle=angle_deg, fill=False,
                          edgecolor=color, linewidth=1.2, alpha=0.8)
            ax.add_patch(ell)

        ax.set_xlim(0, w)
        ax.set_ylim(h, 0)
        ax.set_aspect("equal")
        ax.tick_params(colors=_C["fg_dim"], labelsize=7)
        for spine in ax.spines.values():
            spine.set_color(_C["border"])

        self._fig_vec.tight_layout()
        self._canvas_vec.draw()

    def _draw_mosaic(self, results):
        """Draw 3x3 mosaic of image tiles."""
        self._fig_mosaic.clf()

        fitted = results["star_fits"]
        h, w = results["image_shape"]
        tiles = compute_mosaic_tiles(self._data, fitted, (h, w))

        center_fwhm = None
        for tile in tiles:
            if tile["is_center"] and tile["mean_fwhm"] is not None:
                center_fwhm = tile["mean_fwhm"]
                break

        for tile in tiles:
            idx = tile["row"] * 3 + tile["col"] + 1
            ax = self._fig_mosaic.add_subplot(3, 3, idx)
            ax.set_facecolor(_C["bg_dark"])

            crop = tile["crop"]

            p1 = np.percentile(crop, 1)
            p99 = np.percentile(crop, 99.5)
            ax.imshow(crop, cmap="gray", vmin=p1, vmax=p99,
                      origin="lower", aspect="equal")

            if tile["star_xy_local"]:
                sx = [xy[0] for xy in tile["star_xy_local"]]
                sy = [xy[1] for xy in tile["star_xy_local"]]
                ax.scatter(sx, sy, s=60, facecolors="none",
                           edgecolors=_C["accent_teal"], linewidths=0.8,
                           zorder=5)

            ax.set_title(self.t(tile["name_key"]),
                         color=_C["fg_main"], fontsize=8, pad=3)

            if tile["mean_fwhm"] is not None:
                label = (self.t("tile_fwhm", v=tile["mean_fwhm"]) +
                         " | " + self.t("tile_stars", n=tile["star_count"]))
            else:
                label = self.t("tile_no_stars")
            ax.text(0.5, 0.03, label, transform=ax.transAxes,
                    ha="center", va="bottom", fontsize=7,
                    color=_C["fg_bright"],
                    bbox=dict(boxstyle="round,pad=0.2",
                              facecolor=_C["bg_dark"], alpha=0.75,
                              edgecolor="none"))

            border_color = _C["border"]
            if center_fwhm is not None and tile["mean_fwhm"] is not None:
                ratio = tile["mean_fwhm"] / center_fwhm
                if ratio <= 1.05:
                    border_color = _C["accent_green"]
                elif ratio <= 1.20:
                    border_color = _C["accent_teal"]
                elif ratio <= 1.40:
                    border_color = _C["accent_orange"]
                else:
                    border_color = _C["accent_red"]

            for spine in ax.spines.values():
                spine.set_color(border_color)
                spine.set_linewidth(2)
            ax.set_xticks([])
            ax.set_yticks([])

        self._fig_mosaic.tight_layout(pad=1.5)
        self._canvas_mosaic.draw()

    def _update_diagnostics(self, results):
        """Update the diagnostics text panel with analysis results."""
        self._diag_text.clear()

        fitted = results["star_fits"]
        surface = results["surface"]
        cls = results["classification"]
        h, w = results["image_shape"]

        lines = []

        # Image info
        lines.append(f'<span style="color:{_C["fg_dim"]}">{self.t("image_size", w=w, h=h)}</span>'
                     f'&nbsp;&nbsp;&nbsp;'
                     f'<span style="color:{_C["fg_main"]}">{self.t("stars_detected", n=results["stars_detected"])}</span>'
                     f'&nbsp;&nbsp;&nbsp;'
                     f'<span style="color:{_C["fg_main"]}">{self.t("stars_fitted", n=len(fitted))}</span>')

        # Mean FWHM
        fwhm_line = ""
        if fitted:
            mean_fwhm = np.mean([s["fwhm_geom"] for s in fitted])
            fwhm_line += f'<span style="color:{_C["accent_teal"]}">{self.t("mean_fwhm", v=mean_fwhm)}</span>&nbsp;&nbsp;&nbsp;'
        if surface is not None:
            fwhm_line += f'<span style="color:{_C["accent_teal"]}">{self.t("fwhm_gradient", v=surface["gradient_pct"])}</span>&nbsp;&nbsp;&nbsp;'
        if fitted:
            mean_ecc = np.mean([s["eccentricity"] for s in fitted])
            fwhm_line += f'<span style="color:{_C["fg_main"]}">{self.t("mean_ecc", v=mean_ecc)}</span>'
        if fwhm_line:
            lines.append(fwhm_line)

        # Radial score
        score = cls["score"]
        if score > 0.1:
            interp = self.t("interp_radial")
        elif score < -0.1:
            interp = self.t("interp_tangential")
        else:
            interp = self.t("interp_mixed")
        lines.append(f'<span style="color:{_C["fg_main"]}">{self.t("radial_score", v=score, interp=interp)}</span>')

        # Verdict
        verdict = cls["verdict"]
        if verdict == "correct":
            lines.append(f'<span style="color:{_C["accent_green"]}">{self.t("verdict_correct")}</span>')
        elif verdict == "short":
            lines.append(f'<span style="color:{_C["accent_orange"]}">{self.t("verdict_short")}</span>')
        elif verdict == "long":
            lines.append(f'<span style="color:{_C["accent_orange"]}">{self.t("verdict_long")}</span>')

        # Note
        lines.append(f'<span style="color:{_C["fg_dim"]}">{self.t("note_single")}</span>')

        self._diag_text.setHtml("<br>".join(lines))
