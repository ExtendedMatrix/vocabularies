# Contributing

Thank you for wanting to add to the Extended Matrix vocabularies. This page
says what a contribution must carry and how it is reviewed. It is short on
purpose: when something is not covered, open an issue and ask.

## How a change arrives

1. **Open an issue** when you want to propose a new module, a new profile or a
   change in meaning (a concept split, merged or withdrawn). Say what you need
   to record, show an example, and say why no existing vocabulary covers it —
   checked, not assumed: if the term already lives in the Getty AAT, PeriodO or
   a national thesaurus, we align with it instead of restating it.
2. **Send a pull request.** Every pull request is reviewed by at least one
   curator of the module it touches (see `.github/CODEOWNERS`) and must pass
   the tests (`pytest`). Fixing a typo in a label is a pull request too; it
   just needs no issue.
3. **The curator merges**, and whoever publishes runs `tools/publish_vocab.py`
   so that the resolvable copy on the site matches the source.

## What every module carries

A module is a SKOS file in `skos/` and a card in `schemes/`. The card must say:

| key | what |
|---|---|
| `id` | the scheme id, `em-<name>` for the modules EM originates |
| `origin` | `originated` (ours) or `external` (somebody else's, only declared) |
| `uri` | the namespace, `https://w3id.org/extendedmatrix/vocab/<name>/` |
| `version` | [semantic versioning](https://semver.org): see below |
| `lifecycle` | `proposed`, `stable` or `deprecated`: see below |
| `curators` | who answers for the module (GitHub handles or a group) |
| `license` | the licence of the content; `CC BY 4.0` unless there is a reason |
| `attribution` | who made it, and where the terms come from |
| `resolve` | `kind: skos_file` and the `path` of the Turtle file |

`unverified_languages` lists the languages whose labels nobody has verified
yet: they are usable now and marked as drafts on the published page.

`extensible: project` (optional, our modules only) says that a project may add
terms of its own beside ours — `local:<slug>` on its graph, with who and when,
never in our namespace (`em-media-role`). A local term many projects use is
proposed here, with its source.

In the Turtle file the scheme carries `owl:versionInfo` equal to the card's
`version`, `dct:license`, and every concept carries `skos:prefLabel` in at
least the source language, a `skos:definition` and its **source**
(`dct:source`). No term enters without a source. Definitions are written in
our words, not copied from the source: a published classification is a fact,
its prose is somebody's text.

## Versions

- **patch** (`0.1.0 → 0.1.1`): a label corrected, a definition reworded, a
  translation added or verified. No concept changes meaning.
- **minor** (`0.1.0 → 0.2.0`): concepts added; an alignment added.
- **major** (`1.x → 2.0`): a concept removed, split or changed in meaning.
  Concept IRIs are never reused: a withdrawn concept stays in the file with
  `owl:deprecated true` and, where there is one, `dct:isReplacedBy`.

A module stays at `0.x` while it is `proposed`.

## Lifecycle

- **`proposed`** — usable, citable by IRI, but it may still change in
  meaning. Every new module starts here.
- **`stable`** — the curators answer for it; it changes only by the rules
  above. A module becomes stable at `1.0.0`, when the curators ask for it and
  at least one person outside the group that wrote it has reviewed it.
- **`deprecated`** — kept and still resolving, because data cite it; not to be
  used for new data. The card says what replaces it.

## Alignments

An alignment (`alignments/*.yaml`) says `skos:exactMatch`, `closeMatch`,
`broadMatch` or `narrowMatch` between a concept of ours and a concept of
another scheme. Every alignment is `proposed` until a person with standing in
the target vocabulary has checked it; then it becomes `verified` and says
`by:` whom. A match nobody has checked is never served as though it had been.

## Profiles

Community profiles (community packages) are contributed to
[ExtendedMatrix/em-profiles](https://github.com/ExtendedMatrix/em-profiles),
which holds the specification from 0.2 on, its schemas and the packages
(18 November 2026). `profiles/` here keeps version 0.1, frozen, and takes no
new profile. A vocabulary that several communities share is still proposed
here, as a module.

## Licence of contributions

By sending a pull request you agree that your contribution is published under
the licence of the files it touches (see `LICENSING.md`): CC BY 4.0 for
vocabularies and specifications, CC0 1.0 for schemas, EUPL-1.2 for tools.
Your name stays in the attribution and in the history.
