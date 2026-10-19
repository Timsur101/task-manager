from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None
