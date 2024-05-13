from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session
from Domain.shopping_cart_models import Base
from Persistence import shopping_cart_schemas
from Application import shopping_cart_crud
from Persistence.database_config import SessionLocal, engine
from starlette.responses import RedirectResponse

Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/shopping cart",
    tags=["shopping cart"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root():
    response = RedirectResponse(url="/docs")
    return response

@router.post("/api/shoppingcartcreate/", response_model = shopping_cart_schemas.Cart)
def create_cart(cart: shopping_cart_schemas.CartCreate, db: Session = Depends(get_db)) -> any:
    item_name = cart.name
    db_item = shopping_cart_crud.find_product(db = db, product_name = item_name)
    if not db_item:
        raise HTTPException(status_code = 404, detail = "Item not found!")
    user_id = cart.user_id
    db_user = shopping_cart_crud.find_user(db = db, user_id = user_id)
    if not db_user:
        return shopping_cart_crud.create_cart(db = db, cart = cart)
    else:
        return shopping_cart_crud.add_item_to_cart(db = db, item_add
         = cart)


@router.post("/api/productadd/", response_model = shopping_cart_schemas.Product)
def add_product(product: shopping_cart_schemas.ProductCreate, db: Session = Depends(get_db)):
    return shopping_cart_crud.add_product(db = db, product = product)


@router.put("/api/removeitem/", response_model = shopping_cart_schemas.Cart)
def remove_item(item: shopping_cart_schemas.CartUpdate, db: Session = Depends(get_db)):
    user_id = item.user_id
    item_name = item.name
    if shopping_cart_crud.find_item_in_cart(db = db, user_id = user_id, item_name = item_name) == False:
        raise HTTPException(status_code = 404, detail = "This item does not exist in your shopping cart!")
    return shopping_cart_crud.remove_item(db = db, item_remove = item)

@router.delete("/api/removecart/", response_model = shopping_cart_schemas.Cart)
def remove_cart(cart: shopping_cart_schemas.CartRemove, db: Session = Depends(get_db)):
    user_id = cart.user_id
    db_user = shopping_cart_crud.find_user(db = db, user_id = user_id)
    if not db_user:
        raise HTTPException(status_code = 404, detail = "User does not exist!")
    return shopping_cart_crud.remove_cart(db = db, user_id = user_id)