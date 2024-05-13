from sqlalchemy.orm import Session
from Persistence import wallet_schemas
from Domain import wallet_models
from datetime import datetime
from sqlalchemy import update, delete, and_


def find_credit(db: Session, user_id: int):
    query_result = db.query(wallet_models.WalletManager).with_entities(
        wallet_models.WalletManager.credit).filter(wallet_models.WalletManager.user_id == user_id).first()
    credit = query_result.__getattribute__("credit")
    return credit


def create_wallet(db: Session, create_wallet: wallet_schemas.WalletCreate):
    user_id = create_wallet.user_id
    credit = create_wallet.credit
    db_create_wallet = wallet_models.WalletManager(
        user_id = user_id,
        credit = credit
    )
    db.add(db_create_wallet)
    db.commit()
    db.refresh(db_create_wallet)
    return db_create_wallet

def update_wallet(db: Session, update_wallet: wallet_schemas.WalletUpdate):
    user_id = update_wallet.user_id
    amount_of_change = update_wallet.amount_of_change
    type = update_wallet.type
    user_credit = db.query(wallet_models.WalletManager).with_entities(
        wallet_models.WalletManager.credit
    ).filter(wallet_models.WalletManager.user_id == user_id).first()
    credit = user_credit.__getattribute__("credit")
    if type == "charge":
        updated_credit = credit + abs(amount_of_change)
        add_to_wallet_history(db = db, user_id = user_id, purchased_items_id = None)
    if type == "withdraw":
        updated_credit = credit - abs(amount_of_change)
        add_to_wallet_history(db = db, user_id = user_id, purchased_items_id = 1)
    db_wallet = db.get(wallet_models.WalletManager,user_id)
    wallet_data = update_wallet.dict(exclude_unset = True)
    wallet_data['credit'] = updated_credit
    for key, value in wallet_data.items():
        setattr(db_wallet, key, value)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def read_wallet(db: Session, user_id: int):
    user_id = user_id
    user_info = db.query(wallet_models.WalletManager).filter(wallet_models.WalletManager.user_id == user_id).first()
    return user_info

def add_to_wallet_history(db: Session, user_id: int, purchased_items_id: int = None): # When the wallet is charged, this value is None.
    user_id = user_id
    purchased_items_id = purchased_items_id
    if purchased_items_id == None:
        transaction_type = "Charge"
    else:
        transaction_type = "Withdraw"
    transaction_date = datetime.today()
    db_add_history = wallet_models.WalletHistory(
        user_id = user_id,
        transaction_type = transaction_type,
        transaction_date = transaction_date,
        purchased_items_id = purchased_items_id
        )
    db.add(db_add_history)
    db.commit()
    db.refresh(db_add_history)
    return db_add_history

def read_wallet_history(db: Session, user_id: int, page_number: int, number_of_records = int):
    user_id = user_id
    page_number = page_number
    number_of_records = number_of_records
    starting_index = (page_number - 1) * number_of_records
    query_result = db.query(wallet_models.WalletHistory).filter(wallet_models.WalletHistory.user_id == user_id).offset(starting_index).limit(number_of_records).all()
    return query_result
    

