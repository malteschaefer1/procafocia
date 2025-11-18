# Infrastructure Notes

Use Docker Compose for quick experiments:

```bash
cd infra
docker-compose up --build
```

The backend exposes FastAPI on `http://localhost:8000` and the frontend static helper on `http://localhost:4173`.
