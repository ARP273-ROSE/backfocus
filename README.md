# Backfocus Calculator v2.0

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

**Backfocus Calculator** is a bilingual (English/French) cross-platform desktop application for calculating and managing backfocus configurations in astrophotography optical trains. Built with **PyQt6** and a dark space theme.

> **12,100+ real products** &bull; **125 brands** &bull; **22 part types** &bull; **29 connection types** &bull; **Dark space theme**

---

## Features

### Optical Train Builder
- Build optical trains with **telescope on the left** and **camera on the right** (light path convention)
- Each piece has **telescope-side** and **camera-side** connections with thread diameter + male/female gender
- **Flip** reversible pieces to swap their telescope/camera connections
- Define the **backfocus zone** by marking BF start and BF end pieces
- Real-time calculation of total optical length and gap to target
- Color-coded gap: **green** (OK < 0.1 mm), **orange** (short), **red** (long)
- **Connection compatibility check**: verifies diameter match and male/female gender pairing between adjacent parts
- **Conflict detection**: warns when a part exceeds your owned quantity across configurations
- Visual color-coded **diagram** with highlighted backfocus zone and target line
- **Drag & drop** reordering in the diagram

### Parts Catalog
- Full CRUD: add, edit, duplicate, delete parts in a **large separate window**
- **12,100+ product reference database** with 125 brands for auto-fill
- Each part stores: brand, name, type, optical length, mass, telescope-side connection, camera-side connection, reversible flag, BF role, quantity, notes
- **Auto-fill**: type a brand or name and auto-fill all fields from the built-in database
- **Advanced filters**: search by text, type, thread diameter, gender, owned-only
- **Column sorting**: click any header to sort (click again to reverse)
- **+/- quantity buttons**: quickly adjust owned quantity
- **Color coding**: owned parts in gold, non-owned parts dimmed

### 22 Part Types
Telescope, Refractor, Camera Lens, Astro Camera, DSLR/Mirrorless, Eyepiece, Barlow, Focal Reducer, Field Flattener, Focal Extender, Coma Corrector, Filter Wheel, Filter Holder, OAG, Rotator, Focuser, Diagonal, Adapter Ring, Spacer, Anti-tilt, Guide Scope, Flip Mirror

### 29 Connection Types
- **Metric threads**: M42/T2, M48, M54, M56, M63, M68, M72, M81, M82, M84, M92, M117
- **Camera mounts**: EOS, Canon RF, Nikon F, Nikon Z, Sony E, Fuji X, MFT, Pentax K
- **Barrels**: 1.25", 2", CS
- **Bayonet**: SC (Schmidt-Cassegrain)
- **Bolt mounts**: ZWO 6-bolt, ZWO 4-bolt, QHY 4-bolt

### Auto-complete
- **Suggest**: find a single owned part that fills the backfocus gap
- **Auto-complete**: find combinations of 1, 2, or 3 owned parts that complete the chain
- Option to **allow or disallow parts** already used in other configurations
- Results sorted by proximity to target, with **perfect matches highlighted in green**

### Save & Export
- **Auto-save on close** with confirmation dialog
- **Save All**: manual save at any time (File menu)
- **Export/Import Configuration**: save or load a single configuration as JSON
- **Export/Import All Data**: save or load everything (parts + configs + settings) in one JSON file
- Ideal for backups, transfers between computers, or sharing setups

### Bilingual
- Switch between **English** and **French** instantly via the Language menu
- All labels, messages, help text, and dialogs are fully translated
- Language preference is saved automatically

### FITS / XISF Backfocus Analyzer

> **Experimental** — For precise measurement, use [HocusFocus](https://github.com/jbautista75/HocusFocus) with [N.I.N.A.](https://nighttime-imaging.eu/)

- Load **FITS** (.fits, .fit, .fts), **compressed FITS** (.fits.fz), or **XISF** (PixInsight) images
- Automatically **detect stars** and fit elliptical 2D Gaussians on each one
- Build a **FWHM map** (polynomial surface) showing focus quality across the field
- Display a **vector field** of star elongation directions (radial vs tangential)
- **Mosaic 3x3** view: visual inspection of star quality in 9 regions (corners, edges, center) with color-coded FWHM borders
- **Diagnose backfocus errors**: radial elongation = too short, tangential = too long
- RGB images auto-converted to luminance, large images auto-binned 2x2
- Threaded analysis with progress bar

### Bug Reports & Crash Capture
- **Automatic crash capture**: all unhandled exceptions are logged locally with full traceback
- **Crash detection on restart**: detects previous crash and offers to open a pre-filled GitHub Issue
- **Manual bug report** (Help menu): opens browser with system info and recent errors pre-filled
- **Anonymous reports**: all file paths are sanitized (user home directory replaced with `~`) — no personal information is ever exposed
- **Local error log**: persistent log with automatic rotation (100 KB max)
- **Zero data sent automatically**: you always review and submit the report yourself

### Automatic Updates
- **Silent check on startup** (background thread, 2-second delay)
- **Manual check** via Help > Check for Updates
- Compares local version against GitHub Releases
- Update dialog shows current/new version + changelog
- **Secure download**: size limit, zip validation, anti path-traversal, anti symlink
- Whitelist of files to replace (never touches user data, venv, .git)
- Automatic restart after update

### Desktop Shortcut
- **Create a desktop shortcut** via Help > Create Desktop Shortcut
- Works on Windows, Linux, and macOS
- Shortcut targets `launch.bat` / `launch.sh` (portable across PCs)
- Icon copied locally to avoid network path issues

### Performance & Fluidity (v2.0)
- **Native PyQt6 interface** with built-in dark theme (migrated from tkinter)
- **Async save**: file I/O offloaded to a dedicated daemon thread — eliminates UI micro-freezes
- **Galaxy cursor optimized**: 30 fps polling with early-out when position unchanged
- **Fast qty +/-**: single-row update instead of full catalog rebuild on each click
- **Batch tree insert**: columns hidden during insertion, single repaint instead of one per item
- **Parts search cache**: pre-built index for 12,000+ parts, invalidated on data change
- **Unified debounce**: single 300 ms save timer for all operations

### Dark Space Theme
- Dark space/cosmos theme with color accents
- Color-coded part types in the diagram
- Gold for owned parts, gray for non-owned

---

## Requirements

- **Python 3.8+**
- **PyQt6** (installed automatically by the launcher scripts)
- **FITS Analyzer** (optional): numpy, scipy, astropy, photutils, matplotlib

### Linux
```bash
# Debian/Ubuntu
sudo apt-get install python3 python3-venv python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python
```

---

## Installation & Launch

### Quick Start (Recommended)

**Windows:**
```
Double-click launch.bat
```

**Linux/macOS:**
```bash
chmod +x launch.sh
./launch.sh
```

The launcher script will:
1. Detect Python (or guide you to install it)
2. Create a **local virtual environment** (not in the project folder — safe for NAS/synced setups)
3. Install all dependencies from requirements.txt
4. Launch the application

> **Multi-PC / NAS support**: The venv is stored locally on each PC (`%LOCALAPPDATA%\BackfocusCalculator\venv` on Windows, `~/.local/share/BackfocusCalculator/venv` on Linux/macOS). The project folder can live on a NAS or synced drive without conflicts.

### Windows Standalone (.exe) — No Python Required

A pre-built Windows executable is available on the [Releases](https://github.com/ARP273-ROSE/backfocus/releases) page:

1. Download the latest `BackfocusCalculator-vX.X.X.zip` from Releases
2. Extract the archive
3. Run `BackfocusCalculator.exe` — no Python installation needed

To build the executable yourself:
```bash
pip install pyinstaller
pyinstaller backfocus.spec
```
The output is in `dist/BackfocusCalculator/`. All features work identically (auto-save, export/import, FITS analyzer, auto-update check, etc.).

> **Note**: The standalone exe is Windows-only. On Linux/macOS, use the launcher scripts above.

### Manual Launch
```bash
pip install PyQt6
python backfocus.py
```

---

## Usage

### 1. First Launch
On first launch, the 12,100+ product reference database is automatically loaded into your parts catalog with an owned quantity of 0. You can then mark the parts you own by adjusting their quantity with the +/- buttons.

### 2. Parts Catalog
Open via **View > Parts Catalog** or the toolbar button.

- **Add** a part: fill in brand, name, type, optical length, connections, etc.
- **Auto-fill**: type a brand/name and click Auto-fill to populate from the 12,100+ database
- **+/- buttons**: quickly adjust owned quantity
- **Filters**: combine text search, type, diameter, gender, and owned-only
- **Sort**: click column headers (click again to reverse)
- **Double-click**: edit a part

### 3. Configurations
1. Click **+** to create a new configuration with a target backfocus (e.g., 55 mm)
2. Click **Add part** to add parts from your catalog to the optical train
3. Use **Up/Down** to reorder, **Flip** to reverse reversible parts, **Remove** to delete
4. Mark **BF Start** and **BF End** to define the backfocus measurement zone
5. The app automatically:
   - Calculates the backfocus within the BF zone
   - Shows the gap color-coded (green/orange/red)
   - Checks connection compatibility (MISMATCH warnings)
   - Warns on quantity conflicts
   - Draws a visual diagram
6. Use **Suggest** to find a single part that fills the gap
7. Use **Auto-complete** to find combinations of 1-3 owned parts

### 4. Save & Export
- **File > Save All**: save everything manually
- **File > Export Configuration**: save active config as JSON
- **File > Import Configuration**: load a config from JSON
- **File > Export All Data**: save everything (parts + configs + settings) in one file
- **File > Import All Data**: replace all data from an exported file
- **Auto-save on close**: data is saved automatically when you quit

### 5. Settings
- **Settings > Measurement Units**: toggle mm/inches and grams/ounces
- **Language**: switch between English and Francais instantly

---

## Backfocus Concept

**Backfocus** is measured from the camera-side of the flattener/reducer/corrector to the camera sensor. The application lets you mark exactly which pieces define the start and end of this zone.

**Common backfocus values:**

| Corrector / Reducer | Required BF |
|---------------------|-------------|
| Sky-Watcher 0.85x Reducer | 55 mm |
| Baader MPCC Mark III | 55 mm |
| Celestron f/6.3 Reducer | 99 mm |
| Starizona HyperStar | 12-24 mm |
| Takahashi TOA-35 Reducer | 72.2 mm |
| Riccardi 0.75x M82 Reducer | 56 mm |
| ASA 3" Corrector | 67 mm |

Some telescope designs (e.g., Petzval refractors) do not require separate backfocus correction. The application supports these by simply not defining a BF zone.

---

## Project Structure

```
backfocus/
├── backfocus.py           # Main application (PyQt6, ~3400 lines)
├── reference_data.py      # Reference database (12,100+ entries)
├── gen_refdb.py           # Database generator script
├── fits_analyzer.py       # FITS/XISF backfocus analyzer (optional)
├── test_audit.py          # Automated test suite
├── shortcut_helper.py     # Desktop shortcut creation helper
├── launch.bat             # Windows launcher (auto-setup, local venv)
├── launch.sh              # Linux/macOS launcher (auto-setup, local venv)
├── requirements.txt       # Python dependencies (PyQt6 + FITS analyzer)
├── backfocus.spec         # PyInstaller build spec (Windows .exe)
├── backfocus.ico          # Application icon (Windows)
├── backfocus.png          # Application icon (cross-platform)
├── README.md              # This file
└── manual/
    └── manual.pdf         # Bilingual user manual
```

---

## License

This project is provided as-is for personal astrophotography use.

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests.

---

<sub>If you find this useful, you can [buy me a coffee](https://buymeacoffee.com/orlytourbou) :)</sub>
