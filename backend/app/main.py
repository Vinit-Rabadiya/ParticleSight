from fastapi import FastAPI

app = FastAPI(title="CERNSight API")

@app.get("/")
async def root():
    return {"message": "Welcome to the CERNSight API!",
            "status":"online",
            "system":"CERNSight"}