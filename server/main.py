from fastapi import FastAPI
from server.api.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {"status": "Server is running"}
