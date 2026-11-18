# Extended Matrix — vocabularies

The controlled vocabularies of the **Extended Matrix** (EM) ecosystem, and the
place where scientific communities declare their **profiles**.

| | |
|---|---|
| Namespace | `https://w3id.org/extendedmatrix/vocab/<module>/` |
| Published at | <https://extendedmatrix.org/vocab/> |
| Licence | Vocabularies: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · schemas: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) · tools: EUPL-1.2 — see [LICENSING.md](LICENSING.md) |
| Maintained by | the Extended Matrix project, CNR-ISPC, with the curators of each module |

## What is here

```
skos/         the SKOS modules EM originates (Turtle), one file per module
schemes/      one YAML per vocabulary scheme: ours (origin: originated) and the
              external ones we only declare (ICCD, Getty AAT, iDAI.field …)
alignments/   skos:exactMatch / closeMatch … between schemes, each proposed or verified
fixtures/     invented micro-schemes used by the tests; not normative
profiles/     the EM Profiles specification, its schema, and the community profiles
packages/     the vocabulary packages (one card each), built by tools/build_packages.py
tools/        publish_vocab.py — publishes the modules to the site;
              core_types.py — lists the core types a profile may specialise;
              build_packages.py, getty_aat_export.py — the packages
tests/        the checks every pull request must pass
```

**A module** is a small SKOS concept scheme with its own namespace under
`w3id.org/extendedmatrix/vocab/`, a version, a lifecycle state, curators and a
licence. Its `schemes/*.yaml` card says all of that; its `skos/*.ttl` file holds
the concepts, each with its source (`dct:source`).

**A declared scheme** is somebody else's vocabulary (a national thesaurus, the
Getty AAT, an application's valuelists). We do not copy it: we give it an
identity so that our concepts can be aligned with it, and say where it is
resolved from.

**A profile** is what a scientific community brings to EM: its qualia
vocabularies, its extractors and documents, its own node and edge types (each
a species of a core type) with their glyphs, and pointers to its plugins.
The specification is [`profiles/SPEC.md`](profiles/SPEC.md) (version 0.1,
Editor's Draft); [`profiles/example-toolmarks/`](profiles/example-toolmarks/)
is a minimal example.

## Using a module

Every module resolves as Linked Data: its namespace IRI redirects to the
Turtle, and the site carries a human page beside it.

```
https://w3id.org/extendedmatrix/vocab/us-colore/  → https://extendedmatrix.org/vocab/us-colore/us-colore.ttl
https://extendedmatrix.org/vocab/us-colore/       → the human page
```

In an em.json file a quale points at the concept IRI; the label is resolved
at reading time, in the reader's language. Tools that render recording sheets
(stratigraph-templates) read the `schemes/` cards to know which scheme a field
is bound to and where its labels come from.

## Packages: vocabularies installed like fonts

Since 18 November 2026 (MICRO-U, decided by E.D.) the EM tools install
vocabularies on the machine, in one folder they all share, the way a computer
installs fonts. A **package** (`<id>-<version>.emvocab.zip`) is the SOURCE of a
vocabulary, unmodified, with a manifest (`em-vocabulary-package/1`): id,
version, snapshot date, languages, licence, **tier**, the attribution to show,
the sha256 of the source. The index is never shipped: each machine compiles
its own when it installs (`s3dgraphy.authorities.packages`).

```
packages/<id>/package.yaml   the card of a package: where its source comes from
tools/build_packages.py      builds the packages and catalog.json (release assets)
tools/getty_aat_export.py    a dated export of the Getty AAT (SPARQL, or Linked Art)
```

| Tier | Licence | What travels |
|---|---|---|
| A | open (CC0, CC BY, ODC-By) | the package; the terms a file uses may be copied into it |
| B | share-alike (CC BY-SA) | the package, its source a separate unmodified file; the terms copied keep that licence |
| C | not redistributable | only the card: the tool fetches the source and keeps it on that machine |

Today: `iccd-ra-materia` (tier B, the ICCD file as published) and
`getty-aat-materials` (tier A, the Materials hierarchy of the AAT, exported on
the day of the release). The alignments between them are in
`alignments/materials-aat-iccd.yaml`: 29 closeMatch, all verified by E.D. on
18 Nov 2026 (intonaco deliberately left unaligned: the file says why).

```
python3 tools/build_packages.py dist --iccd <Standard-catalografici> \
    --export getty-aat-materials=<export.nt> --date <YYYY-MM-DD>
```

## Contributing

Pull requests are welcome, and every one is reviewed. Read
[CONTRIBUTING.md](CONTRIBUTING.md) first: it says what a module must carry,
how a proposal becomes stable, and who answers for what.

## Provenance

The modules were born in the `vocabularies/` folder of
[stratigraph-templates](https://github.com/StratiGraph-ECCCH/stratigraph-templates)
(StratiGraph WP3, CNR-ISPC). This repository was created on 25 October 2026 by
splitting that folder out with its history (`git subtree split`): the first
four commits here are those of stratigraph-templates that touched the folder,
the last of them being `14e5f3a` there. From that date this repository is the
source; the copy in stratigraph-templates is kept so that nothing reading it
breaks, and is marked as a copy.

## Publishing

```
python3 tools/publish_vocab.py <path to ExtendedMatrix-site> [module ...]
```

writes `public/vocab/<module>/` on the site — the Turtle behind a header naming
this repository and the commit, and a human page — and regenerates the index.
Commit first: the script refuses a source with uncommitted changes, because the
header must name a commit.

## Tests

```
pip install -r requirements.txt
pytest
```
