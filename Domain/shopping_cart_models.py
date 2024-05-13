from sqlalchemy import Column, Integer, String, Date, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from Persistence.database_config import Base

class Products(Base):
    __tablename__ = "products"
    product_id = Column(String, primary_key = True, nullable = False)
    product_price = Column(Float, nullable = False)


class ShoppingCartManager(Base):
    __tablename__ = "shopping_cart_manager"
    # By default, each user can only have one shopping cart at a given time,
    # thereby we can set it as primary key. 
    user_id = Column(Integer, primary_key = True, nullable = False)
    creation_date = Column(Date, nullable = False)
    total_cost = Column(Float, default = 0)
    payment_status = Column(Boolean, default = False, nullable = False)
    items_with_price = Column(JSON ,nullable = False)
    
# Once payment for a given shopping cart in made, the record is removed from the table.
# As a result,  we cannot link the two tables together.
class ShoppingCartHistory(Base):
    __tablename__ = "shopping_cart_history"
    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, nullable = False)
    total_cost = Column(Float, nullable = False)
    items_info = Column(JSON, nullable = False)




