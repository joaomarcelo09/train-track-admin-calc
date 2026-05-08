from fastapi import FastAPI
from app.schemas import SimulationRequest, SimulationResponse
from app.simulation.engine import SimulationEngine

app = FastAPI(title="Calc Service", version="1.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/simulate", response_model=SimulationResponse)
async def simulate_energy(request: SimulationRequest):
    """Simulate train energy consumption across track segments."""
    engine = SimulationEngine()
    result = engine.simulate(request)
    return result
