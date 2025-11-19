# procafocia

Procafocia is an open-source demonstrator that maps Bills of Materials (BOMs) to transparent Product Carbon Footprint (PCF) and Product Circularity Indicator (PCI) results. The goal is to provide research-grade scaffolding with clear interfaces, provenance tracking, and room for future Brightway2 / data source integrations.

## New to coding? Start here
This project is intentionally approachable. If you have never touched GitHub or Python before, the key ideas are:

1. **What the tool does** – You provide a simple table (a BOM) that lists each part of a product. The backend maps every part to example environmental datasets, then calculates both carbon footprint (PCF) and circularity (PCI). All mapping decisions are stored so you can inspect them before trusting the numbers.
2. **How files are organized** – Everything that powers the server sits in the `backend/` folder (written in Python). A tiny user interface lives in `frontend/`. Sample data and helper scripts live in `examples/`. The rest of the files describe dependencies or optional container setups.
3. **How to run it locally**
   - Install Python 3.11 or later.
   - Open a terminal, run the commands in the “Getting started” section below (create virtual environment, install dependencies, start the FastAPI server).
   - Open another terminal and serve the frontend directory or open `frontend/index.html` directly in your browser.
   - Use the UI buttons (or the API) to create a product, upload `examples/bom_office_chair.csv`, review mappings, and trigger calculations.
4. **Inspecting results** – After a BOM is uploaded, visit `http://localhost:8000/docs` to try endpoints such as `/mapping/review/{product_id}`, `/pcf/run`, or `/circularity/pci/{product_id}`. The frontend mirrors these actions with a friendlier surface.
5. **Where to contribute** – If you want to help, most of the future work is noted in `STATUS.md`. Pick an open item, create an issue or pull request, and reference the file/section you updated.

No special hardware or paid services are required. The code sticks to plain Python, FastAPI, and SQLite so you can explore and extend it without needing prior experience with large frameworks.

## Features
- Domain-centric models (`Product`, `BOMItem`, `Scenario`, `MethodProfile`, `ResultSet`) persisted in SQLite for reproducibility and provenance.
- Swappable engine layer: Brightway2 PCF stub + PCI (Bracquené et al. 2020) flows with full linear-reference and per-material breakdowns.
- Canonical BOM samples, deterministic + fuzzy mapping rules with overrides, plus a mapping-review flow (API/CLI/UI) to inspect candidates before PCF/PCI runs.
- FastAPI backend + minimal frontend for BOM upload, mapping review, and calculation triggers.
- Audit bundle exporter and mapping history APIs for transparency.
- PCF method catalog (PACT V3 + ISO/PEF/TfS/Catena-X stubs) exposed via `/pcf/methods`, selectable in the frontend, and threaded through every PCF calculation with provenance.

## Repository layout
```
backend/        # FastAPI app, services, engines, providers, tests
frontend/       # Simple HTML/JS UI
infra/          # Docker + infra helpers
examples/       # Sample BOM & script
```

## Getting started
1. **Install dependencies**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e '.[dev]'
   ```
2. **Run backend**
   ```bash
   uvicorn backend.app.main:app --reload
   ```
3. **Open frontend**: Serve `frontend/` (e.g., `python -m http.server 8080 -d frontend`) and ensure the backend is on `http://localhost:8000`.
4. **Try the API**: Use `examples/demo_script.py --bom examples/bom_office_chair.csv` or call endpoints via `http://localhost:8000/docs` (e.g., `GET /circularity/pci/{product_id}`, `GET /mapping/review/{product_id}`, `GET /pcf/methods`).

## Tests
```
pytest backend/tests
```

## Data & mapping enhancements
- Canonical BOM schema includes: `product_id`, `bom_item_id`, parent references, mass, `material_family/material_code`, UNSPSC classification, supplier, circularity shares, and optional `lci_dataset_id`.
- Deterministic rule order: BOM-specified dataset → material code → (`material_family` + `UNSPSC prefix`) → supplier override → fuzzy providers (RapidFuzz scoring with configurable thresholds).
- Mapping state stored in SQLite (`procafocia.db`) with `mapping_rules` and `mapping_decisions` tables; history exposed via `/mapping/history/{product_id}` and overrides via `POST /mapping/override`.
- Mapping review flow available via `/mapping/review/{product_id}` (also wired into the frontend button and `examples/mapping_review_cli.py`).
- Seed data lives in `backend/app/data/mapping_rules_seed.json` and is loaded automatically on startup; edit or extend this file to reflect new datasets or rule systems.
- Example BOMs for Product A (office chair) and Product B (cordless drill) are in `examples/`, matching the canonical schema for quick experimentation.
- Scenarios now store a `pcf_method_id` (defaulting to `PACT_V3`) so every PCF run references a specific methodology; swap it via `/pcf/methods` + the frontend dropdown before triggering `/pcf/run`.

## Transparency & TODOs
- All heavy PCF/PCI calculations include TODO markers where Brightway2 calls, EF lookups, or PCI equations must be filled in.
- Mapping logs store provider, dataset, rule id, and reasoning for each BOM item.
- Extend `ScenarioService` + `MethodProfile` to add more methods/boundaries quickly.

## License
MIT License (see `LICENSE`).
