import uvicorn
from fastapi import FastAPI
from auth_routes import router as auth_route
from fastapi_jwt_auth import AuthJWT
from schemas import Settings
from order_routes import router as order_route
from product_routes import router as product_route
app = FastAPI()
app.include_router(auth_route)
app.include_router(order_route)
app.include_router(product_route)

@AuthJWT.load_config
def get_config():
    return Settings()

@app.get("/")
async def root():
    return  {
        "message":"Fastapi is working!"
    }

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)