from fastapi import APIRouter, Depends, HTTPException
from Persistence.database_config import engine, SessionLocal
from sqlalchemy.orm import Session
from Persistence import license_schemas
from Application import license_crud
from Domain.license_models import Base

Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/license",
    tags=["license"],
    dependencies=[Depends(get_db)],
    responses={404: {"description": "Not found"}},
)


'''
@router.post("/api/createprofile/", response_model = license_schemas.License)
def create_profile(profile: license_schemas.LicenseCreate, db: Session = Depends(get_db)) -> any:
    db_service_name = license_crud.valid_service_name(db = db, service_name = profile.service_name)
    if not db_service_name:
        raise HTTPException(status_code = 404, detail = "Service not found!")
    db_user = license_crud.find_user(db = db, user_id = profile.user_id, service_name = profile.service_name)
    if db_user:
        raise HTTPException(status_code = 400, detail = "This user has already registered for " + profile.service_name + " service!")
    return license_crud.create_profile(db = db, profile = profile)'''

@router.put("/api/updatedrone/", response_model = license_schemas.License)
def update_drone(profile: license_schemas.DroneLicenseUpdate, db: Session = Depends(get_db)) -> any:
    user_id = profile.user_id
    service_name = profile.service_name
    db_service_name = license_crud.valid_service_name(db = db, service_name = service_name)
    if db_service_name == False:
        raise HTTPException(status_code = 404, detail = "Service not found!")
    db_user = license_crud.find_user(db = db, user_id = user_id, service_name = profile.service_name)
    if not db_user:
        raise HTTPException(status_code = 404, detail = "This user does not have a license for drone service yet! consider purchasing one.")
        # raise HTTPException(status_code = 400, detail = "This user has already registered for " + profile.service_name + " service!")
    #expiration_date_status = license_crud.find_expiration_date(db = db, user_id = user_id , service_name = service_name)
    #if not expiration_date_status:
        #raise HTTPException(status_code = 400, detail = "Your license is still valid!")
    return license_crud.update_profile(db = db, profile = profile)

@router.post("/api/createdrone/", response_model = license_schemas.Drone)
def create_drone_profile(drone_profile: license_schemas.DroneCreate, db: Session = Depends(get_db)) -> any:
    user_id = drone_profile.user_id

    license_crud.create_profile(db = db, user_id = user_id, service_name = "drone")
    return license_crud.create_drone_profile(db = db, drone_profile = drone_profile)

@router.put("/api/adddronedevice/", response_model = license_schemas.Drone)
def add_drone_device(drone_device: license_schemas.DroneUpdate, db: Session = Depends(get_db)) -> any:
    user_id = drone_device.user_id
    imei = drone_device.imei
    license_validity = license_crud.valid_license(user_id = user_id, imei = imei)
    max_device_number = license_crud.find_max_device_number(db = db, user_id= user_id)
    number_of_stored_devices = license_crud.find_num_of_stored_imeis(db = db, user_id = user_id)
    if number_of_stored_devices > max_device_number:
        raise HTTPException(status_code = 400, detail = "You exceeded the maximum number of IMEI's for which license can be granted!")
    return license_crud.add_device_imei(db = db, drone_device = drone_device)

@router.post("/api/addservice/", response_model = license_schemas.Type)
def add_type(type: license_schemas.TypeCreate, db: Session = Depends(get_db)) -> any:
    return license_crud.add_type(db = db, type = type)
