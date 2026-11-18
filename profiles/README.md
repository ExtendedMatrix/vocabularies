# EM Profiles — moved

**The specification of the EM Profiles lives in
[ExtendedMatrix/em-profiles](https://github.com/ExtendedMatrix/em-profiles)
since version 0.2 (18 November 2026)**, with its schemas, its examples, the
community packages and the checks of its pull requests. In the interface of
the EM tools a profile is a *community package*.

This folder keeps **version 0.1, frozen**, unchanged, for whoever cites it:

| | |
|---|---|
| [`SPEC.md`](SPEC.md) | EM Profiles 0.1, Editor's Draft, 25 October 2026 |
| [`profile.v0.1.schema.json`](profile.v0.1.schema.json) | its schema (also in em-profiles/schemas, byte for byte) |
| [`core-types.json`](core-types.json) | the core types as they were on 25 October 2026 (em-profiles has the current list) |
| [`example-toolmarks/`](example-toolmarks/) | its example (also in em-profiles/examples, unchanged) |

A 0.1 manifest is still read by every 0.2 tool (`s3dgraphy.profiles`), and
validated by the same validator (`python -m s3dgraphy.extensions validate`).
New profiles are proposed in em-profiles, not here; a vocabulary several
communities share is still proposed here, as a module.
