#!/usr/bin/env python3
"""Build the EM vocabulary PACKAGES of this repository (release assets).

MICRO-U-VOCABOLARI-COME-FONT (E.D., 18 Nov 2026). A package is the source of a
vocabulary, UNMODIFIED, with a manifest (``em-vocabulary-package/1``, read by
``s3dgraphy.authorities.packages``): id, version, snapshot date, languages,
licence, tier, the attribution to show, the sha256 of the source. The INDEX is
never in a package: every machine compiles its own when it installs.

Only tiers A and B are built — a tier C vocabulary may not be handed on, so its
package is the manifest alone (a stub the tools complete with «Scarica in
locale»). Each ``packages/<id>/package.yaml`` says where its source comes from:

* ``from: iccd_standards`` — a file of the ICCD's Standard-catalografici
  checkout (``--iccd`` or ``$STRATIGRAPH_ICCD_STANDARDS``), copied byte for byte;
* ``from: export`` — a dated export made by a tool of this repository
  (``--export <id>=<file>``, ``--date``), e.g. tools/getty_aat_export.py;
* ``from: repo`` — a file of this repository (the modules in ``skos/``).

Writes ``<out>/<id>-<version>.emvocab.zip`` and ``<out>/catalog.json``::

    python3 tools/build_packages.py dist --iccd ~/…/Standard-catalografici \\
        --export getty-aat-materials=/tmp/aat-materials.nt --date 2026-11-18
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
FORMAT = "em-vocabulary-package/1"
SUFFIX = ".emvocab.zip"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)   # zip entries dated alike: same input, same bytes


def _source_bytes(card: dict, args) -> bytes:
    src = card["source"]
    kind = src.get("from")
    if kind == "iccd_standards":
        root = args.iccd or os.environ.get("STRATIGRAPH_ICCD_STANDARDS")
        if not root:
            raise SystemExit(f"{card['id']}: --iccd or $STRATIGRAPH_ICCD_STANDARDS is needed")
        return (Path(root).expanduser() / src["path"]).read_bytes()
    if kind == "export":
        given = dict(e.split("=", 1) for e in (args.export or []))
        if card["id"] not in given:
            raise SystemExit(f"{card['id']}: --export {card['id']}=<file> is needed")
        return Path(given[card["id"]]).expanduser().read_bytes()
    if kind == "repo":
        return (REPO / src["path"]).read_bytes()
    raise SystemExit(f"{card['id']}: unknown source kind {kind!r}")


def manifest_of(card: dict, data: bytes, args) -> dict:
    m = {k: v for k, v in card.items() if k != "source"}
    src = card["source"]
    m["format"] = FORMAT
    if src.get("from") == "export":
        if not args.date:
            raise SystemExit(f"{card['id']}: --date (the day of the export) is needed")
        m.setdefault("version", args.date)
        m.setdefault("snapshot_date", args.date)
    m["source"] = {k: src[k] for k in ("file", "format", "retrieved_from", "tool") if src.get(k)}
    m["source"]["sha256"] = hashlib.sha256(data).hexdigest()
    m["source"]["bytes"] = len(data)
    if not m.get("languages"):
        m["languages"] = _languages(data, src.get("format"))
    return m


def _languages(data: bytes, fmt: str) -> list:
    import re
    if fmt == "nt":
        langs = set(re.findall(rb'"@([A-Za-z0-9-]+) \.', data))
    else:
        langs = set(re.findall(rb'xml:lang="([A-Za-z0-9-]+)"', data))
    return sorted(l.decode().lower() for l in langs)


def _zip(manifest: dict, data: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, blob in (("manifest.json",
                            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode()),
                           (manifest["source"]["file"], data)):
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, blob)
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--iccd")
    ap.add_argument("--export", action="append")
    ap.add_argument("--date")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    catalog = []
    for f in sorted((REPO / "packages").glob("*/package.yaml")):
        card = yaml.safe_load(f.read_text(encoding="utf-8"))
        if args.ids and card["id"] not in args.ids:
            continue
        if card.get("tier") == "C":
            continue  # never built: its source may not be handed on
        data = _source_bytes(card, args)
        m = manifest_of(card, data, args)
        blob = _zip(m, data)
        name = f"{m['id']}-{m['version']}{SUFFIX}"
        (out / name).write_bytes(blob)
        catalog.append({k: m.get(k) for k in ("id", "version", "snapshot_date", "title", "languages",
                                              "license", "tier", "attribution", "serves")}
                       | {"url": name, "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)})
        print(f"{name}: {len(data)} bytes of source, {len(m['languages'])} languages", file=sys.stderr)
    (out / "catalog.json").write_text(json.dumps({"format": "em-vocabulary-catalog/1",
                                                  "packages": catalog}, ensure_ascii=False,
                                                 indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
