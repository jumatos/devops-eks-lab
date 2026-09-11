from fastapi import FastAPI

app = FastAPI(
    title="Task API",
    description="Task management API for the DevOps EKS lab.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}