from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from Domain import license_models
from Persistence import license_schemas
import pytz
import Crypto.Random
from Crypto.Cipher import AES
import base64
from Crypto.Util.Padding import pad
from hashlib import sha256

def valid_service_name(db:Session, service_name: str):
    query_result = db.query(license_models.LicenseType).filter(license_models.LicenseType.service_name == service_name).first()
    return query_result

def find_user(db: Session, user_id: int, service_name: str):
    query_result = db.query(license_models.ManageLicense).filter(
        and_(
        license_models.ManageLicense.user_id == user_id,
        license_models.ManageLicense.service_name == service_name
        )
    ).first()
    return query_result

def find_drone_user(db: Session, user_id: int):
    query_result = db.query(license_models.DroneLicense).filter(license_models.DroneLicense.user_id == user_id)
    return query_result

def find_max_device_number(db: Session, user_id: int):
    query_result = db.query(license_models.DroneLicense).with_entities(
        license_models.DroneLicense.max_device_number
    ).filter(license_models.DroneLicense.user_id == user_id).first()
    max_device_number = query_result.__getattribute__("max_device_number")
    return max_device_number

def find_expiration_date(db: Session, user_id: int, service_name: str):
    #current_date = date.today()
    query_result = db.query(license_models.ManageLicense).with_entities(
        license_models.ManageLicense.expiration_date).filter(
        and_(
        license_models.ManageLicense.user_id == user_id,
        license_models.ManageLicense.service_name == service_name
        )
        ).first()
        #license_models.ManageLicense.expiration_date < current_date
    expiration_date = query_result.__getattribute__("expiration_date")
    return expiration_date

def find_unique_id(db: Session, user_id: int, service_name: str):
    unique_id = db.query(license_models.ManageLicense).with_entities(
        license_models.ManageLicense.unique_id).filter(
        and_(
        license_models.ManageLicense.user_id == user_id,
        license_models.ManageLicense.service_name == service_name
        )
    ).first()
    return unique_id

def find_num_of_stored_imeis(db: Session, user_id: int):
    query_result = db.query(license_models.DroneLicense).with_entities(
        license_models.DroneLicense.imei_list).filter(
        license_models.DroneLicense.user_id == user_id).first()
    imei_list_in_string = str(query_result.__getattribute__("imei_list"))
    imei_list = imei_list_in_string.split("|")
    return len(imei_list)

def valid_license(db: Session, user_id: int, imei: str):
    query_result = db.query(license_models.DroneLicense).with_entities(
        license_models.DroneLicense.imei_list).filter(
        license_models.DroneLicense.user_id == user_id).first()
    imei_list_in_string = str(query_result.__getattribute__("imei_list"))
    imei_list = imei_list_in_string.split("|")
    if imei in imei_list:
        return generate_license(imei = imei)
    else:
        return False
    
def encrypt(plain_text, key_string):
    key = bytearray(sha256(key_string.encode('utf8')).hexdigest().encode('utf8'))[23 : 55]
    raw = pad(plain_text.encode(), AES.block_size)
    iv = Crypto.Random.get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return str(base64.b64encode(iv + cipher.encrypt(raw)))[2 : -1]

def ticks(dt):
    return (dt.replace(tzinfo=pytz.UTC) - datetime(1, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds() * 10000000

def generate_license(imei: str):
            ex_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + relativedelta(weeks=1)
            _license = encrypt(
                    encrypt(
                        str(int(ticks(ex_time))),
                        sha256((imei + "SpaceOmidUAVInterface").encode("utf8")).hexdigest(),
                    ),
                    sha256(("UAVInterfaceLicense").encode("utf8")).hexdigest(),
                ) 
            
            return _license

def create_profile(db: Session, user_id: int, service_name: str):
    user_id = user_id
    service_name = service_name
    today = date.today()
    delta = relativedelta(months = 2)
    expiration_date = today + delta
    db_create_profile = license_models.ManageLicense(
            user_id = user_id, service_name = service_name, expiration_date = expiration_date
            )
    db.add(db_create_profile)
    db.commit()
    db.refresh(db_create_profile)
    #return db_create_profile

def update_profile(db: Session, profile: license_schemas.DroneLicenseUpdate):
    user_id = profile.user_id
    max_device_update = profile.max_device_update
    extension_time = profile.extension_time
    expiration_date = find_expiration_date(db = db, user_id = user_id, service_name = "drone")
    max_device_number = find_max_device_number(user_id = user_id)
    db_profile = db.get(license_models.ManageLicense, find_unique_id(db, user_id, service_name = "drone"))
    profile_data = profile.dict(exclude_unset = True)
    profile_data['expiration_date'] = expiration_date + relativedelta(months = extension_time)
    profile_data['max_device_number'] = max_device_number + max_device_update
    for key,value in profile_data.items():
        setattr(db_profile, key, value)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def create_drone_profile(db: Session, drone_profile: license_schemas.DroneCreate):
   user_id = drone_profile.user_id
   max_device_number = drone_profile.max_device_number
   db_create_drone = license_models.DroneLicense(
            user_id = user_id, max_device_number = max_device_number)
   db.add(db_create_drone)
   db.commit()
   db.refresh(db_create_drone)
   return db_create_drone

def add_device_imei(db: Session, drone_device: license_schemas.DroneUpdate):
    user_id = drone_device.user_id
    imei = drone_device.imei
    db_drone = db.get(license_models.DroneLicense, user_id)
    imei_list_in_string = str(db_drone.__getattribute__("imei_list"))
    imei_list = imei_list_in_string.split("|")
    flag = 0
    if imei in imei_list:
        flag = 1
    if flag == 0:
        if imei_list_in_string == "None":
            imei_list_in_string = imei
            new_list = " | " + imei_list_in_string
        else:
            new_list = imei_list_in_string + " | " + imei
        drone_data = drone_device.dict(exclude_unset = True)
        drone_data['imei_list'] = new_list
        drone_data["user_id"] = user_id
        license_number = generate_license(imei = imei)
        for key, value in drone_data.items():
            setattr(db_drone, key, value)
        db.add(db_drone)
        db.commit()
        db.refresh(db_drone)
    else:
        db_new_drone = db.get(license_models.DroneLicense, user_id)
        drone_data = drone_device.dict(exclude_unset = True)
        drone_data['license_number'] = license_number
        for key, value in drone_data.items():
            setattr(db_new_drone, key, value)
    return db_new_drone

def add_type(db: Session, type: license_schemas.TypeCreate):
   service_name = type.service_name
   db_create_type = license_models.LicenseType(service_name = service_name)
   db.add(db_create_type)
   db.commit()
   db.refresh(db_create_type)
   return db_create_type