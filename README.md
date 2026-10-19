# task-manager-api

Простое REST API для управления задачами. Сделал как пет-проект чтобы разобраться с FastAPI и JWT авторизацией.

## Что умеет

- регистрация и логин пользователей
- JWT токены для авторизации
- CRUD для задач (создать, получить список, обновить, удалить)
- каждый видит только свои задачи

## Стек

- FastAPI
- PostgreSQL + SQLAlchemy
- JWT (python-jose)
- Docker

## Настройка

скопируй .env.example в .env и впиши ключ

```bash
cp .env.example .env    # на Windows: copy .env.example .env
```

## Запуск через Docker

```bash
git clone https://github.com/Timsur101/task-manager.git
cd task-manager

docker-compose up --build
```

Swagger документация: http://localhost:8000/docs

## Запуск локально

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

По умолчанию используется SQLite, так что PostgreSQL не нужен для локальной разработки.

## Эндпоинты

```
POST /register        - регистрация
POST /login           - получить токен

GET    /tasks         - список задач
POST   /tasks         - создать задачу
PATCH  /tasks/{id}    - обновить задачу
DELETE /tasks/{id}    - удалить задачу
```

Для задач нужен заголовок `Authorization: Bearer <token>`
