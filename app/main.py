from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.exceptions import CustomExceptionA, CustomExceptionB
from app.database import engine, Base
from app.routers import products, users
import logging

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Control Work #4 API")

# Подключаем роутеры
app.include_router(products.router)
app.include_router(users.router)

# Задание 10.1 - обработчики пользовательских исключений
@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": "CUSTOM_A", "message": exc.detail}
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": "CUSTOM_B", "message": exc.detail}
    )

# Задание 10.2 - обработчик ошибок валидации Pydantic
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": exc.errors()
        }
    )

# Пример конечных точек с пользовательскими исключениями (Задание 10.1)
@app.get("/test-exception-a")
async def test_exception_a(trigger: bool = True):
    if trigger:
        raise CustomExceptionA("Условие не выполнено")
    return {"message": "OK"}

@app.get("/test-exception-b/{resource_id}")
async def test_exception_b(resource_id: int):
    if resource_id != 42:
        raise CustomExceptionB(f"Ресурс с id={resource_id} не найден")
    return {"message": "Ресурс найден", "id": resource_id}

# Дополнительная конечная точка для проверки описания ошибок
@app.get("/")
async def root():
    return {"message": "API работает", "endpoints": ["/test-exception-a", "/test-exception-b/{id}", "/products", "/users"]}