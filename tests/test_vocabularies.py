"""What every module, card and alignment of this repository must hold.

These are the checks on the DATA. The checks on how a renderer resolves a
label through an alignment, or draws a sheet, stay in stratigraph-templates
with the renderer they test; the invariants they rely on are here, so that a
pull request that breaks them is refused where the data lives.
"""
import re
from pathlib import Path

import pytest
import yaml
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

REPO = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
LIFECYCLE = {"proposed", "stable", "deprecated"}
MATCHES = {"exactMatch", "closeMatch", "broadMatch", "narrowMatch", "relatedMatch"}
NAMESPACE = "https://w3id.org/extendedmatrix/vocab/"


def _cards():
    out = {}
    for f in sorted((REPO / "schemes").glob("*.yaml")):
        s = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("scheme")
        assert s, f"{f.name}: no `scheme:` block"
        assert s["id"] not in out, f"{f.name}: scheme id {s['id']} declared twice"
        out[s["id"]] = s
    return out


CARDS = _cards()
ORIGINATED = sorted(i for i, s in CARDS.items() if s.get("origin") == "originated")
LOCAL = sorted(i for i, s in CARDS.items() if (s.get("resolve") or {}).get("kind") == "skos_file")
_GRAPHS = {}


def graph(sid):
    if sid not in _GRAPHS:
        _GRAPHS[sid] = Graph().parse(REPO / CARDS[sid]["resolve"]["path"], format="turtle")
    return _GRAPHS[sid]


def alignments():
    rows = []
    for f in sorted((REPO / "alignments").glob("*.yaml")):
        for a in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("alignments") or []:
            rows.append((f.name, a))
    return rows


def test_there_is_something_to_check():
    assert len(ORIGINATED) >= 6 and LOCAL


@pytest.mark.parametrize("ttl", sorted(p.name for p in (REPO / "skos").glob("*.ttl"))
                         + sorted("fixtures/" + p.name for p in (REPO / "fixtures").glob("*.ttl")))
def test_every_turtle_file_parses(ttl):
    path = REPO / ("skos/" + ttl if "/" not in ttl else ttl)
    assert len(Graph().parse(path, format="turtle")) > 0


@pytest.mark.parametrize("sid", sorted(CARDS))
def test_every_card_says_who_and_what(sid):
    s = CARDS[sid]
    for key in ("id", "authority", "labels", "status"):
        assert s.get(key), f"{sid}: missing {key}"
    assert s["status"] in {"declared", "resolvable"}
    assert s.get("origin", "external") in {"external", "originated"}
    if not s.get("fixture"):
        assert s.get("license") and s.get("attribution"), f"{sid}: licence and attribution are owed"


@pytest.mark.parametrize("sid", LOCAL)
def test_a_local_scheme_points_at_a_file_that_is_there(sid):
    assert (REPO / CARDS[sid]["resolve"]["path"]).is_file()


@pytest.mark.parametrize("sid", ORIGINATED)
def test_an_originated_module_carries_version_lifecycle_curators_licence(sid):
    s = CARDS[sid]
    assert SEMVER.match(str(s.get("version", ""))), f"{sid}: version must be semver"
    assert s.get("lifecycle") in LIFECYCLE, f"{sid}: lifecycle must be one of {sorted(LIFECYCLE)}"
    assert s.get("curators"), f"{sid}: who answers for it?"
    assert s.get("license")
    assert s["uri"].startswith(NAMESPACE) and s["uri"].endswith("/")
    assert s["status"] == "resolvable" and s["resolve"]["kind"] == "skos_file"
    if s["lifecycle"] == "proposed":
        assert s["version"].startswith("0."), f"{sid}: a proposed module stays at 0.x"


@pytest.mark.parametrize("sid", ORIGINATED)
def test_the_turtle_says_what_the_card_says(sid):
    s, g = CARDS[sid], graph(sid)
    scheme = URIRef(s["uri"])
    assert (scheme, RDF.type, SKOS.ConceptScheme) in g
    assert str(g.value(scheme, OWL.versionInfo)) == s["version"], f"{sid}: owl:versionInfo != card version"
    assert g.value(scheme, DCTERMS.license) is not None


@pytest.mark.parametrize("sid", ORIGINATED)
def test_every_concept_has_label_definition_and_source(sid):
    s, g = CARDS[sid], graph(sid)
    concepts = set(g.subjects(SKOS.inScheme, URIRef(s["uri"])))
    assert concepts, f"{sid}: no concepts"
    for c in concepts:
        assert str(c).startswith(s["uri"]), f"{c} outside the namespace of {sid}"
        assert (c, RDF.type, SKOS.Concept) in g
        assert list(g.objects(c, SKOS.prefLabel)), f"{c}: no prefLabel"
        assert list(g.objects(c, SKOS.definition)), f"{c}: no definition"
        assert list(g.objects(c, DCTERMS.source)), f"{c}: no term enters without a source"


@pytest.mark.parametrize("sid", ORIGINATED)
def test_one_preflabel_per_language(sid):
    s, g = CARDS[sid], graph(sid)
    for c in set(g.subjects(SKOS.inScheme, URIRef(s["uri"]))):
        langs = [o.language for o in g.objects(c, SKOS.prefLabel) if isinstance(o, Literal)]
        assert len(langs) == len(set(langs)), f"{c}: two prefLabels in one language"


@pytest.mark.parametrize("sid", sorted(i for i, s in CARDS.items() if s.get("provisional")))
def test_a_provisional_stand_in_is_ours_and_resolvable(sid):
    """A declared scheme (a standard that has not published its SKOS) may name
    one of our modules to answer for it until it does."""
    s = CARDS[sid]
    assert s["status"] == "declared"
    ours = CARDS.get(s["provisional"])
    assert ours and ours.get("origin") == "originated" and ours["status"] == "resolvable"


@pytest.mark.parametrize("sid", sorted(i for i, s in CARDS.items() if s.get("unverified_languages")))
def test_unverified_languages_only_on_a_module_of_ours(sid):
    assert CARDS[sid].get("origin") == "originated"


@pytest.mark.parametrize("row", alignments(), ids=lambda r: f"{r[0]}:{r[1]['source']['concept'].rsplit('/', 1)[-1]}")
def test_every_alignment_joins_two_declared_schemes(row):
    name, a = row
    assert a["match"] in MATCHES, f"{name}: {a['match']}"
    assert a.get("status", "proposed") in {"proposed", "verified"}
    if a.get("status") == "verified":
        assert a.get("by"), f"{name}: a verified alignment says who verified it"
    for side in ("source", "target"):
        sid = a[side]["scheme"]
        assert sid in CARDS, f"{name}: {side} scheme {sid} is not declared in schemes/"
        if sid in LOCAL:
            assert (URIRef(a[side]["concept"]), RDF.type, SKOS.Concept) in graph(sid), \
                f"{name}: {a[side]['concept']} is not a concept of {sid}"
