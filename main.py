from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
import database
import auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Task Manager")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = auth.verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный токен")
    return user




@app.post("/register", response_model=schemas.UserOut)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email уже занят")
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username уже занят")

    hashed = auth.hash_password(user_data.password)
    user = models.User(username=user_data.username, email=user_data.email, password=hashed)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким email или username уже существует")
    db.refresh(user)
    return user


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.check_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = auth.create_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()
    return tasks


@app.post("/tasks", status_code=201)
def create_task(task_data: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = models.Task(
        title=task_data.title,
        description=task_data.description,
        user_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_data: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.done is not None:
        task.done = task_data.done

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db.delete(task)
    db.commit()
    return {"message": "Удалено"}
