from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException
# Создание движка базы данных
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL)

# Создание базового класса для объявления моделей
Base = declarative_base()

# Определение модели User
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    sex = Column(String)
    nationality = Column(String)
    age = Column(Integer)
    email = Column(String)

# Создание таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создание сессии с привязкой к движку
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Создание и добавление объекта в базу данных
#Person5 = User(name="Урамов Тимофей Леонидович", sex="M", nationality="Russian", age=22, email="<EMAIL>")
#db.add(Person5)
#db.commit()
#print("Количество записей в таблице users:", db.query(User).count())
