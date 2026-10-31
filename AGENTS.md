# AGENTS.md - Agent Guide for IMDb Crawler

Single canonical guide for autonomous coding agents in this repository; @CLAUDE.md and any future tool-specific guide only point here. Overview, datasets, workflow, setup, Docker and secrets: @README.md (canonical, not duplicated here). Reference DDL: [doc/sql/IMDb-tables.sql](doc/sql/IMDb-tables.sql), read-only unless the user asks for schema-doc edits. Keep `README.md` aligned with every user-facing change; update this file only when agent workflow or safety context changes.

---

## Related repositories (project ecosystem)

One stage of **Agent BBB** (owner `vaugouin`, siblings under `%USERPROFILE%/Code/<repo>`), converging on a shared MariaDB (`T_WC_*`) and ChromaDB. Canonical roster: `%USERPROFILE%/Nestor/projets/t2s-backlog/topics/related-repositories.txt`.

**This repository's role:** Acquisition. Bulk-imports the official IMDb TSV datasets into the `T_WC_IMDB_*` staging tables. Ratings and links are consumed by `tmdb-movie-preprocess` when it builds the `T_WC_T2S_*` read-model.

---

## Code conventions

- **Hungarian notation** (legacy): `str` strings, `lng` integers, `dbl` floats, `arr` lists, `int` boolean-like flags.
- Functions use the `f_` prefix (as in `citizenphil.py`); private helpers `_`.
- SQL naming follows the ecosystem: uppercase snake case, `T_WC_*`, PK `ID_{ENTITY}` or `ID_ROW`, FKs reuse the PK name, `DAT_*` dates, `TIM_*` datetimes, `IS_*`/`DELETED` flags, `DISPLAY_ORDER`, `*_COUNT`, `*_PATH`; preserve the existing mixed index-naming style.
- Keep Markdown, JSON and logs UTF-8 (non-ASCII names); avoid tools that rewrite them with mojibake.

---

**Last Updated**: 2026-10-31
**Current Version**: 1.0.4 

## Backlog (Nestor second-brain)

Backlog: `C:\Users\vaugo\Nestor\projets\t2s-backlog\repos\imdb-crawler.md` (tasks `IMDB-CRAWLER-NNN`, status and priority); dashboard `C:\Users\vaugo\Nestor\projets\t2s-backlog\index.md`. Consult it before implementing. Local paths on Philippe's PC, absent on the VPS and on cloud agents.
