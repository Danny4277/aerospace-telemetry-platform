import json
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from app.processor import process_telemetry

UPLOAD_DIR = Path("data/uploads")
RESULT_DIR = Path("data/results")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Aerospace Telemetry Platform",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Aerospace Telemetry Platform"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/telemetry")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file")
    
    job_id = str(uuid4())
    csv_path = UPLOAD_DIR / f"{job_id}.csv"
    contents = await file.read()
    csv_path.write_bytes(contents)
    try:
        summary = process_telemetry(csv_path)

    except ValueError as exc:
        csv_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

    result = {
        "job_id": job_id,
        "status": "completed",
        "summary": summary,
    }

    result_path = RESULT_DIR / f"{job_id}.json"

    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)

    return result

@app.get("/results/{job_id}")
def results(job_id: str):
    path = RESULT_DIR / f"{job_id}.json"

    if not path.exists():
        raise HTTPException(404, "Result not found")

    with open(path) as f:
        return json.load(f)