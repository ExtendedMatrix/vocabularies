#!/usr/bin/env python3
"""PROPOSE alignments between two installed vocabulary packages, by label.

MICRO-U-VOCABOLARI-COME-FONT (E.D., 18 Nov 2026): Getty AAT × ICCD, the first
vocabulary taken all the way. No published alignment of the ICCD material
thesaurus with the AAT was found to reuse (searched 18 Nov 2026: Bulla et al.,
SWODCH 2022, describe an automatic ICCD→AAT alignment with manual validation
but publish no data for this thesaurus; ARIADNE's AAT mappings are «not
publicly available yet»). So these are PROPOSED here:

* a concept of SOURCE whose preferred label, in a language, equals (accents,
  case and a parenthesised qualifier aside) a preferred or alternative label
  of a concept of TARGET in the same language → ``closeMatch`` — never
  ``exactMatch``: equal words are a reason to look, not an identity;
* every row ``status: proposed``, ``by:`` the MICRO. A person makes it
  ``verified``.

It reads the indices compiled on this machine (``s3dgraphy.authorities.packages``,
``EM_VOCABULARIES_DIR``) and writes a YAML in the shape of ``alignments/``::

    python3 tools/align_by_label.py iccd-ra-materia iccd-ra-materia \\
        getty-aat-materials getty-aat OUT.yaml [--only-top]
"""
from __future__ import annotations

import argparse
import sys

import yaml


def main(argv=None) -> int:
    from s3dgraphy.authorities import packages as P
    ap = argparse.ArgumentParser()
    ap.add_argument("source_pkg")
    ap.add_argument("source_scheme")
    ap.add_argument("target_pkg")
    ap.add_argument("target_scheme")
    ap.add_argument("out")
    ap.add_argument("--by", default="MICRO-U (2026-11-18), proposta per etichetta uguale")
    a = ap.parse_args(argv)
    src, tgt = P.vocab_index(a.source_pkg), P.vocab_index(a.target_pkg)
    if not src or not tgt:
        raise SystemExit("both packages must be installed here")
    by_label = {}
    for uri, c in tgt["concepts"].items():
        for lang, text in (c.get("pref") or {}).items():
            by_label.setdefault((lang.split("-")[0], P.norm_label(text)), set()).add(uri)
        for lang, texts in (c.get("alt") or {}).items():
            for text in texts:
                by_label.setdefault((lang.split("-")[0], P.norm_label(text)), set()).add(uri)
    rows = []
    for uri in sorted(src["concepts"]):
        c = src["concepts"][uri]
        for lang, text in sorted((c.get("pref") or {}).items()):
            hits = sorted(by_label.get((lang.split("-")[0], P.norm_label(text)), ()))
            for h in hits:
                en = (tgt["concepts"][h].get("pref") or {}).get("en", "")
                rows.append({"source": {"scheme": a.source_scheme, "concept": uri},
                             "match": "closeMatch",
                             "target": {"scheme": a.target_scheme, "concept": h},
                             "status": "proposed", "by": a.by,
                             "note": f"«{text}» ({lang}) = {h.rsplit('/', 1)[-1]} «{en}»"
                                     + (f" — {len(hits)} candidates for this label" if len(hits) > 1 else "")})
    head = ("# " + a.source_pkg + " ↔ " + a.target_pkg + ": PROPOSED by tools/align_by_label.py\n"
            "# (the same label in the same language → closeMatch, never exactMatch).\n"
            f"# Source index {src['version']} (sha256 {src['source_sha256'][:12]}), "
            f"target index {tgt['version']} (sha256 {tgt['source_sha256'][:12]}).\n"
            "# No published ICCD-materia ↔ AAT alignment was found to reuse (18 Nov 2026):\n"
            "# Bulla et al., SWODCH 2022, publish no data for it; ARIADNE's mappings are not public.\n"
            "# Every row waits for a person: status proposed until verified, with who verified it.\n")
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(head)
        yaml.safe_dump({"alignments": rows}, fh, allow_unicode=True, sort_keys=False, width=200)
    print(f"{len(rows)} proposals → {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
