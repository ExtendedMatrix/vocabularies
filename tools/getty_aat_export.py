#!/usr/bin/env python3
"""A real, dated export of a part of the Getty AAT, for an EM vocabulary package.

Two ways to the same AAT: the SPARQL endpoint (default) and, when that is
degraded, Getty's Linked Art records (``--via linked-art``,
https://data.getty.edu/vocab/aat/<id>) — the same concepts, names and
hierarchy, one record per concept.

MICRO-U-VOCABOLARI-COME-FONT (E.D., 18 Nov 2026). The package `getty-aat-materials`
carries the Materials hierarchy of the AAT (300010357, every concept below it)
and the Roman building techniques the Templu Mare and Basilica Iulia graphs
use, in every language the AAT gives for them. They are read from the official
SPARQL endpoint, https://vocab.getty.edu/sparql, nowhere else.

The endpoint refuses heavy queries (``Service temporarily degraded`` after
about ten seconds, measured on 18 Nov 2026), so the hierarchy is walked in
light steps: the children of up to ``BATCH`` parents at a time
(``gvp:broaderPreferred``), then the labels of up to ``BATCH`` concepts at a
time. Each request is retried with a pause.

What is written is N-Triples of Getty's own statements, selected, not changed:
``rdf:type skos:Concept``, ``skos:inScheme``, ``skos:prefLabel``,
``skos:altLabel`` (every language), ``skos:broader`` (the PREFERRED parent,
written with the SKOS property Getty also states), ``skos:scopeNote`` is left
out (it is a resource in the AAT, not a literal). Licence: ODC-By 1.0 — the
attribution goes with the package (its manifest) and wherever its terms are
shown.

    python3 tools/getty_aat_export.py OUT.nt [--extra 300266485 …]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Set

ENDPOINT = "https://vocab.getty.edu/sparql.json"
AAT = "http://vocab.getty.edu/aat/"
SKOS = "http://www.w3.org/2004/02/skos/core#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SCHEME = "http://vocab.getty.edu/aat/"
MATERIALS = "300010357"
BATCH = 40

#: Roman building techniques used by Templu Mare v10 and Basilica Iulia (opus …),
#: looked up by label on the endpoint and listed here so the export is the same
#: every time it runs. Their hierarchy is not walked: the concepts themselves.
ROMAN_TECHNIQUES_LABELS = [
    "opus reticulatum", "opus incertum", "opus quadratum", "opus latericium",
    "opus testaceum", "opus mixtum", "opus spicatum", "opus caementicium",
    "opus vittatum", "opus signinum", "opus sectile", "opus africanum",
    "ashlar", "rubble masonry", "brickwork", "mortar (material)", "stucco",
    "lime mortar", "concrete (material)",
]


#: …and their ids, read from the SPARQL endpoint on 18 Nov 2026 (luc:term
#: "opus*", prefLabel en): caementicium, incertum, latericium, spicatum, mixtum,
#: quadratum, reticulatum, romanum, signinum, testaceum. The Linked Art way has
#: no search: it fetches these records by id.
ROMAN_TECHNIQUES = ["300379970", "300262689", "300379971", "300417912", "300265615",
                    "300379973", "300262690", "300263252", "300379969", "300265616"]


def query(q: str, tries: int = 60) -> List[Dict[str, Dict[str, str]]]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": q})
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Accept": "application/sparql-results+json",
                "User-Agent": "ExtendedMatrix-vocabularies/1 (CNR-ISPC; emanuel.demetrescu@cnr.it)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read().decode("utf-8")
            if not body.lstrip().startswith("{"):
                raise RuntimeError(body[:80])
            return json.loads(body)["results"]["bindings"]
        except Exception as exc:  # noqa: BLE001 — retried, then raised
            last = exc
            time.sleep(min(60, 3 + 4 * i))
    raise RuntimeError(f"SPARQL failed after {tries} tries: {last}")


def _values(ids: Iterable[str]) -> str:
    return " ".join(f"aat:{i}" for i in ids)


def children(parents: List[str]) -> Dict[str, str]:
    q = ("PREFIX aat: <http://vocab.getty.edu/aat/> "
         "PREFIX gvp: <http://vocab.getty.edu/ontology#> "
         "SELECT ?c ?p WHERE { VALUES ?p { " + _values(parents) + " } "
         "?c gvp:broaderPreferred ?p }")
    out = {}
    for b in query(q):
        out[b["c"]["value"][len(AAT):]] = b["p"]["value"][len(AAT):]
    return out


def labels(ids: List[str]) -> List[tuple]:
    q = ("PREFIX aat: <http://vocab.getty.edu/aat/> "
         "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> "
         "SELECT ?c ?k ?l WHERE { VALUES ?c { " + _values(ids) + " } "
         "VALUES ?k { skos:prefLabel skos:altLabel } ?c ?k ?l }")
    return [(b["c"]["value"], b["k"]["value"], b["l"]["value"], b["l"].get("xml:lang", ""))
            for b in query(q)]


def by_label(text: str) -> List[str]:
    q = ("PREFIX skos: <http://www.w3.org/2004/02/skos/core#> "
         "PREFIX gvp: <http://vocab.getty.edu/ontology#> "
         "SELECT DISTINCT ?c WHERE { ?c gvp:prefLabelGVP/<http://www.w3.org/2008/05/skos-xl#literalForm> \""
         + text.replace('"', '') + "\"@en . ?c skos:inScheme <http://vocab.getty.edu/aat/> }")
    return [b["c"]["value"][len(AAT):] for b in query(q)]


LINKED_ART = "https://data.getty.edu/vocab/aat/"
PREFERRED_TERM = "http://vocab.getty.edu/aat/300404670"


def linked_art(cid: str, tries: int = 12) -> dict:
    """One concept from Getty's Linked Art service (the same AAT, as JSON-LD)."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(LINKED_ART + cid, headers={
                "Accept": "application/ld+json",
                "User-Agent": "ExtendedMatrix-vocabularies/1 (CNR-ISPC; emanuel.demetrescu@cnr.it)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(min(30, 2 + 3 * i))
    raise RuntimeError(f"{cid}: Linked Art failed after {tries} tries: {last}")


def _ids(items) -> List[str]:
    out = []
    for it in items or []:
        u = it.get("id", "") if isinstance(it, dict) else str(it)
        if u.startswith(AAT):
            out.append(u[len(AAT):])
    return out


def walk_linked_art(root: str, workers: int = 6) -> Dict[str, dict]:
    """Every concept under ``root`` (its narrower, all the way down), from the
    Linked Art records: ``{id: record}``."""
    from concurrent.futures import ThreadPoolExecutor
    got: Dict[str, dict] = {}
    frontier = [root]
    depth = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while frontier:
            recs = list(pool.map(linked_art, frontier))
            nxt: List[str] = []
            for cid, rec in zip(frontier, recs):
                got[cid] = rec
                for n in _ids(rec.get("narrower")):
                    if n not in got and n not in nxt and n not in frontier:
                        nxt.append(n)
            depth += 1
            print(f"depth {depth}: +{len(nxt)} (total {len(got)})", file=sys.stderr)
            frontier = nxt
    return got


def triples_from_linked_art(records: Dict[str, dict]) -> List[str]:
    """Getty's own statements, in SKOS: per language the PREFERRED name (the one
    Getty classifies «preferred term», else the first) as skos:prefLabel, the
    others as skos:altLabel; skos:broader from the record's ``broader``."""
    lines: List[str] = []
    for cid, rec in records.items():
        s = f"<{AAT}{cid}>"
        lines.append(f"{s} <{RDF_TYPE}> <{SKOS}Concept> .")
        lines.append(f"{s} <{SKOS}inScheme> <{SCHEME}> .")
        for b in _ids(rec.get("broader")):
            lines.append(f"{s} <{SKOS}broader> <{AAT}{b}> .")
        by_lang: Dict[str, List[tuple]] = {}
        for n in rec.get("identified_by") or []:
            if n.get("type") != "Name" or not n.get("content"):
                continue
            langs = [l.get("_label", "") for l in n.get("language") or []] or [""]
            pref = any(c.get("id") == PREFERRED_TERM for c in n.get("classified_as") or [])
            for lang in langs:
                by_lang.setdefault(lang.lower(), []).append((not pref, n["content"]))
        for lang, names in by_lang.items():
            names.sort(key=lambda x: x[0])        # the preferred first, stable otherwise
            tag = f"@{lang}" if lang else ""
            seen = set()
            for k, (_, text) in enumerate(names):
                if text in seen:
                    continue
                seen.add(text)
                prop = "prefLabel" if k == 0 else "altLabel"
                lines.append(f"{s} <{SKOS}{prop}> {_lit(text)}{tag} .")
    return lines


def _lit(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r") + '"'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", default=MATERIALS)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--max-depth", type=int, default=30)
    ap.add_argument("--via", choices=["sparql", "linked-art"], default="sparql",
                    help="linked-art: Getty's Linked Art records (data.getty.edu/vocab/aat), "
                         "when the SPARQL endpoint is degraded (measured on 18 Nov 2026)")
    a = ap.parse_args(argv)
    if a.via == "linked-art":
        records = walk_linked_art(a.root)
        for cid in list(a.extra) + ROMAN_TECHNIQUES:
            if cid not in records:
                records[cid] = linked_art(cid)
        lines = sorted(set(triples_from_linked_art(records)))
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"{len(records)} concepts, {len(lines)} triples → {a.out}", file=sys.stderr)
        return 0

    parent: Dict[str, str] = {a.root: ""}
    frontier = [a.root]
    depth = 0
    while frontier and depth < a.max_depth:
        nxt: List[str] = []
        for i in range(0, len(frontier), BATCH):
            got = children(frontier[i:i + BATCH])
            for c, p in got.items():
                if c not in parent:
                    parent[c] = p
                    nxt.append(c)
        depth += 1
        print(f"depth {depth}: +{len(nxt)} (total {len(parent)})", file=sys.stderr)
        frontier = nxt

    extra: Set[str] = set(a.extra)
    for text in ROMAN_TECHNIQUES_LABELS:
        for c in by_label(text):
            extra.add(c)
    extra -= set(parent)
    # the preferred parent of each extra concept, so «broader» is stated
    for i in range(0, len(sorted(extra)), BATCH):
        part = sorted(extra)[i:i + BATCH]
        q = ("PREFIX aat: <http://vocab.getty.edu/aat/> "
             "PREFIX gvp: <http://vocab.getty.edu/ontology#> "
             "SELECT ?c ?p WHERE { VALUES ?c { " + _values(part) + " } ?c gvp:broaderPreferred ?p }")
        for b in query(q):
            parent[b["c"]["value"][len(AAT):]] = b["p"]["value"][len(AAT):]
    for c in extra:
        parent.setdefault(c, "")
    print(f"extra concepts: {len(extra)}", file=sys.stderr)

    ids = sorted(parent)
    lines: List[str] = []
    for i in range(0, len(ids), BATCH):
        for c, k, l, lang in labels(ids[i:i + BATCH]):
            lit = _lit(l) + (f"@{lang}" if lang else "")
            lines.append(f"<{c}> <{k}> {lit} .")
        if (i // BATCH) % 10 == 0:
            print(f"labels {i}/{len(ids)}", file=sys.stderr)
    for c in ids:
        lines.append(f"<{AAT}{c}> <{RDF_TYPE}> <{SKOS}Concept> .")
        lines.append(f"<{AAT}{c}> <{SKOS}inScheme> <{SCHEME}> .")
        if parent[c]:
            lines.append(f"<{AAT}{c}> <{SKOS}broader> <{AAT}{parent[c]}> .")
    lines = sorted(set(lines))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"{len(ids)} concepts, {len(lines)} triples → {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
