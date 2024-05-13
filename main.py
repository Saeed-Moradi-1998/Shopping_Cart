from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse

from API import license, shopping_cart, wallet
from Persistence import database_config

def get_db():
    db = database_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(dependencies=[Depends(get_db)])


app.include_router(license.router)
app.include_router(shopping_cart.router)
app.include_router(wallet.router)


@app.get("/")
async def root():
    return RedirectResponse("/docs")
