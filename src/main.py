import datetime as dt
from fastapi import FastAPI, HTTPException, Query
from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting, GetWeatherRequest
from models import *

app = FastAPI()


@app.post('/cities/', summary='Create City', description='Создание города по его названию', tags=['cities'],
          response_model=CityModel)
def create_city(city: RegisterCityRequest):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    city_dict = City(**city.dict())
    check = CheckCityExisting()
    if not check.check_existing(city_dict.name):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city_dict.name.capitalize()).first()
    if city_object is None:
        city_object = City(name=city_dict.name.capitalize())
        s = Session()
        s.add(city_object)
        s.commit()

    return CityModel.from_orm(city_object)


@app.get('/cities/', description='Список городов с погодой', summary='Get Cities', tags=['cities'])
def cities_list(q: str = Query(description="Название города", default=None)):
    if q is None:
        cities = Session().query(City).all()
        return [{'id': city.id, 'name': city.name, 'weather': city.weather} for city in cities]
    else:
        city = Session().query(City).filter(City.name == q.capitalize()).first()
        if city is None:
            raise HTTPException(status_code=404, detail='Города с таким названием в базе нет')
        return {'id': city.id, 'name': city.name, 'weather': city.weather}


@app.get('/users/', summary='Get Users',
         description='Получение списка пользователей с возможностью фильтрации по возрасту', tags=['users'])
def users_list(min_age: int = Query(description="Минимальный возраст пользователей", default=1),
               max_age: int = Query(description="Максимальный возраст пользователей", default=999)):
    users = Session().query(User).filter(User.age >= min_age, User.age <= max_age)
    return [{
        'id': user.id,
        'name': user.name,
        'surname': user.surname,
        'age': user.age,
    } for user in users]


@app.post('/users/', description='Регистрация пользователя', summary='CreateUser', tags=['users'],
          response_model=UserModel)
def register_user(user: RegisterUserRequest):
    user_object = User(**user.dict())
    s = Session()
    s.add(user_object)
    s.commit()

    return UserModel.from_orm(user_object)


@app.get('/picnics/', description='Получить список пикников с участниками', summary='All Picnics', tags=['picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    picnics = Session().query(Picnic)
    if datetime is not None:
        picnics = picnics.filter(Picnic.time == datetime)
    if not past:
        picnics = picnics.filter(Picnic.time >= dt.datetime.now())

    return [{
        'id': pic.id,
        'city': Session().query(City).filter(City.id == pic.city_id).first().name,
        'time': pic.time,
        'users': [pr.user for pr in Session().query(PicnicRegistration).filter(PicnicRegistration.picnic_id == pic.id)],
    } for pic in picnics]


@app.post('/picnics/', description='Создать пикник', summary='Picnic Add', tags=['picnic'], response_model=PicnicModel)
def picnic_add(p: AddPicnicRequest):

    if Session().query(City).filter(City.id == p.city_id).first() is None:
        raise HTTPException(status_code=400, detail='Города с таким id не найдено')
    picnic = Picnic(**p.dict())
    s = Session()
    s.add(picnic)
    s.commit()

    return {
        'id': picnic.id,
        'city': Session().query(City).filter(City.id == picnic.city_id).first().name,
        'time': picnic.time,
    }


@app.post('/picnics/registration/', description='Регистрация пользователя на пикник',
          summary='Picnic Registration', tags=['picnic'])
def register_to_picnic(pic_reg: PicnicRegistrationRequest):
    user = Session().query(User).filter(User.id == pic_reg.user_id).first()
    picnic = Session().query(Picnic).filter(Picnic.id == pic_reg.picnic_id).first()
    picnic_reg = PicnicRegistration(user_id=pic_reg.user_id, picnic_id=pic_reg.picnic_id)
    s = Session()
    s.add(picnic_reg)
    s.commit()

    return {
        'id': picnic_reg.id,
        'user_id': user.id,
        'user_name': user.name,
        'user_surname': user.surname,
        'picnic_date': picnic.time,
    }
