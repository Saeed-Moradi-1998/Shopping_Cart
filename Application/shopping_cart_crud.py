from sqlalchemy.orm import Session
from sqlalchemy import update, delete, and_
from datetime import date
from Persistence import shopping_cart_schemas
from Domain import shopping_cart_models, wallet_models
import json

def find_user(db: Session, user_id: int):
    query_result = db.query(shopping_cart_models.ShoppingCartManager).filter(shopping_cart_models.ShoppingCartManager.user_id == user_id).first()
    return query_result

def find_product(db: Session, product_id: str):
    query_result = db.query(shopping_cart_models.Products).filter(
        shopping_cart_models.Products.product_id == product_id).first()
    return query_result

def find_item_in_cart(db: Session, user_id: int, item_id: str):
    query_result = db.query(shopping_cart_models.ShoppingCartManager).with_entities(
        shopping_cart_models.ShoppingCartManager.items_with_price).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first()
    items_in_json = query_result.__getattribute__("items_with_price")
    items_in_dict = json.loads(items_in_json)
    for key in items_in_dict:
        if items_in_dict[key]['item_name'] == item_id:
            return True
    return False

def create_cart(db: Session, cart: shopping_cart_schemas.CartCreate):
    user_id = cart.user_id
    today = date.today()
    creation_date = today
    item_id = cart.item_id
    item_data = find_product(db = db, product_id = item_id)
    item_price = item_data.__getattribute__("product_price")
    item_count = cart.item_count
    # When a cart is first created, it is not paid.
    # As a result, it is stored with its default value as False
    #total_cost = total_cost + cart.items_with_price['price']
    payment_status = False
    items = {1: dict(item_id = item_id, item_price = item_price, item_count = item_count)}
    items_in_json = json.dumps(items, indent = 2)
    db_create_cart = shopping_cart_models.ShoppingCartManager(
    user_id = user_id,
    creation_date = creation_date,
    total_cost = item_price * item_count,
    payment_status = payment_status,
    items_with_price = items_in_json
    )
    db.add(db_create_cart)
    db.commit()
    db.refresh(db_create_cart)
    return db_create_cart


def add_item_to_cart(db: Session, item_add: shopping_cart_schemas.CartUpdate):
    user_id = item_add.user_id
    item_id = item_add.item_id
    item_data = find_product(db = db, product_id = item_id)
    item_price = item_data.__getattribute__("product_price")
    item_count = item_add.item_count
    items = db.query(shopping_cart_models.ShoppingCartManager).with_entities(
        shopping_cart_models.ShoppingCartManager.items_with_price
    ).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first()
    total_cost = db.query(shopping_cart_models.ShoppingCartManager).with_entities(
        shopping_cart_models.ShoppingCartManager.total_cost
    ).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first()  
    index = len(items) + 1
    total_cost = total_cost.__getattribute__("total_cost")
    items = items.__getattribute__("items_with_price")
    items_in_dict = json.loads(items)
    new_item = dict(item_name = item_id, item_price = item_price, item_count = item_count)
    flag = False
    for key in items_in_dict:
        if items_in_dict[key]["item_name"] == item_id:
            key_index = key
            flag = True
    if flag == True:
        items_in_dict[key_index]["item_count"] += abs(item_count)
    else:
        items_in_dict[index] = new_item

    items_in_json = json.dumps(items_in_dict, indent = 2)
    db_cart = db.get(shopping_cart_models.ShoppingCartManager, user_id)
    cart_data = item_add.dict(exclude_unset = True)
    cart_data['total_cost'] = total_cost + abs(item_price * item_count)
    cart_data['items_with_price'] = items_in_json
    for key, value in  cart_data.items():
        setattr(db_cart, key, value)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def add_product(db: Session, product: shopping_cart_schemas.ProductCreate):
    product_name = product.name
    product_price = product.price
    db_add_product = shopping_cart_models.Products(
        product_name = product_name,
        product_price = product_price,
    )
    db.add(db_add_product)
    db.commit()
    db.refresh(db_add_product)
    return db_add_product

def remove_item(db: Session, item_remove: shopping_cart_schemas.CartUpdate):
    user_id = item_remove.user_id
    item_name = item_remove.name
    item_data = find_product(db = db, product_name = item_name)
    item_price = item_data.__getattribute__("product_price")
    item_count = item_remove.count
    items = db.query(shopping_cart_models.ShoppingCartManager).with_entities(
        shopping_cart_models.ShoppingCartManager.items_with_price
    ).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first()
    total_cost = db.query(shopping_cart_models.ShoppingCartManager).with_entities(
        shopping_cart_models.ShoppingCartManager.total_cost
    ).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first() 
    total_cost = total_cost.__getattribute__("total_cost")
    items = items.__getattribute__("items_with_price")
    items_in_dict = json.loads(items)
    flag = 0
    for key in items_in_dict:
        if items_in_dict[key]["item_name"] == item_name:
            if items_in_dict[key]["item_count"] <= item_count:
                item_count = items_in_dict[key]["item_count"] # To make sure the total cost would be adjusted correctly. 
                key_index = key
                flag = 1
            else:
                items_in_dict[key]["item_count"] -= abs(item_count)
    if flag == 1:
        del items_in_dict[key_index]
    
    items_in_json = json.dumps(items_in_dict, indent = 2)
    db_cart = db.get(shopping_cart_models.ShoppingCartManager, user_id)
    cart_data = item_remove.dict(exclude_unset = True)
    cart_data['total_cost'] = total_cost - abs(item_price * item_count)
    cart_data['items_with_price'] = items_in_json
    for key, value in  cart_data.items():
        setattr(db_cart, key, value)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    if len(items_in_dict) == 0:
        remove_cart(db = db, user_id = user_id)
    return db_cart

def remove_cart(db: Session, user_id: int):
    #add_cart_to_history(db = db, user_id = user_id)
    db_user = find_user(db = db, user_id = user_id)
    db_delete = db.delete(db_user)
    db.commit()
    return db_delete

def add_cart_to_history(db: Session, user_id: int):# This function is called when payment is made.
    remove_cart(db = db, user_id = user_id)
    user_info = find_user(db = db, user_id = user_id)
    items_info = user_info.__getattribute__("items_with_price")
    total_cost = user_info.__getattribute__("total_cost")
    db_add_cart_to_history = shopping_cart_models.ShoppingCartHistory(
        user_id = user_id,
        total_cost = total_cost,
        items_info = items_info
    )
    purchased_items_id = db_add_cart_to_history.__getattribute__("id")
    add_cart_to_wallet(db = db, user_id = user_id, purchased_items_id = purchased_items_id)
    db.add(db_add_cart_to_history)
    db.commit()
    db.refresh(db_add_cart_to_history)
    remove_cart(db = db, user_id = user_id)
    return db_add_cart_to_history

def read_from_history(db: Session, user_id: int, page_number: int, number_of_records: int = 5):
    user_id = user_id
    page_number = page_number
    number_of_records = number_of_records
    starting_index = (page_number - 1) * number_of_records
    query_result = db.query(shopping_cart_models.ShoppingCartHistory).filter(
        shopping_cart_models.ShoppingCartHistory.user_id == user_id).offset(starting_index).limit(number_of_records).all()
    return query_result

def add_cart_to_wallet(db: Session, user_id: int, purchased_items_id: int):
    user_id = user_id
    purchased_items_id = purchased_items_id
    transaction_type = "withdrawal"
    transaction_date = date.today()
    db_add_cart_to_wallet = wallet_models.WalletHistory(
        user_id = user_id,
        transaction_type = transaction_type,
        transaction_date = transaction_date,
        purchased_items_id = purchased_items_id
    )
    db.add(db_add_cart_to_wallet)
    db.commit()
    db.refresh(db_add_cart_to_wallet)
    return(db_add_cart_to_wallet)

def read_cart(db: Session, user_id: int):
    cart_information = db.query(shopping_cart_models.ShoppingCartManager).filter(
        shopping_cart_models.ShoppingCartManager.user_id == user_id).first()
    items_in_json = cart_information.__getattribute__("items_with_price")
    items_in_dict = json.loads(items_in_json)
    cart_information['items_with_price'] = items_in_dict
    return cart_information