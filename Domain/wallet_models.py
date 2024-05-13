from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from Persistence.database_config import Base

class WalletManager(Base):
    __tablename__ = "wallet_manager"

    user_id = Column(Integer, primary_key = True)
    credit = Column(Integer, default = 0)

class WalletHistory(Base):
    __tablename__ = "wallet_history"

    id = Column(Integer, primary_key= True, autoincrement = True)
    user_id = Column(Integer)
    transaction_type = Column(String)
    transaction_date = Column(DateTime)
    purchased_items_id = Column(Integer, default = None)
    # If a user charges their wallet, this value should be None. 