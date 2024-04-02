from typing import List, Optional
import requests
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import requests

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class User(Base):
    '''Описание модели таблицы Users'''
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    sex = Column(String)
    nationality = Column(String)
    age = Column(Integer)
    email = Column(String)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

class UserUpdate(BaseModel):
    '''Класс для определения моделей данных для обновления пользователя'''
    name: str
    email: str

class UserResponse(BaseModel):
    name: str
    email: str
    age: int
    sex: str
    nationality: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/users/by-first-name/{first_name}", response_model=UserResponse)
def read_user_by_first_name(first_name: str):
    """Функция, позволяющая найти информацию о человеке по фамилии"""
    db = SessionLocal()
    user = db.query(User).filter(User.name.ilike(f"{first_name}%")).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    '''Функция, для просмотра всех пользователей'''
    users = db.query(User).offset(skip).limit(limit).all()
    return users

class UserCreate(BaseModel):
    name: str
    email: str

def get_age(name: str):
    '''Получение возраста с помощью agify.io'''
    url = f"https://api.agify.io/?name={name}"
    response = requests.get(url)
    data = response.json()
    age = data.get("age")
    return age

def get_gender(name: str):
    '''Получение пола с помощью genderize.io'''
    url = f"https://api.genderize.io/?name={name}"
    response = requests.get(url)
    data = response.json()
    gender = data.get("gender")
    return gender

def get_nationality(name: str):
    '''Получение национальности с помощью nationalize.io'''
    url = f"https://api.nationalize.io/?name={name}"
    response = requests.get(url)
    data = response.json()
    country = data.get("country")[0]
    nationality = country.get("country_id")
    return nationality

@app.post("/users/")
def create_user(user_data: UserCreate):
    '''Функция, для создания пользователя. Принимает два занчения name, email. Остальные данные генерируются с помощью
    agify.io, genderize.io, nationalize.io'''
    name = user_data.name
    email = user_data.email
    split_name = name.split()

    if len(split_name) >= 2:
        last_name = split_name[0]
        first_name = split_name[1]
        age = get_age(first_name)
        sex = get_gender(first_name)
        nationality = get_nationality(first_name)
    else:
        last_name = ""
        first_name = split_name[0]
        age = 0
        sex = ""
        nationality = ""

    user = User(name=name, email=email, age=age, sex=sex, nationality=nationality)

    session = SessionLocal()
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created successfully", "user": user}

@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    '''Функция для изменения пользователя '''
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    user.name = user_data.name
    user.email = user_data.email
    db.commit()

    return {"message": "User updated successfully", "user": user}







