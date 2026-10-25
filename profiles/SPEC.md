# EM Profiles — how a community extends Extended Matrix

**Version 0.1 · Editor's Draft · 25 October 2026**

| | |
|---|---|
| This version | `profiles/SPEC.md` in [ExtendedMatrix/vocabularies](https://github.com/ExtendedMatrix/vocabularies) |
| Schema | [`profile.v0.1.schema.json`](profile.v0.1.schema.json) (to be served at `https://w3id.org/extendedmatrix/schemas/profile.v0.1.schema.json`) |
| Editor | Emanuel Demetrescu (CNR-ISPC), ORCID [0000-0002-5065-7970](https://orcid.org/0000-0002-5065-7970) |
| Licence | Text: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Schema and examples: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Status | **Editor's Draft.** The name «EM Profiles» is provisional. Implementable, but it may change before it becomes a Release. |
| Related | [em.json — the Extended Matrix document format](https://w3id.org/extendedmatrix/spec/em-json/), version 1.1 |

## 1. What it is for

Extended Matrix is one formal language. Scientific communities use it with
things of their own: the values they record, the ways they read their
sources, the documents only they produce, sometimes a kind of unit or a
relation the core does not name, and the tools they use to look at their
media. An **EM Profile** is the package in which a community declares all of
that, so that:

- the language stays **one**: every new type is a species of a core type, and
  the core algorithms keep working on data that uses it;
- a file that uses a profile **says so**, and a tool that does not have the
  profile still opens the file, draws every node and loses nothing;
- the profile has an identity, a version and curators of its own, and can
  change without touching the version of the core or of the file format.

A profile is declared in a manifest, `profile.json`, in its own folder of this
repository. This document says what the manifest contains, how a profile is
used in an em.json file, and how it is versioned.

## 2. A profile in PROF terms

The specification follows the W3C vocabulary
[*The Profiles Vocabulary*](https://www.w3.org/TR/dx-prof/) (PROF). An EM
Profile is a **`prof:Profile`** that is a profile of (`prof:isProfileOf`) the
em.json format and of the EM core; its parts are **resources** described by
`prof:ResourceDescriptor`, each with a **role**. The manifest is the
serialisation of that description; the correspondence is fixed:

| Manifest | PROF |
|---|---|
| `iri` | the `prof:Profile` |
| `prefix` | `prof:hasToken` |
| `is_profile_of[]` | `prof:isProfileOf` |
| `qualia_vocabularies[]` | resource, role `role:vocabulary`, artifact = the SKOS scheme |
| `extractor_types[]`, `document_types[]`, `node_types[]`, `edge_types[]` | resource, role `role:vocabulary` (the profile's own terms); their `mapping` IRIs: role `role:mapping` |
| `visual_rules` | resource, role `emrole:visual-rules` |
| `plugins[]` | resource, role `emrole:plugin`, artifact = `href` |
| `example.em.json` | resource, role `role:example` |
| `profile.json` and the schema it validates against | resource, role `role:specification` and `role:validation` |

`role:` is `http://www.w3.org/ns/dx/prof/role/`. PROF has no role for visual
rules nor for plugins; `emrole:` is
`https://w3id.org/extendedmatrix/profiles/role#`.

In Turtle, the head of the example profile reads:

```turtle
@prefix prof: <http://www.w3.org/ns/dx/prof/> .
@prefix role: <http://www.w3.org/ns/dx/prof/role/> .
@prefix dct:  <http://purl.org/dc/terms/> .

<https://example.org/em-profiles/example-toolmarks> a prof:Profile ;
    dct:title "Tool marks on dressed stone (example profile)"@en ;
    prof:hasToken "tm" ;
    prof:isProfileOf <https://w3id.org/extendedmatrix/spec/em-json/> ,
                     <https://w3id.org/extendedmatrix/core/> ;
    prof:hasResource [
        a prof:ResourceDescriptor ;
        prof:hasRole role:vocabulary ;
        prof:hasArtifact <https://example.org/em-profiles/example-toolmarks/vocab/tool-type/> ;
        dct:format <https://www.iana.org/assignments/media-types/text/turtle>
    ] .
```

## 3. The manifest

A profile lives in `profiles/<name>/` and its manifest is
`profiles/<name>/profile.json`. Beside it may stand the Turtle files of its
vocabularies, its SVG glyphs, and an `example.em.json`.

```
profiles/
  SPEC.md                      this document
  profile.v0.1.schema.json     the schema of the manifest
  core-types.json              the core types a profile may specialise (generated)
  <name>/
    profile.json
    vocab/*.ttl
    example.em.json
```

The keys every manifest carries:

| key | what |
|---|---|
| `profile_format` | the version of this specification the manifest follows: `"0.1"` |
| `iri` | the identity of the profile; real profiles live under `https://w3id.org/extendedmatrix/profile/<name>` |
| `name` | equal to the folder name |
| `prefix` | a short token (2–16 lowercase letters or digits): the profile's types are written `<prefix>:<name>` |
| `version` | semantic versioning (§5) |
| `lifecycle` | `proposed`, `stable` or `deprecated`, as for the vocabulary modules (CONTRIBUTING.md) |
| `title`, `description` | language-tagged texts (`{"en": "…"}`) |
| `curators` | who answers for the profile |
| `license` | of the profile's content; CC BY 4.0 unless there is a reason |
| `is_profile_of` | `[{iri, version}]`: the em.json format and the EM core it was written for |

**Types are prefixed.** Every type a profile introduces — node, edge,
extractor, document, quale — is written `<prefix>:<name>` (`tm:mark_field`),
so that it never collides with a core type nor with another profile's. Core
types are written bare (`UL`, `document`, `is_after`), as the core writes
them. The prefix is unique in this repository.

Readers ignore manifest keys they do not know.

## 4. What a profile may contain

### 4.1 Qualia vocabularies

A quale is the value of an EM property. A community that records a quality
with its own terms declares, in `qualia_vocabularies`, which property type
(`property_type`: a core one, or its own `<prefix>:<name>`) takes its values
from which SKOS scheme (`scheme`, its IRI, and `version`). When the scheme
lives in this repository, `path` points at its Turtle file; it follows the
rules of every module (CONTRIBUTING.md: version, sources on every concept,
definitions in our words).

### 4.2 Extractors and documents

`extractor_types` are the ways the community **reads** its sources: each
`specializes` the core `extractor`, says which `input_formats` it reads (media
types and extensions), from which `source_documents`, and which qualia it
`produces`.

`document_types` are the documents **peculiar** to the community: each
`specializes` the core `document`, says its `content_nature` (`2d_object` or
`3d_object`, the core's second axis) and its `formats`.

In em.json an extractor or a document of a profile kind is a core
`extractor` or `document` node that names its kind in `data.em_kind`
(`"tm:mark_reading"`); it needs no fallback, because its node type is the
core one.

### 4.3 Node and edge types

A community may bring **node types of its own**. Each one:

- **`specializes` a core node type** — a runtime `node_type` listed in
  `core-types.json` (a unit, a document, an extractor, a property…). The
  list is generated from s3Dgraphy (`tools/core_types.py`) and names the
  datamodel versions it was read from. What the core says of the parent
  holds for the species: its allowed connections, its place in the
  propagation of information, its mapping, unless the species narrows it;
- carries its own **`mapping`** — the IRI of the class it is mapped to, in
  the CIDOC CRM family, CRMem or another ontology; normally a subclass of the
  parent's class, or the parent's class itself;
- may declare the **`data_keys`** it adds to a node.

And **edge types of its own**. Each one:

- declares its **`family`** — `stratigraphic`, `relative_chronology`,
  `epochs`, `paradata` or `other`;
- declares whether it **`propagates`**: whether the core propagation
  algorithms must treat it as the core edge it `specializes`. **Normally
  not**: an edge that propagates changes what the core derives (an order in
  time, a contemporaneity), and must name the core edge it behaves as;
- lists its **`allowed_connections`** (source and target types, core or its
  own) and its **`mapping`** (the IRI of the property);
- may declare its `reverse`.

### 4.4 Glyphs and visual rules

`visual_rules` says how the profile's types are drawn, **in the same format
as the core's visual rules** (`em_visual_rules.json` in s3Dgraphy), keyed by
the profile type:

- `node_styles` — shape, border and fill colours, border style and width,
  label position, as the core's `node_styles.<type>.style`;
- `2d_glyphs` — the pictogram as vector paths (`viewBox`, `aspect`,
  `layers[].d`), as the core's `2d_glyphs`;
- `edge_style` — colour, line style and width, label;
- `matrix` — whether the type is drawn in the **Matrix** view (`draw`) and, if
  it is, in which **lane**: `first_epoch` (the lane of the epoch it begins
  in, by `has_first_epoch`, as a unit) or `follow:<edge_type>` (the lane of
  the node it reaches by that edge). The **Graph** view draws every type.

**Fallback.** A tool that does not have the profile draws a node of a
profile type with the rules of the core type it specialises, and an edge
with the style it gives any edge it does not know, labelled with its type; it keeps the node and the edge, and
writes them back unchanged (em.json 1.1 §3.1, §4.5). The file carries what
the fallback needs (§6), so the tool does not need the manifest to fall back.

### 4.5 Plugins

`plugins` points at the tools that view or interpret the profile's media —
a viewer of a particular image type, an interpreter that proposes readings.
A plugin entry is a **pointer, never code**: an `id`, a `kind` (`viewer`,
`interpreter`, `connector`), the `href` where it is published, the types it
`handles`, and its **`descriptor`** in the form of the EM plugin
architecture's connector descriptor: where it runs (`host`: `app-side` or
`emstudio-side`), how it is reached (`transport`), what it does
(`capabilities`, from the closed set of that architecture), the versions it
speaks (`emjson`, `datamodel`, `connector_api`) and whether it `writes`. A
tool that knows the architecture can offer the plugin to the user; a plugin
that declares a writing capability goes through the same checks as any
other connector (role, author, allowed connections).

## 5. Versions

Three axes, independent, never mixed:

- **the format** — em.json `header.version` (1.1): changes only with the
  form of the document;
- **the core** — the EM language: its datamodels (`header.datamodel_versions`)
  and the ontologies they map to; a profile names in `is_profile_of` the
  core version it was written for (`"1.6"`);
- **each profile** — its own `version`, in semantic versioning: **patch** for
  labels, descriptions and styles; **minor** for new types, new vocabulary
  concepts, new plugins; **major** when a type is removed or changes its
  parent, its family or whether it propagates. A profile stays at `0.x`
  while it is `proposed`.

Updating a profile does not change the number of the core nor of the format,
and a file written with version 1.2 of a profile is read by a tool that knows
version 1.0 of it, with the fallback for what it does not know.

## 6. Using a profile in an em.json file

A file that uses a profile **declares it in its header**, with the version
it was written with (em.json 1.1, §2.7):

```json
"header": {
  "format": "em.json",
  "version": "1.1",
  "profiles": [
    {"iri": "https://example.org/em-profiles/example-toolmarks", "version": "0.1.0"}
  ]
}
```

A **node of a profile type** keeps its type in `node_type` and names the core
type it specialises in `data.em_specializes`:

```json
{"id": "mf1", "node_type": "tm:mark_field", "name": "MF1",
 "data": {"em_specializes": "UL", "tm_face": "north"}}
```

An **edge of a profile type** names its family and whether it propagates in
its attributes, and the core edge it specialises when it has one:

```json
{"id": "e1", "edge_type": "tm:same_tool_as", "source": "mf1", "target": "mf2",
 "attributes": {"em_family": "other", "em_propagates": false}}
```

An extractor or a document of a profile kind is a core node with
`data.em_kind` (§4.2).

**A writer** that writes a profile type writes these keys, and declares the
profile in the header. **A reader** that does not have a profile declared in
the header opens the file all the same: it may say which profiles are
missing; it draws the profile's types by the fallback (§4.4); it keeps them,
with their data and attributes, when it writes the file back. A missing
profile is never a reason to refuse a file.

## 7. Conformance

- A **manifest** conforms when it validates against the schema of its
  `profile_format` and holds together: its types carry its prefix, each
  `specializes` names a core type of `core-types.json`, every type a rule, a
  connection or a plugin names is declared, every local vocabulary is there
  and says the version the manifest says. The tests of this repository
  (`tests/test_profiles.py`) check all of it on every pull request.
- A **document** that uses profiles conforms when it conforms to em.json, its
  header declares every profile whose types it uses, and every node and edge
  of a profile type carries the keys of §6.
- A **reader** conforms when it reads such a document without the profile,
  draws every node, and writes back what it read.

## 8. Contributing a profile

Open an issue that says who the community is, what it records and why the
core and the existing profiles are not enough; then a pull request that adds
`profiles/<name>/` with its manifest, its vocabularies and an
`example.em.json`, and a line in `.github/CODEOWNERS` that makes its curators
the reviewers of its folder. The editor of this specification reviews the
first version of every profile, to keep the language one: a type that the
core should have, rather than a profile, becomes a proposal for the core.

## 9. Example

[`example-toolmarks/`](example-toolmarks/) is a minimal profile, written to
illustrate this specification and not to be cited: a community that reads the
marks hand tools leave on dressed stone. It brings a vocabulary of three
tools for the quale `tm:tool`; an extractor `tm:mark_reading` that reads
photographs under raking light and 3D models; a document `tm:mark_map`; a node
type `tm:mark_field`, species of the core working unit `UL`; an edge
`tm:same_tool_as`, of family `other`, which does not propagate; their styles,
with the field drawn in the Matrix in the lane of its first epoch; and a
pointer to a viewer plugin. Its `example.em.json` uses it.

## 10. Open points

- The **name** («EM Profiles») is provisional.
- The **IRI of the EM core** (`https://w3id.org/extendedmatrix/core/`) and the
  namespace of real profiles (`https://w3id.org/extendedmatrix/profile/<name>`)
  are proposed and not yet registered.
- How a core tool **loads** a profile (from this repository, from a plugin
  package, from the file's header) is left to the tools and to the plugin
  architecture.

## 11. Changes

- **0.1 — 25 October 2026 (Editor's Draft).** First draft: the manifest, the
  PROF correspondence, the five kinds of content, the fallback, the three axes
  of version, the declaration in the em.json header.

## 12. How to cite

Demetrescu, E. (ed.) (2026). *EM Profiles — how a community extends Extended
Matrix*, version 0.1 (Editor's Draft). CNR-ISPC.
https://github.com/ExtendedMatrix/vocabularies/blob/main/profiles/SPEC.md
