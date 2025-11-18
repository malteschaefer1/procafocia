# procafocia

Procafocia is an open-source demonstrator that maps Bills of Materials (BOMs) to transparent Product Carbon Footprint (PCF) and Product Circularity Indicator (PCI) results. The goal is to provide research-grade scaffolding with clear interfaces, provenance tracking, and room for future Brightway2 / data source integrations.

## Features
- Domain-centric models (`Product`, `BOMItem`, `Scenario`, `MethodProfile`, `ResultSet`).
- Swappable engine layer: Brightway2 PCF stub + PCI (Bracquene et al. 2020) scaffold.
- Mapping layer with pluggable LCI providers (ProBas + Boavizta stubs) and confidence logging.
- FastAPI backend + minimal frontend for BOM upload and calculation triggers.
- Audit bundle exporter for transparency.

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
4. **Try the API**: Use `examples/demo_script.py` or call endpoints via `http://localhost:8000/docs`.

## Tests
```
pytest backend/tests
```

## Transparency & TODOs
- All heavy PCF/PCI calculations include TODO markers where Brightway2 calls, EF lookups, or PCI equations must be filled in.
- Mapping logs store provider, dataset, rule id, and reasoning for each BOM item.
- Extend `ScenarioService` + `MethodProfile` to add more methods/boundaries quickly.

## License
MIT License (see `LICENSE`).
