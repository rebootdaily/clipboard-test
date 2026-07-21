#!/usr/bin/env python3
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import re
import json
import shutil

ROOT = Path(__file__).resolve().parent
WORKBOOK = ROOT / "Clipboard_v4_Master_Base.xlsx"
BUILD = ROOT / "clipboard_generated"
TEMPLATE = ROOT / "app_template"

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def col_num(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def read_workbook(path):
    with zipfile.ZipFile(path) as z:
        sst = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("m:si", NS):
                sst.append(
                    "".join(t.text or "" for t in si.iter("{%s}t" % NS["m"]))
                )

        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        sheets = {}

        for sh in wb.find("m:sheets", NS):
            name = sh.attrib["name"]
            rid = sh.attrib["{%s}id" % NS["r"]]
            target = "xl/" + rmap[rid].lstrip("/")
            xml = ET.fromstring(z.read(target))
            rows = []

            for row in xml.findall(".//m:sheetData/m:row", NS):
                vals = {}
                for c in row.findall("m:c", NS):
                    ref = c.attrib["r"]
                    typ = c.attrib.get("t")
                    v = c.find("m:v", NS)
                    val = ""

                    if v is not None:
                        raw = v.text or ""
                        val = sst[int(raw)] if typ == "s" and raw else raw
                    elif typ == "inlineStr":
                        val = "".join(
                            t.text or "" for t in c.iter("{%s}t" % NS["m"])
                        )

                    vals[col_num(ref)] = val

                if vals:
                    mx = max(vals)
                    rows.append([vals.get(i, "") for i in range(1, mx + 1)])

            sheets[name] = rows

        return sheets


REQUIRED_SHEETS = [
    "APP DESIGN",
    "FOLLOW-UP TEMPLATES",
    "Lists",
    "Settings",
    "Navigation",
]

REQUIRED_COLUMNS = {
    "APP DESIGN": ["Field ID", "Tab", "Input Type"],
    "FOLLOW-UP TEMPLATES": ["Field ID", "Follow-Up Group", "Input Type"],
    "Settings": ["Setting", "Value"],
    "Navigation": ["Order", "Tab"],
}

REQUIRED_DATA_ROWS = ["APP DESIGN", "Navigation"]


def validate_workbook_structure(sheets):
    """Structural checks on the raw workbook, before any config is built.

    Anything appended here is fatal: it means generation stops and no
    file (config.json, clipboard_generated/, or the published root) is
    touched, rather than silently producing a broken application.
    """
    errors = []

    for name in REQUIRED_SHEETS:
        rows = sheets.get(name)

        if rows is None:
            errors.append(f"Missing required worksheet: '{name}'")
            continue

        if not rows:
            errors.append(f"Worksheet '{name}' has no header row")
            continue

        headers = {str(x).strip() for x in rows[0]}
        missing = [c for c in REQUIRED_COLUMNS.get(name, []) if c not in headers]
        if missing:
            errors.append(
                f"Worksheet '{name}' is missing required column(s): "
                + ", ".join(missing)
            )

        if name in REQUIRED_DATA_ROWS and len(rows) < 2:
            errors.append(
                f"Worksheet '{name}' has a header row but no data rows"
            )

    return errors


def records(rows):
    if not rows:
        return []

    headers = [str(x).strip() for x in rows[0]]
    out = []

    for r in rows[1:]:
        if not any(str(x).strip() for x in r):
            continue

        d = {}
        for i, h in enumerate(headers):
            if not h:
                continue

            v = r[i] if i < len(r) else ""

            if h == "Display Order" and str(v).strip():
                try:
                    v = int(float(v))
                except Exception:
                    pass
            elif h == "Default Value" and str(v).strip():
                sv = str(v).strip()
                if re.fullmatch(r"-?\d+(?:\.0+)?", sv):
                    v = int(float(sv))

            if v != "":
                d[h] = v

        out.append(d)

    return out


def build_config(s):
    app = records(s.get("APP DESIGN", []))
    followups = records(s.get("FOLLOW-UP TEMPLATES", []))

    lists = {}
    rows = s.get("Lists", [])
    if rows:
        heads = rows[0]
        for i, h in enumerate(heads):
            h = str(h).strip()
            if h:
                lists[h] = [
                    r[i]
                    for r in rows[1:]
                    if i < len(r) and str(r[i]).strip()
                ]

    settings = {}
    for r in s.get("Settings", [])[1:]:
        if len(r) >= 2 and str(r[0]).strip():
            settings[str(r[0]).strip()] = r[1]

    settings['Version'] = '7.0'
    settings['Workbook Role'] = 'Live master configuration for Clipboard v7.0'

    nav = []
    for r in s.get("Navigation", [])[1:]:
        if len(r) >= 2 and str(r[1]).strip():
            nav.append(
                (
                    float(r[0]) if str(r[0]).strip() else 999,
                    r[1],
                )
            )
    nav = [x[1] for x in sorted(nav)]

    return {
        "app": app,
        "followups": followups,
        "lists": lists,
        "settings": settings,
        "navigation": nav,
    }


def validate(cfg):
    issues = []

    ids = [x.get("Field ID") for x in cfg["app"] if x.get("Field ID")]
    if len(ids) != len(set(ids)):
        issues.append("Duplicate APP DESIGN Field IDs")

    fids = [
        x.get("Field ID")
        for x in cfg["followups"]
        if x.get("Field ID")
    ]
    if len(fids) != len(set(fids)):
        issues.append("Duplicate follow-up Field IDs")

    for f in cfg["app"] + cfg["followups"]:
        opt = f.get("Options")
        if opt and opt not in cfg["lists"]:
            issues.append(
                f"Missing list {opt} for {f.get('Field ID', '?')}"
            )

    return sorted(set(issues))


def copy_template_to_build():
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template folder not found: {TEMPLATE}")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    copied = []
    for source in TEMPLATE.iterdir():
        destination = BUILD / source.name

        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

        copied.append(source.name)

    if not (BUILD / "index.html").exists():
        raise FileNotFoundError(
            f"Template index.html not found in: {TEMPLATE}"
        )

    return copied


def publish_build_to_root():
    published = []

    # Remove obsolete versioned application files from the published root.
    for stale in ROOT.glob("app-v*.js"):
        stale.unlink()

    for source in BUILD.iterdir():
        destination = ROOT / source.name

        if source.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

        published.append(source.name)

    return published


def print_banner():
    print("-" * 50)
    print("Clipboard Generator")
    print()
    print("Workbook Source:")
    print(WORKBOOK.name)
    print()
    print("Application Source:")
    print(f"{TEMPLATE.name}/")
    print()
    print("Generated Output:")
    print("root/")
    print(f"{BUILD.name}/")
    print()
    print("WARNING")
    print()
    print("Generated files are build artifacts.")
    print()
    print("Do not edit generated files.")
    print()
    print("Always edit app_template for application code.")
    print("-" * 50)


def main():
    print_banner()

    try:
        if not WORKBOOK.exists():
            raise FileNotFoundError(f"Workbook not found: {WORKBOOK}")

        sheets = read_workbook(WORKBOOK)

        structure_errors = validate_workbook_structure(sheets)
        if structure_errors:
            message = "\n".join(
                [
                    "Workbook structure validation FAILED.",
                    "Generation stopped before any file was written or overwritten.",
                    "",
                ]
                + [f"- {e}" for e in structure_errors]
                + [
                    "",
                    "Fix the worksheet(s)/column(s) above in "
                    f"{WORKBOOK.name} and re-run generate.py.",
                ]
            )
            print(message)
            (ROOT / "VALIDATION.txt").write_text(message + "\n", encoding="utf-8")
            return 1

        cfg = build_config(sheets)
        issues = validate(cfg)

        copied = copy_template_to_build()

        (BUILD / "config.json").write_text(
            json.dumps(cfg, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        published = publish_build_to_root()

        report = [
            "Clipboard v4 workbook validation",
            f"Workbook: {WORKBOOK.name}",
            f"APP DESIGN fields: {len(cfg['app'])}",
            f"Follow-up questions: {len(cfg['followups'])}",
            f"Lists: {len(cfg['lists'])}",
            f"Navigation tabs: {len(cfg['navigation'])}",
            f"Issues: {len(issues)}",
        ] + [f"- {x}" for x in issues]

        (ROOT / "VALIDATION.txt").write_text(
            "\n".join(report) + "\n",
            encoding="utf-8",
        )

        print("\n".join(report))
        print(f"Template files copied: {', '.join(copied)}")
        print(f"Generated: {BUILD}")
        print("Published to repository root:")
        for name in published:
            print(f"- {name}")
        print("GitHub Pages URL:")
        print("https://rebootdaily.github.io/clipboard-test/")

        return 1 if issues else 0

    except Exception as exc:
        message = f"ERROR: {exc}"
        print(message)
        (ROOT / "VALIDATION.txt").write_text(
            message + "\n",
            encoding="utf-8",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
