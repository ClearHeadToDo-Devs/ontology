# ClearHead Ontology

**Current**: V5 (`5.0.0-draft`), on CCO v2.2 and IAO. **Legacy**: v4, still emitted by Core and the CLI.

What ClearHead's data means, stated in standard terms. V5 defines no terms of its own: objectives and plans are CCO, an action is IAO's action specification, and conditions, status, priority and records are CCO patterns. This repository holds the alignment, examples that use it, and checks that prove it answers the questions it must.

- **[docs/domain.md](docs/domain.md)**: the domain in plain words, its competency questions, and the standard term for each part.
- **[docs/DECISIONS.md](docs/DECISIONS.md)**: the choices behind it, with alternatives rejected.

How the data is shaped (JSON schemas, SHACL shapes, the JSON-LD context) belongs to the [specifications](https://github.com/ClearHeadToDo-Devs/specifications), not here (platform Decision 42).

## Layout

| Path | What |
| --- | --- |
| `v5/clearhead.ttl` | The ontology header: imports, no terms. |
| `v5/imports/` | CCO v2.2 and an IAO module, pinned by checksum. |
| `v5/examples/` | Real plans written in the standard terms. |
| `v5/queries/` | One `robot query` per competency question. |
| `v5/verify/` | Must-never-happen checks (every action belongs to a plan, every plan names an objective). |

## Testing

Needs [ROBOT](https://robot.obolibrary.org) and Java.

```bash
make -C v5 test     # merge, reason with HermiT, verify, answer the competency questions
make -C v5 imports  # re-fetch the pinned CCO and IAO; fails if the bytes changed
```

Answers land in `v5/build/*.csv`.

## Legacy v4

`v4/`, `examples/v4/`, `queries/v4/`, `tests/` (pytest + pySHACL) and `V4_DESIGN.md` describe the v4 vocabulary (`https://clearhead.us/vocab/actions/v4#`), which minted its own terms (`actions:Action`, `actions:Charter`, `inServiceOf`). Core and the CLI still project to it, and `site/` still hosts it at clearhead.us (see [DEPLOYMENT.md](DEPLOYMENT.md)). It is kept until the implementations move to V5, then removed.

## License

See [LICENSE](./LICENSE).
