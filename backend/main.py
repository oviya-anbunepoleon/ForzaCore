from fastapi import FastAPI
from routers import problem

app = FastAPI(title="ForzaCore API")

app.include_router(problem.router)

@app.get("/")
def root():
    return {"message": "ForzaCore Backend Running 🚀"}