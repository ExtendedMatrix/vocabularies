"""Every profile validates against the manifest schema, and holds together.

The schema checks the form. The rest is what a schema cannot say: that each
type is a species of a core type that exists, that every type a rule or a
connection names is declared, that the vocabularies are there and say the
version the manifest says (profiles/SPEC.md).
"""
import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF, SKOS

REPO = Path(__file__).resolve().parents[1]
PROFILES = REPO / "profiles"
SCHEMA = json.loads((PROFILES / "profile.v0.1.schema.json").read_text(encoding="utf-8"))
CORE = json.loads((PROFILES / "core-types.json").read_text(encoding="utf-8"))
CORE_NODES, CORE_EDGES = set(CORE["node_types"]), set(CORE["edge_types"])
MANIFESTS = sorted(p.parent.name for p in PROFILES.glob("*/profile.json"))
EMJSON_SCHEMA = Path(__file__).resolve().parents[2] / "s3Dgraphy" / "spec" / "em-json" / "em.v1.1.schema.json"


def manifest(name):
    return json.loads((PROFILES / name / "profile.json").read_text(encoding="utf-8"))


def own_types(m):
    node = {t["type"] for t in m.get("node_types", [])}
    node |= {t["id"] for t in m.get("extractor_types", [])} | {t["id"] for t in m.get("document_types", [])}
    edge = {t["type"] for t in m.get("edge_types", [])}
    edge |= {t["reverse"]["type"] for t in m.get("edge_types", []) if t.get("reverse")}
    props = {q["property_type"] for q in m.get("qualia_vocabularies", []) if ":" in q["property_type"]}
    return node, edge, props


def test_the_schema_is_a_valid_schema():
    Draft202012Validator.check_schema(SCHEMA)


def test_core_types_say_where_they_come_from():
    assert CORE["source"]["nodes"] and CORE["source"]["connections"] and CORE["source"]["commit"]
    assert {"US", "UL", "document", "extractor", "property"} <= CORE_NODES
    assert {"is_after", "has_property", "extracted_from"} <= CORE_EDGES


def test_there_is_an_example_profile():
    assert MANIFESTS and any(manifest(n).get("example") for n in MANIFESTS)


@pytest.mark.parametrize("name", MANIFESTS)
def test_the_manifest_validates(name):
    errors = sorted(Draft202012Validator(SCHEMA, format_checker=FormatChecker()).iter_errors(manifest(name)),
                    key=lambda e: list(e.path))
    assert not errors, "\n".join(f"{list(e.path)}: {e.message}" for e in errors)


@pytest.mark.parametrize("name", MANIFESTS)
def test_name_and_prefix_hold_together(name):
    m = manifest(name)
    assert m["name"] == name, "the name is the name of the folder"
    node, edge, props = own_types(m)
    for t in node | edge | props:
        assert t.split(":", 1)[0] == m["prefix"], f"{t}: a profile type carries the profile's prefix"
    assert len(node | edge | props) == len(node) + len(edge) + len(props), "a type name is used twice"


@pytest.mark.parametrize("name", MANIFESTS)
def test_every_type_is_a_species_of_a_core_type(name):
    m = manifest(name)
    for t in m.get("node_types", []):
        assert t["specializes"] in CORE_NODES, f"{t['type']}: {t['specializes']} is not a core node type"
    for t in m.get("edge_types", []):
        if "specializes" in t:
            assert t["specializes"] in CORE_EDGES, f"{t['type']}: {t['specializes']} is not a core edge type"


@pytest.mark.parametrize("name", MANIFESTS)
def test_every_type_a_rule_names_is_declared(name):
    m = manifest(name)
    node, edge, props = own_types(m)
    known_nodes = node | CORE_NODES
    for t in m.get("edge_types", []):
        for c in t["allowed_connections"]:
            assert c["source"] in known_nodes and c["target"] in known_nodes, f"{t['type']}: {c}"
    for x in m.get("extractor_types", []):
        for d in x.get("source_documents", []):
            assert d in known_nodes, f"{x['id']}: unknown source document {d}"
        for q in x.get("produces", []):
            assert q in props or ":" not in q, f"{x['id']}: produces {q}, which no qualia vocabulary declares"
    vr = m.get("visual_rules", {})
    for block in ("node_styles", "2d_glyphs"):
        for k in vr.get(block, {}):
            assert k in node, f"visual_rules.{block}.{k}: not a node type of the profile"
    for k in vr.get("edge_style", {}):
        assert k in edge, f"visual_rules.edge_style.{k}: not an edge type of the profile"
    for k, rule in vr.get("matrix", {}).items():
        assert k in node | edge, f"visual_rules.matrix.{k}: not a type of the profile"
        lane = rule.get("lane", "")
        if lane.startswith("follow:"):
            assert lane[7:] in edge | CORE_EDGES, f"visual_rules.matrix.{k}: lane follows an unknown edge"
    for p in m.get("plugins", []):
        for h in p.get("handles", []):
            assert h in known_nodes, f"plugin {p['id']}: handles unknown type {h}"
        d = p["descriptor"]
        if d.get("writes") is False:
            assert not {"write-graph", "attach-asset", "materialize-3D", "ingest-batch"} & set(d["capabilities"]), \
                f"plugin {p['id']}: declares a writing capability with writes=false"


@pytest.mark.parametrize("name", MANIFESTS)
def test_the_qualia_vocabularies_are_there_and_say_the_same_version(name):
    m = manifest(name)
    for q in m.get("qualia_vocabularies", []):
        if "path" not in q:
            continue
        g = Graph().parse(PROFILES / name / q["path"], format="turtle")
        scheme = URIRef(q["scheme"])
        assert (scheme, RDF.type, SKOS.ConceptScheme) in g, f"{q['path']}: no scheme {q['scheme']}"
        assert str(g.value(scheme, OWL.versionInfo)) == q["version"]
        assert set(g.subjects(SKOS.inScheme, scheme)), f"{q['path']}: no concepts"


@pytest.mark.parametrize("name", MANIFESTS)
def test_the_example_document_declares_the_profile_and_falls_back(name):
    """An em.json that uses the profile cites it in its header, and every node
    or edge of a profile type carries what a reader without the profile needs
    to draw it as the core type it specialises (SPEC §6)."""
    path = PROFILES / name / "example.em.json"
    if not path.exists():
        pytest.skip("no example document")
    m, doc = manifest(name), json.loads(path.read_text(encoding="utf-8"))
    assert {"iri": m["iri"], "version": m["version"]} in doc["header"]["profiles"]
    node_parent = {t["type"]: t["specializes"] for t in m.get("node_types", [])}
    edges = {t["type"]: t for t in m.get("edge_types", [])}
    kinds = {t["id"] for t in m.get("extractor_types", []) + m.get("document_types", [])}
    for g in doc["graphs"].values():
        for n in g["nodes"]:
            if n["node_type"] in node_parent:
                assert n["data"]["em_specializes"] == node_parent[n["node_type"]]
            kind = (n.get("data") or {}).get("em_kind")
            if kind and kind.startswith(m["prefix"] + ":"):
                assert kind in kinds and n["node_type"] in {"extractor", "document"}
        for e in g["edges"]:
            if e["edge_type"] in edges:
                a = e["attributes"]
                assert a["em_family"] == edges[e["edge_type"]]["family"]
                assert a["em_propagates"] == edges[e["edge_type"]]["propagates"]
    if EMJSON_SCHEMA.exists():
        schema = json.loads(EMJSON_SCHEMA.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(doc))
        assert not errors, errors[0].message
