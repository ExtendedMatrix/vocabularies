# Licences

Three kinds of file, three licences.

| What | Where | Licence |
|---|---|---|
| Vocabularies: SKOS modules, scheme cards, alignments, fixtures; the text of the specifications | `skos/`, `schemes/`, `alignments/`, `fixtures/`, `*.md` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| JSON schemas | `*.schema.json` | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Tools and tests | `tools/`, `tests/` | [EUPL-1.2](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12) |

**Why CC BY 4.0 for the vocabularies.** A vocabulary is cited: the attribution
is what keeps the name of whoever built it attached to it, and CC BY asks for
nothing else. It is the licence the modules have carried since their first
publication.

**Why CC0 for the schemas.** A schema is there to be implemented. Anyone may
copy it into their own code without carrying a notice; that costs us nothing
and removes the friction.

**Why EUPL-1.2 for the tools.** `tools/publish_vocab.py` and the tests come
from stratigraph-templates, which is under the EUPL-1.2; they keep its licence.

**Somebody else's vocabularies are referenced, not embedded.** The cards in
`schemes/` with `origin: external` declare a vocabulary (ICCD, Getty AAT,
iDAI.field…) with its own licence and attribution, and say where it is
resolved from; its terms are not copied here. Each card carries the licence
and the attribution of the scheme it declares.

**Where the terms of our modules come from.** Every concept cites its source
(`dct:source`). Definitions are reworded, not transcribed: a published
classification is a fact and is not covered by copyright, its prose is.
