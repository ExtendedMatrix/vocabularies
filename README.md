# Extended Matrix — vocabularies

The controlled vocabularies of the **Extended Matrix** (EM) ecosystem.

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
tools/        publish_vocab.py — publishes the modules to the site
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

## Using a module

Every module resolves as Linked Data:

```
https://w3id.org/extendedmatrix/vocab/us-colore/       → human page
https://w3id.org/extendedmatrix/vocab/us-colore/us-colore.ttl → Turtle
```

In an em.json file a quale points at the concept IRI; the label is resolved
at reading time, in the reader's language. Tools that render recording sheets
(stratigraph-templates) read the `schemes/` cards to know which scheme a field
is bound to and where its labels come from.

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
