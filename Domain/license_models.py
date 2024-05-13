from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from Persistence.database_config import Base


class LicenseType(Base):
    __tablename__ = "license_type" # This attribute specify
    # the name of the table to use in the database.
    service_name = Column(String, primary_key = True)

    #user_manager = relationship("ManageLicense", back_populates = "type")

class ManageLicense(Base):
    __tablename__ = "manage_license"
    unique_id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, nullable = False)
    service_name = Column(String, ForeignKey("license_type.service_name"), nullable = False)
    expiration_date = Column(Date, nullable = False)

    #type = relationship("LicenseType", back_populates = "user_manager")
    #drone = relationship("DroneLicense", back_populates = "user")


class DroneLicense(Base):
    __tablename__ = "drone_license"

    user_id = Column(Integer, primary_key = True, nullable = False)
    max_device_number = Column(Integer, nullable = False)
    imei_list = Column(String, nullable = True)

    #user = relationship("ManageLicense", back_populates = "drone")


