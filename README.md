# SATELLITE-BASED WATER QUALITY & CONTAMINATION INTELLIGENCE

**A decision-support platform for prioritizing ground-level water quality investigations using satellite-derived spectral anomaly detection.**

---

## 1. Project Overview
This platform provides an end-to-end geospatial intelligence pipeline. It retrieves multispectral satellite imagery (Sentinel-2), processes it to detect water bodies, extracts spectral indicators (NDTI, NDCI, Suspended Sediment, FAI), compares them against historical seasonal baselines, and flags potential anomalies. It ranks these anomalies with an Evidence Fusion engine and feeds them into an operational Priority Queue.

## 2. Problem Statement
Water resources are vast and difficult to monitor continuously using only field sensors and manual sampling. Environmental authorities need a way to **prioritize** where to deploy their limited ground teams. This system bridges the gap by using satellite-observable anomalies to highlight areas that require immediate field and laboratory validation.

## 3. Architecture
```
DATA SOURCES (Google Earth Engine) -> PREPROCESSING & WATER DETECTION -> 
SPECTRAL ENGINE -> HISTORICAL BASELINE -> ANOMALY ENGINE -> 
EVIDENCE FUSION -> EXPLAINABILITY -> PRIORITY QUEUE -> 
REPORT GENERATION -> GROUND/LAB VALIDATION
```
*   **Frontend**: React (Vite), TypeScript, Tailwind CSS, Leaflet.
*   **Backend**: Python, FastAPI, NumPy, Pandas, scikit-learn.
*   **Data**: JSON-based flat-file persistence (for hackathon MVP) replacing heavy PostgreSQL.
*   **Geospatial**: Google Earth Engine (GEE).

## 4. Technology Stack
*   **Frontend**: React 18, React-Leaflet, Recharts, Tailwind CSS.
*   **Backend**: FastAPI, Pydantic, Uvicorn, pytest.
*   **Geospatial Processing**: Google Earth Engine Python API (`earthengine-api`).
*   **PDF Generation**: ReportLab.
*   **Machine Learning**: `scikit-learn` (Isolation Forest), `scipy` (MAD).

## 5. Folder Structure
```
├── backend/
│   ├── app/
│   │   ├── api/routes/           # FastAPI routers
│   │   ├── database/             # JSON repositories
│   │   ├── geospatial/           # GEE integration and remote sensing
│   │   ├── intelligence/         # Anomaly, Baseline, Fusion engines
│   │   ├── reports/              # PDF Generation
│   │   ├── schemas/              # Pydantic models
│   │   └── services/             # Orchestration logic
│   ├── data/                     # Persistent JSON stores & PDFs
│   ├── tests/                    # Pytest suite
│   ├── main.py                   # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                  # Router
│   │   ├── components/           # UI Components (Dashboard, Map, Queue)
│   │   ├── data/                 # Static Water Bodies
│   │   ├── pages/                # Views (Dashboard, Queue, Validation)
│   │   ├── services/             # API client & Zustand stores
│   │   └── types/                # TypeScript definitions
│   └── package.json
└── README.md
```

## 6. Setup Instructions
Requires Python 3.9+ and Node.js 18+.
Clone the repository and prepare the environments.

## 7. Environment Variables
Copy `backend/.env.example` to `backend/.env` and update values.
**Do not commit the `.env` file.**

## 8. GEE Setup
1. Create a Google Cloud Project and enable the Earth Engine API.
2. Create a Service Account and download the JSON key.
3. Set `GEE_CREDENTIALS_FILE=/path/to/key.json`.
4. Ensure the service account is registered for Earth Engine access.

## 9. Database Setup
This hackathon MVP uses a robust flat-file JSON storage layer located in `backend/data/`. No external PostgreSQL database setup is required for local testing.

## 10. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run at `http://localhost:5173`.

## 11. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 12. Demo Mode
If `GEE_ENABLED=false` in your `.env` file, the backend will return deterministic, scientifically realistic mock data. This allows for end-to-end UI testing and demonstration without Google Cloud credentials. All synthetic data is clearly marked as **DEMO DATA**.

## 13. Live Mode
Set `GEE_ENABLED=true` and provide valid GEE credentials. The system will retrieve real Sentinel-2 data, generate live water masks, and perform actual statistical anomaly detection.

## 14. API Overview
Key routes under `http://localhost:8000`:
*   `GET /api/gee/health` - Earth Engine connection check.
*   `POST /api/analysis/*` - Satellite processing pipeline.
*   `GET /api/priority-queue` - Alert management.
*   `POST /api/reports/generate` - PDF creation.
*   `POST /api/validation/samples` - Ground truth logging.

## 15. Scientific Methodology
The system calculates Median Absolute Deviation (MAD) for spectral indicators against a 3-year seasonal baseline. Evidence fusion calculates a deterministic 0-100 Priority Score based on the magnitude of deviation, multi-indicator agreement, and data quality.
*   **Disclaimer**: The platform identifies satellite-observable anomalies. It does NOT independently confirm pollution or contamination.

## 16. Report Generation
The system generates formatted PDF reports using `reportlab`. They include metadata, indicator scores, historical comparisons, and explainable AI summaries.

## 17. Field/Lab Validation
Operators can register field samples and attach laboratory results (e.g., Turbidity in NTU). The system runs a transparent rule engine to determine if the lab result `SUPPORTS` the satellite anomaly, strictly ensuring satellite spectral signals are not misrepresented as direct contamination values.

## 18. Testing
```bash
cd backend
python -m pytest tests/ -v
```
Provides 80/80 passing tests covering unit logic, intelligence engines, PDF generation, and validation pipelines.

## 19. Deployment
*   **Frontend**: Build with `npm run build` and host statically (e.g., Vercel, Netlify, Cloud Storage).
*   **Backend**: Containerize using Docker and deploy to Cloud Run, ECS, or App Service. 

## 20. Limitations
*   Satellite indicators (NDTI, NDCI) are **proxies** for water quality, not direct measurements.
*   Cloud cover and atmospheric haze can reduce data availability.
*   Sentinel-2 resolution (10m/20m) limits detection in very narrow rivers or streams.
*   Isolation Forest anomaly detection requires sufficient historical baseline data to avoid false positives.

---
*Developed for HackRonyx 2026*
