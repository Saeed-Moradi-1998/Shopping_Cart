from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from Persistence.database_config import engine, SessionLocal
from sqlalchemy.orm import Session
from Persistence import wallet_schemas
from Application import wallet_crud
from Domain.license_models import Base

Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/wallet",
    tags=["wallet"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)

@router.post("/api/walletmanager/", response_model = wallet_schemas.Wallet) 
def create_wallet(create_wallet: wallet_schemas.WalletCreate, db: Session = Depends(get_db)) -> any:
    # This is just for creating the wallet. 
    # As any usre should have a wallet from the beginning, a wallet is created once the user creates a profile.
    return wallet_crud.create_wallet(db = db, create_wallet = create_wallet)
    

@router.put("/api/walletupdate/", response_model = wallet_schemas.Wallet)
def update_wallet(update_wallet: wallet_schemas.WalletUpdate, db: Session = Depends(get_db)) -> any:
    user_id = update_wallet.user_id
    credit = wallet_crud.find_credit(db = db, user_id = user_id)
    amount_of_change = update_wallet.amount_of_change
    type = update_wallet.type
    if type == False and amount_of_change > credit:
        response = RedirectResponse(url = "/api/paymentportal") # If the wallet cannot affor the cost of selected items,
        # the user will be redirected to the payment portal through which they can charge their wallet.
        #raise HTTPException(status_code = 400, detail = "You don't have enough credit to purchase the items! Consider charging your wallet.")
    else:
        return wallet_crud.update_wallet(db = db, update_wallet = update_wallet)
    

@router.get("/api/walletread/{user_id}", response_model = wallet_schemas.Wallet)
def read_wallet(user_id: int, db: Session = Depends(get_db)) -> any:
    return wallet_crud.read_wallet(db = db, user_id = user_id)


@router.post("/api/wallethistory/", response_model = wallet_schemas.HistoryWallet)
def create_wallet_record(wallet_create_history: wallet_schemas.HistoryWalletCreate, db: Session = Depends(get_db)) -> any:
    user_id = wallet_create_history.user_id
    purchased_items_id = wallet_create_history.purchased_items_id
    return wallet_crud.add_to_wallet_history(db = db, user_id = user_id, purchased_items_id = purchased_items_id)
    
@router.get("/api/wallethistory/{user_id}/{page_number}/{number_of_records}", response_model = wallet_schemas.HistoryWallet)
def read_wallet_record(user_id: int, page_number: int, number_of_records: int, db: Session = Depends(get_db)) -> any:
    return wallet_crud.read_wallet_history(db = db, user_id = user_id, page_number = page_number, number_of_records = number_of_records)

