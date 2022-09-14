from pydantic import BaseModel, validator
from datetime import datetime


class RegisterUserRequest(BaseModel):
    name: str
    surname: str
    age: int


class UserModel(BaseModel):
    id: int
    name: str
    surname: str
    age: int

    class Config:
        orm_mode = True


class RegisterCityRequest(BaseModel):
    name: str


class CityModel(BaseModel):
    id: int
    name: str
    weather: str

    class Config:
        orm_mode = True


class AddPicnicRequest(BaseModel):
    city_id: int
    time: datetime


class PicnicModel(BaseModel):
    id: int
    city: str
    time: datetime

    class Config:
        orm_mode = True


class PicnicRegistrationRequest(BaseModel):
    user_id: int
    picnic_id: int
