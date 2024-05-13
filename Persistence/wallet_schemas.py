from datetime import datetime
from pydantic import BaseModel

class WalletBase(BaseModel):
    user_id: int

class WalletCreate(WalletBase): # In reality, there is no such thing as creating a wallet.
    # Once a user creates profile, a wallet is automatically created.
    credit: int

class WalletUpdate(WalletBase):
    type: str
    amount_of_change: int

class Wallet(WalletBase):
    credit: int

    class Config:
        orm_mode = True

class HistoryWalletBase(BaseModel):
    user_id: int

class HistoryWalletCreate(HistoryWalletBase):
    purchased_items_id: int

class HistoryWalletRead(HistoryWalletBase):
    page_number: int
    number_of_records: int

class HistoryWallet(HistoryWalletBase):
    transaction_type: str
    transaction_date: datetime

    class Config:
        orm_mode = True