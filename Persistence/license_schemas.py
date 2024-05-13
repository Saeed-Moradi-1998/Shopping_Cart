from pydantic import BaseModel
from datetime import date
from pydantic.schema import Optional

class LicenseBase(BaseModel):
    user_id: int

class LicenseCreate(LicenseBase):
    service_name: str

class DroneLicenseUpdate(LicenseBase):
    extension_time: int 
    # Determines for how long the user wished their licenses to be extended.
    max_device_update: int

class License(LicenseBase):
    #unique_id: int
    expiration_date: date
    
    class Config:
        orm_mode = True

class DroneBase(BaseModel):
    user_id: int

class DroneCreate(DroneBase):
    max_device_number: int

class DroneUpdate(DroneBase):
    imei: str

class Drone(DroneBase):
    license_number: Optional[str]
    imei: Optional[str]

    class Config:
        orm_mode = True

class TypeBase(BaseModel):
    service_name: str

class TypeCreate(TypeBase):
    pass

class Type(TypeBase):
    class Config:
        orm_mode = True