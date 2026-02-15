#!/usr/bin/env python3
"""Comprehensive automated audit tests for backfocus application."""
import json, os, sys, copy, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reference_data import REFERENCE_DB

# ---------------------------------------------------------------------------
# Constants (duplicated from backfocus.py for headless testing)
# ---------------------------------------------------------------------------
THREADS = [
    "", "M42", "T2 (M42x0.75)", "M48", "M52", "M54", "M56", "M63", "M68", "M72",
    "M81", "M82", "M84", "M92", "M117",
    "SC (Schmidt-Cassegrain)", "EOS", "Canon RF", "Nikon F", "Nikon Z",
    "Sony E", "Fuji X", "MFT", "Pentax K", "CS", '1.25"', '2"',
    "ZWO 6-bolt", "ZWO 4-bolt", "QHY 4-bolt",
]
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
BF_ROLE_END_TYPES = {"type_camera", "type_dslr", "type_eyepiece"}

# ---------------------------------------------------------------------------
# Helper functions (duplicated from backfocus.py for headless testing)
# ---------------------------------------------------------------------------
def _extract_diam(conn):
    if not conn:
        return ""
    for d in ("M117","M92","M84","M82","M81","M72","M68","M63","M56","M54","M48","M42"):
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

def _default_data():
    return {"language": "fr", "length_unit": "mm", "mass_unit": "g",
            "parts": [], "configurations": []}

# ---------------------------------------------------------------------------
# Read TR dict from source
# ---------------------------------------------------------------------------
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backfocus.py"),
           encoding="utf-8").read()
# Extract TR dict
tr_start = src.index("TR = {")
tr_end = src.index("\n}", tr_start) + 2
TR = {}
exec(src[tr_start:tr_end])

# ===========================================================================
# TESTS
# ===========================================================================
passed = 0
failed = 0
warnings = []

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} -- {detail}")

def warn(msg):
    warnings.append(msg)
    print(f"  WARN: {msg}")

# === 1. Default data ===
print("=== 1. Default data structure ===")
d = _default_data()
test("has language", "language" in d)
test("has parts list", isinstance(d.get("parts"), list))
test("has configurations list", isinstance(d.get("configurations"), list))
test("default language is fr", d["language"] == "fr")
test("default length_unit is mm", d.get("length_unit") == "mm")
test("default mass_unit is g", d.get("mass_unit") == "g")

# === 2. Connection compatibility ===
print("=== 2. Connection compatibility ===")
test("M42 M/F compatible", _conn_compat("M42","Male","M42","Female") == True)
test("M42 M/M incompatible", _conn_compat("M42","Male","M42","Male") == False)
test("M42 F/F incompatible", _conn_compat("M42","Female","M42","Female") == False)
test("M42/M48 incompatible", _conn_compat("M42","Male","M48","Female") == False)
test("empty thread wildcard A", _conn_compat("","","M42","Female") == True)
test("empty thread wildcard B", _conn_compat("M42","Male","","") == True)
test("both empty compatible", _conn_compat("","","","") == True)
test("no gender = compatible", _conn_compat("M42","","M42","") == True)
test("one gender only", _conn_compat("M42","Female","M42","") == True)
# T2 vs M42 edge case - T2 contains "M42" so _extract_diam returns M42
test("T2 vs M42 compat", _conn_compat("T2 (M42x0.75)","Male","M42","Female") == True,
     "T2 extracts to M42, should match M42")

# === 3. Extract diameter ===
print("=== 3. Extract diameter ===")
test("M42", _extract_diam("M42") == "M42")
test("M48", _extract_diam("M48") == "M48")
test("M54", _extract_diam("M54") == "M54")
test("M68", _extract_diam("M68") == "M68")
test("SC", _extract_diam("SC (Schmidt-Cassegrain)") == "SC")
test("T2 -> M42", _extract_diam("T2 (M42x0.75)") == "M42")
test("EOS", _extract_diam("EOS") == "EOS")
test("Canon RF", _extract_diam("Canon RF") == "Canon RF")
test("ZWO 6-bolt", _extract_diam("ZWO 6-bolt") == "ZWO 6-bolt")
test("QHY 4-bolt", _extract_diam("QHY 4-bolt") == "QHY 4-bolt")
test("empty", _extract_diam("") == "")
# Edge case: '1.25"' and '2"' are not in the diameter extraction list
res_125 = _extract_diam('1.25"')
test('1.25" passthrough', res_125 == '1.25"', f'got: {res_125}')

# === 4. Flip/effective ===
print("=== 4. Flip effective ===")
item = {"tside_thread":"M42","tside_gender":"Female","cside_thread":"M48","cside_gender":"Male"}
eff = _effective(item)
test("non-flipped keeps sides", eff["tside_thread"] == "M42")
item_f = dict(item, flipped=True)
eff_f = _effective(item_f)
test("flipped swaps tside", eff_f["tside_thread"] == "M48")
test("flipped swaps cside", eff_f["cside_thread"] == "M42")
test("flipped swaps tgender", eff_f["tside_gender"] == "Male")
test("flipped swaps cgender", eff_f["cside_gender"] == "Female")

# === 5. Format functions ===
print("=== 5. Format functions ===")
test("fmt_len mm", _fmt_len(55, "mm") == "55.00 mm")
test("fmt_len zero", _fmt_len(0, "mm") == "0.00 mm")
test("fmt_len inches", "2.1654" in _fmt_len(55, "in"))
test("fmt_mass g", _fmt_mass(500, "g") == "500 g")
test("fmt_mass zero", _fmt_mass(0, "g") == "0 g")
test("fmt_mass oz", "17.64" in _fmt_mass(500, "oz"))

# === 6. Translation coverage ===
print("=== 6. Translation coverage ===")
tr_ok = True
for key, val in TR.items():
    if "en" not in val:
        warn(f"key {key} missing EN"); tr_ok = False
    if "fr" not in val:
        warn(f"key {key} missing FR"); tr_ok = False
    if val.get("en","") == "":
        warn(f"key {key} empty EN"); tr_ok = False
    if val.get("fr","") == "":
        warn(f"key {key} empty FR"); tr_ok = False
test(f"all {len(TR)} TR keys bilingual", tr_ok)

# Check PART_TYPES all translated
pt_ok = True
for pt in PART_TYPES:
    if pt not in TR:
        warn(f"PART_TYPE {pt} missing translation"); pt_ok = False
test("all PART_TYPES translated", pt_ok)

# === 7. Reference DB integrity ===
print("=== 7. Reference DB integrity ===")
test(f"DB has {len(REFERENCE_DB)} entries", len(REFERENCE_DB) >= 11900)

valid_types = set(PART_TYPES)
valid_bf = {"", "start", "end"}
valid_genders = {"", "Female", "Male"}
valid_threads_set = set(THREADS)

type_errors = 0
bf_errors = 0
gender_errors = 0
thread_warnings = set()
neg_ol = 0
neg_mass = 0
zero_mass_cameras = 0

for i, e in enumerate(REFERENCE_DB):
    if e.get("type") not in valid_types:
        type_errors += 1
    if e.get("bf_role", "") not in valid_bf:
        bf_errors += 1
    for g in ("tside_gender", "cside_gender"):
        if e.get(g, "") not in valid_genders:
            gender_errors += 1
    for t in ("tside_thread", "cside_thread"):
        tv = e.get(t, "")
        if tv and tv not in valid_threads_set:
            thread_warnings.add(tv)
    if e.get("optical_length", 0) < 0:
        neg_ol += 1
    if e.get("mass", 0) < 0:
        neg_mass += 1
    if e.get("type") in ("type_camera","type_dslr") and e.get("mass",0) == 0:
        zero_mass_cameras += 1

test("no invalid types", type_errors == 0, f"{type_errors} invalid types")
test("no invalid bf_roles", bf_errors == 0, f"{bf_errors} invalid bf_roles")
test("no invalid genders", gender_errors == 0, f"{gender_errors} invalid genders")
test("no negative optical_length", neg_ol == 0, f"{neg_ol} negative")
test("no negative mass", neg_mass == 0, f"{neg_mass} negative")

if thread_warnings:
    warn(f"{len(thread_warnings)} unknown thread values in DB: {sorted(thread_warnings)[:10]}")
if zero_mass_cameras:
    warn(f"{zero_mass_cameras} cameras/DSLRs with mass=0")

# === 8. Duplicates check ===
print("=== 8. Duplicates check ===")
seen = set()
dups = 0
for e in REFERENCE_DB:
    key = (e.get("brand",""), e.get("name",""))
    if key in seen:
        dups += 1
    seen.add(key)
test("no duplicates", dups == 0, f"{dups} duplicates found")

# === 9. BF role consistency ===
print("=== 9. BF role consistency ===")
wrong_start = 0
wrong_end = 0
for e in REFERENCE_DB:
    tp = e.get("type", "")
    bf = e.get("bf_role", "")
    # Cameras should have bf_role = end
    if tp in BF_ROLE_END_TYPES and bf != "end":
        wrong_end += 1
    # Reducers etc should have bf_role = start
    if tp in BF_ROLE_START_TYPES and bf != "start" and bf != "":
        wrong_start += 1

# Count cameras without end role
cam_no_end = sum(1 for e in REFERENCE_DB if e.get("type") in ("type_camera","type_dslr") and e.get("bf_role","") != "end")
if cam_no_end:
    warn(f"{cam_no_end} cameras/DSLRs without bf_role='end'")

# === 10. Backfocus calculation simulation ===
print("=== 10. Backfocus calculation ===")
stack = [
    {"name":"Reducer","optical_length":5,"type":"type_reducer","bf_role":"start"},
    {"name":"Spacer1","optical_length":20,"type":"type_spacer"},
    {"name":"FilterWheel","optical_length":20,"type":"type_filter_wheel"},
    {"name":"Camera","optical_length":6.5,"type":"type_camera","bf_role":"end"},
]
total = sum(it.get("optical_length",0) for it in stack)
test("total = 51.5", total == 51.5, f"got {total}")
# BF calculation excludes the start piece (range starts at bs+1)
bs, be = 0, 3
bf_total = sum(stack[j].get("optical_length",0) for j in range(bs+1, be+1))
test("bf_total excludes start = 46.5", bf_total == 46.5, f"got {bf_total}")
target = 55
diff = bf_total - target
test("diff = -8.5 (short)", diff == -8.5, f"got {diff}")
bs2, be2 = 1, 3
bf_sub = sum(stack[j].get("optical_length",0) for j in range(bs2+1, be2+1))
test("bf_sub subset = 26.5", bf_sub == 26.5, f"got {bf_sub}")

# === 11. Save/Load simulation ===
print("=== 11. Save/Load simulation ===")
tmpdir = tempfile.mkdtemp()
tmpfile = os.path.join(tmpdir, "test_data.json")
try:
    test_data = _default_data()
    test_data["parts"] = [{"brand":"ZWO","name":"ASI 294MC Pro","type":"type_camera",
                           "optical_length":6.5,"mass":478,"qty":1}]
    test_data["configurations"] = [{"name":"Test Config","target_backfocus":55,
                                    "notes":"test","stack":[],"bf_start_idx":-1,"bf_end_idx":-1}]
    with open(tmpfile, "w", encoding="utf-8") as fh:
        json.dump(test_data, fh, indent=2, ensure_ascii=False)
    with open(tmpfile, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    test("save/load roundtrip", loaded == test_data)
    test("parts preserved", len(loaded["parts"]) == 1)
    test("config preserved", len(loaded["configurations"]) == 1)
    test("utf-8 roundtrip", loaded["parts"][0]["brand"] == "ZWO")

    # Test export-all format
    export_data = copy.deepcopy(test_data)
    export_data["language"] = "en"
    export_data["length_unit"] = "in"
    export_file = os.path.join(tmpdir, "export_all.json")
    with open(export_file, "w", encoding="utf-8") as fh:
        json.dump(export_data, fh, indent=2, ensure_ascii=False)
    with open(export_file, "r", encoding="utf-8") as fh:
        reimported = json.load(fh)
    for k, v in _default_data().items():
        reimported.setdefault(k, v)
    test("export-all reimport", reimported["language"] == "en")
    test("export-all units", reimported["length_unit"] == "in")
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

# === 12. NOT_REVERSIBLE validation ===
print("=== 12. NOT_REVERSIBLE validation ===")
nr_ok = all(nr in PART_TYPES for nr in NOT_REVERSIBLE)
test("NOT_REVERSIBLE subset of PART_TYPES", nr_ok)
# Check that adapters/spacers are NOT in NOT_REVERSIBLE (they should be reversible)
test("adapters reversible", "type_adapter" not in NOT_REVERSIBLE)
test("spacers reversible", "type_spacer" not in NOT_REVERSIBLE)
test("barlows reversible", "type_barlow" not in NOT_REVERSIBLE)

# === 13. T2/M42 interaction edge case ===
print("=== 13. Edge cases ===")
# T2 (M42x0.75) extracts to M42 - this means T2 and M42 parts show as compatible
# This is technically correct since T2 IS M42x0.75 threading
test("T2 extracts to M42", _extract_diam("T2 (M42x0.75)") == "M42")
# But it might confuse users - just flag it
warn("T2 (M42x0.75) extracts as M42 - physically correct but may confuse (T2=M42x0.75)")

# Test auto-fill would match correctly
matches = [x for x in REFERENCE_DB if "asi 294mc pro" in (x["brand"]+" "+x["name"]).lower()]
test("auto-fill finds ASI 294MC Pro", len(matches) >= 1, f"found {len(matches)}")

# === 14. Large dataset performance ===
print("=== 14. Performance check ===")
import time
t0 = time.time()
parts_copy = [dict(p, qty=0) for p in REFERENCE_DB]
t1 = time.time()
test(f"copy 12K parts in {t1-t0:.3f}s", t1-t0 < 2.0, f"took {t1-t0:.3f}s")

t0 = time.time()
for p in parts_copy:
    _ = p.get("brand","").lower()
    _ = p.get("name","").lower()
t1 = time.time()
test(f"search 12K parts in {t1-t0:.3f}s", t1-t0 < 1.0, f"took {t1-t0:.3f}s")

# === 15. Help text check ===
print("=== 15. Help text check ===")
# The help text references "3,000+" but DB is now 12,000+
help_section = src[src.index("def open_help"):src.index("class CatalogWindow")]
if "3,000+" in help_section or "3 000" in help_section:
    warn("Help text still references '3,000+' products but DB has 12,000+")
if "12,000" in help_section or "12 000" in help_section:
    test("help text updated to 12K", True)
else:
    test("help text updated to 12K", False, "still references old count")

# === 16. Menu structure validation ===
print("=== 16. Menu/UI keys validation ===")
required_menu_keys = [
    "file", "view", "settings", "help_menu", "language",
    "save_all", "export_config", "import_config", "export_all", "import_all", "quit",
    "open_catalog", "units", "length_mm", "length_in", "mass_g", "mass_oz",
    "user_guide", "about", "report_bug",
    "fits_analyzer", "fits_btn", "fits_analyzer_missing_deps",
]
missing_keys = [k for k in required_menu_keys if k not in TR]
test("all menu TR keys exist", len(missing_keys) == 0, f"missing: {missing_keys}")

# === 17. Initial data population ===
print("=== 17. Initial data population ===")
# When parts is empty, App.__init__ copies REFERENCE_DB
# Verify each ref entry has the expected keys
required_keys = {"brand", "name", "type", "optical_length", "mass",
                 "tside_thread", "tside_gender", "cside_thread", "cside_gender",
                 "reversible", "bf_role"}
missing_entries = 0
for i, e in enumerate(REFERENCE_DB):
    for k in required_keys:
        if k not in e:
            missing_entries += 1
            if missing_entries <= 5:
                warn(f"entry {i} missing key '{k}': {e.get('name','?')}")
test("all ref entries have required keys", missing_entries == 0, f"{missing_entries} missing")

# ===========================================================================
# SUMMARY
# ===========================================================================
print()
print("=" * 60)
print(f"AUDIT RESULTS: {passed} passed, {failed} failed, {len(warnings)} warnings")
print("=" * 60)
if warnings:
    print("\nWARNINGS:")
    for w in warnings:
        print(f"  - {w}")
if failed:
    print(f"\n{failed} TEST(S) FAILED!")
    sys.exit(1)
else:
    print("\nALL TESTS PASSED!")
    sys.exit(0)
