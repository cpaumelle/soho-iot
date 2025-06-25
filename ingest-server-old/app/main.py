from fastapi import FastAPI
from app.routers import uplinks

app = FastAPI()

# Include the uplinks router
app.include_router(uplinks.router)
