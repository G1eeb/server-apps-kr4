from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, constr, EmailStr, conint
from typing import Optional
from itertools import count
from threading import Lock

router = APIRouter(prefix="/users", tags=["users"])

# In-memory хранилище для пользователей (Задание 11.1 и 11.2)
db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()

def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)

# Задание 10.2 - модель Pydantic с валидацией
class UserCreate(BaseModel):
    username: str
    age: conint(gt=18)  # больше 18
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'

class UserResponse(BaseModel):
    id: int
    username: str
    age: int
    email: str
    phone: str

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    user_id = next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)