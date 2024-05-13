from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
#from .config import settings
from urllib.parse import quote_plus
'''DATABASE_PORT = "5432"
POSTGRES_USER = "root"
POSTGRES_HOSTNAME = "94.101.189.100"
POSTGRES_PASSWORD = quote_plus(
    "Fidac3_Kime9_Fabu7-Sucan7@Sidup2=Recih6_Masi0-Vety0#Vary5-Kafep4=Cutab5=Gatuf2#Depab2_Kilu8-Pavyv3@Nati8@Botab0#Zudep1@Kode7=Diza4"
)
POSTGRES_DB = "financial"
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{DATABASE_PORT}/{POSTGRES_DB}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL)
'''
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()