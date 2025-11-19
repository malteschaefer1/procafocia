# Project Status (Living Document)

_Last updated: 2025-11-19_

## Purpose
This document tracks what already works in Procafocia and what remains on the roadmap. Update it whenever you add or change functionality so newcomers can instantly see the state of the project.

## What is complete
- **Backend scaffolding**: FastAPI app with structured packages (`backend/app`), configuration, logging, and dependency definitions (`pyproject.toml`).
- **Data persistence**: SQLite database with SQLAlchemy models for products, BOM items, scenarios, mapping rules, and mapping decisions. Defaults (mapping rules + scenarios) are seeded during startup.
- **Product & BOM flows**: REST endpoints for creating products, uploading/downloading BOMs, and storing everything via `ProductRepository`.
- **Mapping system**: Deterministic + fuzzy matching using pluggable providers (ProBas + Boavizta stubs) with full provenance logging, override support, and transparency endpoints (`/mapping/history`, `/mapping/review`). soda4LCA (ÖKOBAUDAT) support validates BOM-supplied UUIDs and caches ILCD metadata for future Brightway imports.
- **Mapping transparency upgrades**: Every mapping now stores all candidate datasets (with placeholder Brightway references) plus inferred life-cycle stages, so reviewers can confirm selections before running PCF.
- **PCF pipeline**: Brightway2-based engine stub, PCF service, and `/pcf/run` API route that ties together products, BOMs, scenarios, recorded mappings, and the selected PCF method.
- **PCF methods catalog**: Registry covering PACT V3 (full metadata) plus ISO/PEF/TfS/Catena-X stubs, exposed via `/pcf/methods`, selectable in the frontend, and passed through to the PCF engine + provenance.
- **PCI pipeline**: Bracquené 2020 implementation with per-material flows, scenario-level circularity parameters, utility factor support, and `/circularity/pci/{product_id}` endpoint.
- **Transparency tooling**: Audit-friendly ResultSet payloads, mapping review CLI (`examples/mapping_review_cli.py`), and frontend buttons for upload/run/review actions.
- **Testing**: Pytest suite covering API happy paths, mapping logic, and circularity math.

## In progress / planned
- **True Brightway2 integration**: Replace the PCF placeholder calculations with actual database imports, demand vector building, and LCIA execution. (Needs access to datasets + more elaborate method profiles.)
- **PACT V3 completion**: Implement DQR scoring, primary-data checks, and real cradle-to-gate LCIA once Brightway results are available.
- **Scenario & method CRUD**: Current scenarios are read-only seeds. Future work should add endpoints + UI to create/edit/delete scenarios and attach custom material parameter sets.
- **User experience**: Frontend is intentionally minimal. Consider building a guided SPA, wizard, or documentation-driven walkthrough so non-technical users can explore mapping decisions and results more intuitively.
- **Advanced mapping features**: Add more data providers, rule management screens, or machine-learning based suggestions. Include audit-bundle downloads (JSON/CSV zip) via the `export_service` stub.
- **Method-specific rules**: Implement PACT data-quality scoring, PEF LCIA setups, Catena-X validation, and ISO/TfS nuances within the PCF engine once real data + guidance are in place.
- **Authentication & multi-project support**: Everything is single-user. If collaboration is needed, add user accounts, project scoping, or workspace concepts.
- **Automation & CI**: Set up linting, type-checking, and GitHub Actions to run tests automatically on pull requests.

## How to contribute
1. Pick an item from the “In progress / planned” list or open a GitHub issue describing your idea.
2. Create a branch, implement the change, and keep this file updated with new accomplishments or remaining gaps.
3. Run `pytest backend/tests` before opening a pull request to ensure the regression suite passes.

Feel free to expand this document with finer-grained tasks, ownership notes, or links to discussion threads as the project grows.
