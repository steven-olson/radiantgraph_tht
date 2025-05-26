from fastapi import FastAPI
from src.rest_api.customer_rest_api import customer_router
from src.rest_api.purchase_rest_api import purchase_router
from src.rest_api.analytics_rest_api import analytics_router
from src.data.database import Base, engine

app = FastAPI()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(customer_router)
app.include_router(purchase_router)
app.include_router(analytics_router)



@app.get("/")
async def ping():
    return {"ping": "pong"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
