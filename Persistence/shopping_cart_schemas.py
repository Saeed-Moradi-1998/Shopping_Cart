from pydantic import BaseModel
from datetime import date


class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    pass
    
    class Config:
        orm_mode = True

class CartBase(BaseModel):
    user_id: int

class CartCreate(CartBase):
    item_id: str
    item_count: int

class CartUpdate(CartBase):
    item_id: str
    item_count: int
    
class CartRemove(CartBase):
    pass

class Cart(CartBase):
    user_id: int
    creation_date: date
    total_cost: float
    payment_status: bool
    items_with_price: dict # As pydantic doesn't support JSON, we cannot add this
    #varialb to this class as we'll be prompted to an error while calling the create_cart function.

    class Config:
        orm_mode = True