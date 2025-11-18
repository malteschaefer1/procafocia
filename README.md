# procafocia

Procafocia is an open-source demonstrator that maps Bills of Materials (BOMs) to transparent Product Carbon Footprint (PCF) and Product Circularity Indicator (PCI) results. The goal is to provide research-grade scaffolding with clear interfaces, provenance tracking, and room for future Brightway2 / data source integrations.

## Features
- Domain-centric models (`Product`, `BOMItem`, `Scenario`, `MethodProfile`, `ResultSet`).
- Swappable engine layer: Brightway2 PCF stub + PCI (Bracquene et al. 2020) scaffold.
- Canonical BOM samples (office chair & cordless drill), deterministic + fuzzy mapping rules, and override workflow backed by SQLite.
- FastAPI backend + minimal frontend for BOM upload, mapping review, and calculation triggers.
- Audit bundle exporter and mapping history APIs for transparency.

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
4. **Try the API**: Use `examples/demo_script.py --bom examples/bom_office_chair.csv` or call endpoints via `http://localhost:8000/docs`.

## Tests
```
pytest backend/tests
```

## Data & mapping enhancements
- Canonical BOM schema includes: `product_id`, `bom_item_id`, parent references, mass, `material_family/material_code`, UNSPSC classification, supplier, circularity shares, and optional `lci_dataset_id`.
- Deterministic rule order: BOM-specified dataset → material code → (`material_family` + `UNSPSC prefix`) → supplier override → fuzzy providers (RapidFuzz scoring with configurable thresholds).
- Mapping state stored in SQLite (`procafocia.db`) with `mapping_rules` and `mapping_decisions` tables; history exposed via `/mapping/history/{product_id}` and overrides via `POST /mapping/override`.
- Seed data lives in `backend/app/data/mapping_rules_seed.json` and is loaded automatically on startup; edit or extend this file to reflect new datasets or rule systems.
- Example BOMs for Product A (office chair) and Product B (cordless drill) are in `examples/`, matching the canonical schema for quick experimentation.

## Transparency & TODOs
- All heavy PCF/PCI calculations include TODO markers where Brightway2 calls, EF lookups, or PCI equations must be filled in.
- Mapping logs store provider, dataset, rule id, and reasoning for each BOM item.
- Extend `ScenarioService` + `MethodProfile` to add more methods/boundaries quickly.

## License
MIT License (see `LICENSE`).
