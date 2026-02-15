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

import math
import os
import struct
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import zlib

import numpy as np
from scipy.optimize import curve_fit
from astropy.io import fits
from astropy.stats import sigma_clipped_stats, sigma_clip
from photutils.detection import DAOStarFinder
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Ellipse
import matplotlib.colors as mcolors

# ═══════════════════════════════════════════════════════════════════
#  TRANSLATIONS (EN / FR)
# ═══════════════════════════════════════════════════════════════════
TR_FITS = {
    "win_title":        {"en": "FITS / XISF Backfocus Analyzer", "fr": "Analyseur FITS / XISF de backfocus"},
    "browse":           {"en": "Browse…", "fr": "Parcourir…"},
    "analyze":          {"en": "Analyze", "fr": "Analyser"},
    "fwhm_est":         {"en": "FWHM est:", "fr": "FWHM est. :"},
    "threshold":        {"en": "Threshold:", "fr": "Seuil :"},
    "no_file":          {"en": "No file selected", "fr": "Aucun fichier sélectionné"},
    "loading":          {"en": "Loading image…", "fr": "Chargement image…"},
    "detecting":        {"en": "Detecting stars…", "fr": "Détection des étoiles…"},
    "fitting":          {"en": "Fitting PSFs ({n}/{total})…", "fr": "Ajustement PSF ({n}/{total})…"},
    "building_map":     {"en": "Building FWHM map…", "fr": "Construction carte FWHM…"},
    "classifying":      {"en": "Classifying backfocus…", "fr": "Classification backfocus…"},
    "done":             {"en": "Done.", "fr": "Terminé."},
    "error":            {"en": "Error: {msg}", "fr": "Erreur : {msg}"},
    "stars_detected":   {"en": "Stars detected: {n}", "fr": "Étoiles détectées : {n}"},
    "stars_fitted":     {"en": "Stars fitted: {n}", "fr": "Étoiles ajustées : {n}"},
    "mean_fwhm":        {"en": "Mean FWHM: {v:.2f} px", "fr": "FWHM moyen : {v:.2f} px"},
    "fwhm_gradient":    {"en": "FWHM gradient (center→edge): {v:+.1f}%",
                         "fr": "Gradient FWHM (centre→bord) : {v:+.1f}%"},
    "mean_ecc":         {"en": "Mean eccentricity: {v:.3f}", "fr": "Excentricité moy. : {v:.3f}"},
    "verdict_correct":  {"en": "VERDICT: Backfocus appears CORRECT",
                         "fr": "VERDICT : Backfocus semble CORRECT"},
    "verdict_short":    {"en": "VERDICT: Backfocus TOO SHORT → add spacers",
                         "fr": "VERDICT : Backfocus TROP COURT → ajouter des espaceurs"},
    "verdict_long":     {"en": "VERDICT: Backfocus TOO LONG → remove spacers",
                         "fr": "VERDICT : Backfocus TROP LONG → retirer des espaceurs"},
    "radial_score":     {"en": "Radial score: {v:+.3f}  ({interp})",
                         "fr": "Score radial : {v:+.3f}  ({interp})"},
    "interp_radial":    {"en": "radial elongation", "fr": "allongement radial"},
    "interp_tangential":{"en": "tangential elongation", "fr": "allongement tangentiel"},
    "interp_mixed":     {"en": "mixed / neutral", "fr": "mixte / neutre"},
    "fwhm_map_title":   {"en": "FWHM Map (px)", "fr": "Carte FWHM (px)"},
    "vector_title":     {"en": "PSF Elongation Field", "fr": "Champ d'allongement PSF"},
    "too_few_stars":    {"en": "Too few stars detected ({n}). Try lowering threshold.",
                         "fr": "Trop peu d'étoiles ({n}). Essayez un seuil plus bas."},
    "file_label":       {"en": "File:", "fr": "Fichier :"},
    "image_size":       {"en": "Image: {w}×{h}", "fr": "Image : {w}×{h}"},
    "note_single":      {"en": "Note: Single-image analysis gives direction only, not precise offset.",
                         "fr": "Note : L'analyse mono-image donne la direction, pas l'écart précis."},
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
}

# ═══════════════════════════════════════════════════════════════════
#  DARK SPACE COLOR PALETTE (matches backfocus.py)
# ═══════════════════════════════════════════════════════════════════
_C = {
    "bg_dark":   "#101018",
    "bg_mid":    "#181822",
    "bg_light":  "#22222E",
    "fg_main":   "#D0D0DA",
    "fg_dim":    "#706880",
    "fg_bright": "#EDE8F2",
    "accent_teal":   "#72C4B8",
    "accent_green":  "#88C8A0",
    "accent_red":    "#D08070",
    "accent_orange": "#D4A870",
    "accent_purple": "#B08AD8",
    "border":    "#302838",
    "btn_bg":    "#262630",
    "btn_hover": "#38304A",
}

# ═══════════════════════════════════════════════════════════════════
#  ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def _is_xisf(filepath):
    """Check if file is XISF by magic bytes."""
    try:
        with open(filepath, "rb") as f:
            return f.read(8) == b"XISF0100"
    except OSError:
        return False


def _load_xisf(filepath):
    """Load an XISF file, return (2D float64 array, dict header).

    Supports attached data blocks with optional zlib compression.
    """
    with open(filepath, "rb") as f:
        magic = f.read(8)
        if magic != b"XISF0100":
            raise ValueError("Not a valid XISF file (bad magic)")
        header_len, _reserved = struct.unpack("<II", f.read(8))
        xml_bytes = f.read(header_len)

        # Parse XML — strip namespace if present
        xml_str = xml_bytes.decode("utf-8", errors="replace")
        # Remove namespace declarations for easier parsing
        xml_str = xml_str.replace(' xmlns="http://www.pixinsight.com/xisf"', "")
        xml_str = xml_str.replace(" xmlns='http://www.pixinsight.com/xisf'", "")
        root = ET.fromstring(xml_str)

        # Find first Image element
        img_el = root.find(".//Image")
        if img_el is None:
            raise ValueError("No Image element found in XISF header")

        # Parse geometry: "width:height:channels"
        geom = img_el.get("geometry", "")
        parts = geom.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid XISF geometry: {geom}")
        width = int(parts[0])
        height = int(parts[1])
        channels = int(parts[2]) if len(parts) > 2 else 1

        # Sample format
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

        # Color space and pixel storage
        color_space = img_el.get("colorSpace", "Gray")
        pixel_storage = img_el.get("pixelStorage", "planar")

        # Data location
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
            b64_data = location.split(":", 1)[1]
            # Might also be in element text
            data_el = img_el.find("Data")
            if data_el is not None and data_el.text:
                b64_data = data_el.text
            raw = base64.b64decode(b64_data)
        else:
            raise ValueError(f"Unsupported XISF location: {location}")

        # Decompress if needed
        if compression:
            codec = compression.split(":")[0].lower()
            if codec in ("zlib", "zlib+sh"):
                uncompressed_size = int(compression.split(":")[1]) if ":" in compression else None
                raw = zlib.decompress(raw)
            elif codec in ("lz4", "lz4+sh", "lz4hc", "lz4hc+sh"):
                try:
                    import lz4.block
                    uncompressed_size = int(compression.split(":")[1]) if ":" in compression else 0
                    raw = lz4.block.decompress(raw, uncompressed_size=uncompressed_size)
                except ImportError:
                    raise ValueError("XISF file uses LZ4 compression. Install: pip install lz4")
            elif codec in ("zstd", "zstd+sh"):
                try:
                    import zstandard
                    raw = zstandard.ZstdDecompressor().decompress(raw)
                except ImportError:
                    raise ValueError("XISF file uses Zstandard compression. Install: pip install zstandard")

        data = np.frombuffer(raw, dtype=dtype)

        # Reshape
        if channels > 1:
            if pixel_storage == "planar":
                data = data.reshape(channels, height, width)
            else:
                data = data.reshape(height, width, channels)
        else:
            data = data.reshape(height, width)

    # Collect header info
    header = {"XISF": True, "NAXIS1": width, "NAXIS2": height,
              "CHANNELS": channels, "FORMAT": sample_fmt,
              "COLORSPACE": color_space}
    for prop in root.iter("FITSKeyword"):
        header[prop.get("name", "")] = prop.get("value", "")

    return data, header


def load_fits_data(filepath):
    """Load a FITS or XISF image file, return (2D float64 array, header).

    Supported: .fits, .fit, .fts, .fits.fz, .fit.fz (all case-insensitive),
               .xisf (PixInsight).
    Handles single/multi-extension, RGB→luminance, auto-bin if large.
    """
    # Route to XISF loader if applicable
    name_lower = os.path.basename(filepath).lower()
    if name_lower.endswith(".xisf") or _is_xisf(filepath):
        data, header = _load_xisf(filepath)
    else:
        # FITS / compressed FITS (.fits.fz) — astropy handles fpack natively
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

    # RGB → luminance (ITU-R BT.601)
    if data.ndim == 3:
        if data.shape[0] == 3:
            data = 0.299 * data[0] + 0.587 * data[1] + 0.114 * data[2]
        elif data.shape[2] == 3:
            data = 0.299 * data[:, :, 0] + 0.587 * data[:, :, 1] + 0.114 * data[:, :, 2]
        else:
            data = data[0]  # take first plane

    data = data.astype(np.float64)

    # Replace NaN with median
    nan_mask = np.isnan(data)
    if np.any(nan_mask):
        med = np.nanmedian(data)
        data[nan_mask] = med

    # Auto-bin 2x2 if very large
    th = ANALYSIS_DEFAULTS["autobin_threshold"]
    if data.shape[0] > th or data.shape[1] > th:
        h, w = data.shape
        h2, w2 = h // 2 * 2, w // 2 * 2
        data = data[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).mean(axis=(1, 3))

    return data, header


def detect_stars(data, fwhm_est=None, threshold=None):
    """Detect stars using DAOStarFinder. Returns list of dicts with x, y, flux."""
    if fwhm_est is None:
        fwhm_est = ANALYSIS_DEFAULTS["fwhm_est"]
    if threshold is None:
        threshold = ANALYSIS_DEFAULTS["threshold"]

    mean, median, std = sigma_clipped_stats(data, sigma=3.0)

    finder = DAOStarFinder(fwhm=fwhm_est, threshold=threshold * std)
    sources = finder(data - median)

    if sources is None or len(sources) == 0:
        return []

    margin = ANALYSIS_DEFAULTS["edge_margin"]
    h, w = data.shape
    mask = ((sources["xcentroid"] > margin) &
            (sources["xcentroid"] < w - margin) &
            (sources["ycentroid"] > margin) &
            (sources["ycentroid"] < h - margin))
    sources = sources[mask]

    if len(sources) == 0:
        return []

    # Sort by flux descending, keep top N
    sources.sort("flux")
    sources.reverse()
    limit = ANALYSIS_DEFAULTS["star_limit"]
    if len(sources) > limit:
        sources = sources[:limit]

    stars = []
    for row in sources:
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


def fit_star_psfs(data, stars, box_size=None, progress_cb=None):
    """Fit elliptical 2D Gaussian to each star. Returns list of result dicts."""
    if box_size is None:
        box_size = ANALYSIS_DEFAULTS["box_size"]

    half = box_size // 2
    h, w = data.shape
    results = []
    interval = ANALYSIS_DEFAULTS["progress_interval"]

    y_grid, x_grid = np.mgrid[0:box_size, 0:box_size]
    xy = (x_grid.ravel(), y_grid.ravel())

    for i, star in enumerate(stars):
        sx, sy = int(round(star["x"])), int(round(star["y"]))
        x0 = sx - half
        y0 = sy - half

        if x0 < 0 or y0 < 0 or x0 + box_size > w or y0 + box_size > h:
            continue

        cutout = data[y0:y0 + box_size, x0:x0 + box_size].copy()
        bg = np.median(np.concatenate([
            cutout[0, :], cutout[-1, :], cutout[:, 0], cutout[:, -1]
        ]))
        cutout_sub = cutout - bg

        amp_guess = cutout_sub.max()
        if amp_guess <= 0:
            continue

        cx_local = star["x"] - x0
        cy_local = star["y"] - y0
        sig_guess = ANALYSIS_DEFAULTS["fwhm_est"] / 2.355

        p0 = [amp_guess, cx_local, cy_local, sig_guess, sig_guess, 0.0, 0.0]
        bounds_lo = [0, cx_local - half/2, cy_local - half/2, 0.5, 0.5, -math.pi, -np.inf]
        bounds_hi = [amp_guess * 3, cx_local + half/2, cy_local + half/2,
                     half, half, math.pi, amp_guess]

        try:
            popt, pcov = curve_fit(_gaussian_2d, xy, cutout_sub.ravel(),
                                   p0=p0, bounds=(bounds_lo, bounds_hi),
                                   maxfev=2000)
        except (RuntimeError, ValueError):
            continue

        amp, fit_cx, fit_cy, sigma_x, sigma_y, theta, offset = popt

        # Compute FWHM and eccentricity
        fwhm_x = abs(sigma_x) * 2.355
        fwhm_y = abs(sigma_y) * 2.355
        fwhm_major = max(fwhm_x, fwhm_y)
        fwhm_minor = min(fwhm_x, fwhm_y)

        if fwhm_major < 0.5:
            continue

        eccentricity = math.sqrt(1 - (fwhm_minor / fwhm_major) ** 2)

        # Position angle: angle of major axis
        if fwhm_x >= fwhm_y:
            pa = theta
        else:
            pa = theta + math.pi / 2
        # Normalize to [-pi/2, pi/2]
        pa = ((pa + math.pi / 2) % math.pi) - math.pi / 2

        # Chi-squared estimate
        model = _gaussian_2d(xy, *popt)
        residuals = cutout_sub.ravel() - model
        chi2 = np.sum(residuals**2) / (amp_guess**2 + 1e-10) * box_size

        # Reject bad fits
        if chi2 > ANALYSIS_DEFAULTS["max_chi2"]:
            continue
        if eccentricity > ANALYSIS_DEFAULTS["max_eccentricity"]:
            continue
        if fwhm_major > box_size / 2:
            continue

        results.append({
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
        })

        if progress_cb and (i + 1) % interval == 0:
            progress_cb(i + 1, len(stars))

    if progress_cb:
        progress_cb(len(stars), len(stars))

    return results


def build_fwhm_surface(star_fits, image_shape):
    """Build FWHM polynomial surface from fitted stars.

    Returns dict with grid, polynomial coeffs, gradient_pct, center/edge FWHM.
    """
    if len(star_fits) < 6:
        return None

    h, w = image_shape
    xs = np.array([s["x"] for s in star_fits])
    ys = np.array([s["y"] for s in star_fits])
    fwhms = np.array([s["fwhm_geom"] for s in star_fits])

    # Normalize coordinates to [-1, 1]
    xn = (xs - w / 2) / (w / 2)
    yn = (ys - h / 2) / (h / 2)

    # Polynomial degree 2: 1, x, y, x^2, xy, y^2
    A = np.column_stack([np.ones_like(xn), xn, yn, xn**2, xn * yn, yn**2])

    # Iterative sigma-clipped fit
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

    # Build grid for visualization
    gs = ANALYSIS_DEFAULTS["grid_size"]
    gx = np.linspace(-1, 1, gs)
    gy = np.linspace(-1, 1, gs)
    gx2d, gy2d = np.meshgrid(gx, gy)
    A_grid = np.column_stack([np.ones(gs * gs), gx2d.ravel(), gy2d.ravel(),
                              gx2d.ravel()**2, gx2d.ravel() * gy2d.ravel(),
                              gy2d.ravel()**2])
    fwhm_grid = (A_grid @ coeffs).reshape(gs, gs)

    # Center and edge FWHM
    center_fwhm = coeffs[0]  # value at (0,0)
    # Average at the 4 edges
    edge_vals = [
        np.polyval([coeffs[3], coeffs[1], coeffs[0]], 1),   # x=1,y=0
        np.polyval([coeffs[3], coeffs[1], coeffs[0]], -1),  # x=-1,y=0
    ]
    # Also evaluate at corners of the grid edge
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
        "grid_extent": [0, w, h, 0],  # for imshow
        "center_fwhm": center_fwhm,
        "edge_fwhm": edge_fwhm,
        "gradient_pct": gradient_pct,
        "mask": mask,
    }


def classify_backfocus_error(star_fits, center):
    """Classify backfocus error via radial vs tangential elongation.

    Returns dict with score, verdict, zone_scores.
    """
    cx, cy = center
    ecc_thresh = ANALYSIS_DEFAULTS["ecc_threshold"]
    n_zones = ANALYSIS_DEFAULTS["annular_zones"]
    zone_weights = ANALYSIS_DEFAULTS["annular_weights"]

    # Compute max radius
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
        # Normalize delta to [0, pi/2]
        delta = delta % math.pi
        if delta > math.pi / 2:
            delta = math.pi - delta

        # radial_score: +1 = radial, -1 = tangential
        radial_score = math.cos(2 * delta)
        # Weight by eccentricity
        weighted = radial_score * s["eccentricity"]

        # Determine zone (0-based)
        zone_frac = r / max_r
        zone_idx = min(int(zone_frac * n_zones), n_zones - 1)
        zone_sums[zone_idx] += weighted
        zone_counts[zone_idx] += 1

    # Compute zone averages and global weighted score
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

    # Classify
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


# ═══════════════════════════════════════════════════════════════════
#  UI WINDOW
# ═══════════════════════════════════════════════════════════════════

class FITSAnalyzerWindow:
    """Toplevel window for FITS backfocus analysis."""

    def __init__(self, app):
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
        self._build()

    def t(self, key, **kw):
        e = TR_FITS.get(key, {})
        s = e.get(self.lang, e.get("en", key))
        return s.format(**kw) if kw else s

    # ── Build UI ──
    def _build(self):
        self.win = tk.Toplevel(self.app.root)
        self.win.title(self.t("win_title"))
        self.win.geometry("1200x820")
        self.win.configure(bg=_C["bg_dark"])
        self.win.minsize(900, 650)

        # ── Toolbar ──
        toolbar = tk.Frame(self.win, bg=_C["bg_mid"], bd=0, highlightthickness=0)
        toolbar.pack(fill=tk.X, padx=6, pady=(6, 3))

        btn_style = {"bg": _C["btn_bg"], "fg": _C["fg_main"],
                     "activebackground": _C["btn_hover"], "activeforeground": _C["fg_bright"],
                     "relief": "flat", "bd": 0, "padx": 10, "pady": 4,
                     "font": ("Segoe UI", 9)}

        self._btn_browse = tk.Button(toolbar, text=self.t("browse"), command=self._load_file, **btn_style)
        self._btn_browse.pack(side=tk.LEFT, padx=(4, 2))

        self._btn_analyze = tk.Button(toolbar, text=self.t("analyze"), command=self._run_analysis,
                                      state=tk.DISABLED, **btn_style)
        self._btn_analyze.pack(side=tk.LEFT, padx=2)

        sep = tk.Frame(toolbar, width=20, bg=_C["bg_mid"])
        sep.pack(side=tk.LEFT)

        tk.Label(toolbar, text=self.t("fwhm_est"), bg=_C["bg_mid"],
                 fg=_C["fg_main"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 2))
        self._var_fwhm = tk.StringVar(value=str(ANALYSIS_DEFAULTS["fwhm_est"]))
        self._ent_fwhm = tk.Entry(toolbar, textvariable=self._var_fwhm, width=5,
                                  bg=_C["bg_light"], fg=_C["fg_bright"],
                                  insertbackground=_C["fg_bright"], relief="flat",
                                  font=("Segoe UI", 9))
        self._ent_fwhm.pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text=self.t("threshold"), bg=_C["bg_mid"],
                 fg=_C["fg_main"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(12, 2))
        self._var_thresh = tk.StringVar(value=str(ANALYSIS_DEFAULTS["threshold"]))
        self._ent_thresh = tk.Entry(toolbar, textvariable=self._var_thresh, width=5,
                                    bg=_C["bg_light"], fg=_C["fg_bright"],
                                    insertbackground=_C["fg_bright"], relief="flat",
                                    font=("Segoe UI", 9))
        self._ent_thresh.pack(side=tk.LEFT, padx=2)

        # File label on right
        self._file_label = tk.Label(toolbar, text=self.t("no_file"), bg=_C["bg_mid"],
                                    fg=_C["fg_dim"], font=("Segoe UI", 8),
                                    anchor=tk.E)
        self._file_label.pack(side=tk.RIGHT, padx=6, fill=tk.X, expand=True)

        # ── Plots area ──
        plots_frame = tk.Frame(self.win, bg=_C["bg_dark"])
        plots_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)

        # FWHM map (left)
        self._fig_fwhm = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=_C["bg_dark"])
        self._ax_fwhm = self._fig_fwhm.add_subplot(111)
        self._canvas_fwhm = FigureCanvasTkAgg(self._fig_fwhm, master=plots_frame)
        self._canvas_fwhm.get_tk_widget().configure(bg=_C["bg_dark"], highlightthickness=0)
        self._canvas_fwhm.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))

        # Vector field (right)
        self._fig_vec = Figure(figsize=(5.5, 4.2), dpi=100, facecolor=_C["bg_dark"])
        self._ax_vec = self._fig_vec.add_subplot(111)
        self._canvas_vec = FigureCanvasTkAgg(self._fig_vec, master=plots_frame)
        self._canvas_vec.get_tk_widget().configure(bg=_C["bg_dark"], highlightthickness=0)
        self._canvas_vec.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0))

        self._setup_empty_axes()

        # ── Diagnostics text ──
        diag_frame = tk.Frame(self.win, bg=_C["bg_mid"], bd=0, highlightthickness=0)
        diag_frame.pack(fill=tk.X, padx=6, pady=(3, 2))

        self._diag_text = tk.Text(diag_frame, height=6, bg=_C["bg_mid"],
                                  fg=_C["fg_main"], font=("Consolas", 9),
                                  relief="flat", bd=0, wrap=tk.WORD,
                                  state=tk.DISABLED, cursor="arrow",
                                  selectbackground=_C["bg_light"])
        self._diag_text.pack(fill=tk.X, padx=6, pady=4)

        self._diag_text.tag_configure("ok", foreground=_C["accent_green"])
        self._diag_text.tag_configure("warn", foreground=_C["accent_orange"])
        self._diag_text.tag_configure("bad", foreground=_C["accent_red"])
        self._diag_text.tag_configure("info", foreground=_C["fg_main"])
        self._diag_text.tag_configure("dim", foreground=_C["fg_dim"])
        self._diag_text.tag_configure("accent", foreground=_C["accent_teal"])

        # ── Progress bar ──
        prog_frame = tk.Frame(self.win, bg=_C["bg_dark"])
        prog_frame.pack(fill=tk.X, padx=6, pady=(0, 6))

        self._progress_var = tk.DoubleVar(value=0)
        style = ttk.Style()
        style.configure("FITS.Horizontal.TProgressbar",
                        troughcolor=_C["bg_light"],
                        background=_C["accent_teal"],
                        darkcolor=_C["accent_teal"],
                        lightcolor=_C["accent_teal"],
                        bordercolor=_C["border"])
        self._progressbar = ttk.Progressbar(prog_frame, variable=self._progress_var,
                                            maximum=100, mode="determinate",
                                            style="FITS.Horizontal.TProgressbar")
        self._progressbar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 8))

        self._status_label = tk.Label(prog_frame, text="", bg=_C["bg_dark"],
                                      fg=_C["fg_dim"], font=("Segoe UI", 8),
                                      anchor=tk.W, width=30)
        self._status_label.pack(side=tk.LEFT)

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

    # ── File loading ──
    def _load_file(self):
        fp = filedialog.askopenfilename(
            title=self.t("browse"),
            filetypes=[("All supported", "*.fits *.fit *.fts *.fits.fz *.fit.fz *.xisf "
                                         "*.FITS *.FIT *.FTS *.FITS.fz *.FIT.fz *.XISF"),
                       ("FITS files", "*.fits *.fit *.fts *.FITS *.FIT *.FTS"),
                       ("Compressed FITS", "*.fits.fz *.fit.fz *.FITS.fz *.FIT.fz"),
                       ("XISF files", "*.xisf *.XISF"),
                       ("All files", "*.*")])
        if not fp:
            return
        self._filepath = fp
        fname = fp.rsplit("/", 1)[-1] if "/" in fp else fp.rsplit("\\", 1)[-1]
        self._file_label.configure(text=f"{self.t('file_label')} {fname}",
                                   fg=_C["fg_bright"])
        self._btn_analyze.configure(state=tk.NORMAL)

    # ── Analysis thread management ──
    def _run_analysis(self):
        if self._thread and self._thread.is_alive():
            return
        if not self._filepath:
            return

        self._results = None
        self._error = None
        self._progress = (0, 1)
        self._progress_var.set(0)
        self._btn_analyze.configure(state=tk.DISABLED)
        self._btn_browse.configure(state=tk.DISABLED)

        self._thread = threading.Thread(target=self._analysis_worker, daemon=True)
        self._thread.start()
        self._poll_thread()

    def _analysis_worker(self):
        """Run the full analysis pipeline in a background thread."""
        try:
            # Parse user parameters
            try:
                fwhm_est = float(self._var_fwhm.get())
            except ValueError:
                fwhm_est = ANALYSIS_DEFAULTS["fwhm_est"]
            try:
                threshold = float(self._var_thresh.get())
            except ValueError:
                threshold = ANALYSIS_DEFAULTS["threshold"]

            # 1. Load FITS
            self._status_text = self.t("loading")
            self._progress = (5, 100)
            data, header = load_fits_data(self._filepath)
            self._data = data
            self._header = header

            # 2. Detect stars
            self._status_text = self.t("detecting")
            self._progress = (15, 100)
            stars = detect_stars(data, fwhm_est=fwhm_est, threshold=threshold)

            # Retry with lower threshold if too few
            if len(stars) < ANALYSIS_DEFAULTS["min_stars"]:
                retry_thresh = ANALYSIS_DEFAULTS["retry_threshold"]
                if retry_thresh < threshold:
                    stars = detect_stars(data, fwhm_est=fwhm_est, threshold=retry_thresh)

            if len(stars) < 3:
                self._error = self.t("too_few_stars", n=len(stars))
                return

            # 3. Fit PSFs
            def progress_cb(n, total):
                pct = 20 + int(60 * n / max(total, 1))
                self._status_text = self.t("fitting", n=n, total=total)
                self._progress = (pct, 100)

            self._status_text = self.t("fitting", n=0, total=len(stars))
            self._progress = (20, 100)
            fitted = fit_star_psfs(data, stars, progress_cb=progress_cb)

            if len(fitted) < 3:
                self._error = self.t("too_few_stars", n=len(fitted))
                return

            # 4. Build FWHM surface
            self._status_text = self.t("building_map")
            self._progress = (85, 100)
            h, w = data.shape
            surface = build_fwhm_surface(fitted, (h, w))

            # 5. Classify
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
        """Poll the analysis thread every 100ms for progress updates."""
        if self._thread and self._thread.is_alive():
            pct, _ = self._progress
            self._progress_var.set(pct)
            self._status_label.configure(text=self._status_text)
            self.win.after(100, self._poll_thread)
        else:
            # Thread finished
            pct, _ = self._progress
            self._progress_var.set(pct)
            self._status_label.configure(text=self._status_text)
            self._btn_browse.configure(state=tk.NORMAL)
            if self._error:
                self._btn_analyze.configure(state=tk.NORMAL)
                self._show_error(self._error)
            elif self._results:
                self._btn_analyze.configure(state=tk.NORMAL)
                self._on_analysis_done()

    def _show_error(self, msg):
        self._diag_text.configure(state=tk.NORMAL)
        self._diag_text.delete("1.0", tk.END)
        self._diag_text.insert(tk.END, self.t("error", msg=msg), "bad")
        self._diag_text.configure(state=tk.DISABLED)

    # ── Display results ──
    def _on_analysis_done(self):
        r = self._results
        self._draw_fwhm_map(r)
        self._draw_vector_field(r)
        self._update_diagnostics(r)

    def _draw_fwhm_map(self, results):
        """Draw FWHM contour map with star scatter overlay."""
        ax = self._ax_fwhm
        ax.clear()
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
        """Draw PSF elongation vector field with color-coded radial/tangential."""
        ax = self._ax_vec
        ax.clear()
        ax.set_facecolor(_C["bg_dark"])
        ax.set_title(self.t("vector_title"), color=_C["fg_main"], fontsize=10)

        fitted = results["star_fits"]
        h, w = results["image_shape"]
        cx, cy = w / 2, h / 2

        # Draw annular zones
        max_r = math.sqrt(cx**2 + cy**2)
        n_zones = ANALYSIS_DEFAULTS["annular_zones"]
        for i in range(1, n_zones + 1):
            r = max_r * i / n_zones
            circle = matplotlib.patches.Circle((cx, cy), r, fill=False,
                                               edgecolor=_C["border"],
                                               linewidth=0.5,
                                               linestyle="--", alpha=0.5)
            ax.add_patch(circle)

        # Center marker
        ax.plot(cx, cy, "+", color=_C["accent_teal"], markersize=10,
                markeredgewidth=1.5, zorder=10)

        # Draw elongation ellipses/vectors
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

            # Color: green (radial, +1) → white (neutral, 0) → orange (tangential, -1)
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
                # Round star: small circle
                ax.plot(s["x"], s["y"], "o", color=_C["fg_dim"],
                        markersize=2, alpha=0.4)
                continue

            # Elongated star: draw as an ellipse
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

    def _update_diagnostics(self, results):
        """Update the diagnostics text panel with analysis results."""
        self._diag_text.configure(state=tk.NORMAL)
        self._diag_text.delete("1.0", tk.END)

        fitted = results["star_fits"]
        surface = results["surface"]
        cls = results["classification"]
        h, w = results["image_shape"]

        # Image info
        self._diag_text.insert(tk.END, self.t("image_size", w=w, h=h) + "    ", "dim")
        self._diag_text.insert(tk.END, self.t("stars_detected", n=results["stars_detected"]) + "    ", "info")
        self._diag_text.insert(tk.END, self.t("stars_fitted", n=len(fitted)) + "\n", "info")

        # Mean FWHM
        if fitted:
            mean_fwhm = np.mean([s["fwhm_geom"] for s in fitted])
            self._diag_text.insert(tk.END, self.t("mean_fwhm", v=mean_fwhm) + "    ", "accent")

        # Gradient
        if surface is not None:
            self._diag_text.insert(tk.END,
                self.t("fwhm_gradient", v=surface["gradient_pct"]) + "    ", "accent")

        # Mean eccentricity
        if fitted:
            mean_ecc = np.mean([s["eccentricity"] for s in fitted])
            self._diag_text.insert(tk.END, self.t("mean_ecc", v=mean_ecc) + "\n", "info")

        # Radial score and interpretation
        score = cls["score"]
        if score > 0.1:
            interp = self.t("interp_radial")
        elif score < -0.1:
            interp = self.t("interp_tangential")
        else:
            interp = self.t("interp_mixed")
        self._diag_text.insert(tk.END,
            self.t("radial_score", v=score, interp=interp) + "\n", "info")

        # Verdict
        verdict = cls["verdict"]
        if verdict == "correct":
            self._diag_text.insert(tk.END, self.t("verdict_correct") + "\n", "ok")
        elif verdict == "short":
            self._diag_text.insert(tk.END, self.t("verdict_short") + "\n", "warn")
        elif verdict == "long":
            self._diag_text.insert(tk.END, self.t("verdict_long") + "\n", "warn")

        # Note
        self._diag_text.insert(tk.END, self.t("note_single"), "dim")

        self._diag_text.configure(state=tk.DISABLED)
