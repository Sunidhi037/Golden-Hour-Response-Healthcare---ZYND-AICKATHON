from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import routes
import uvicorn

app = FastAPI(
    title="Golden Hour Response System",
    description="AI-powered emergency response backend",
    version="1.0.0"
)

# CORS (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "message": "Golden Hour System Active 🚑"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
