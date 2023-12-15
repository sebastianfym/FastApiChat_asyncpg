import asyncio

import uvicorn
from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.api.routers import routers
from src.database.database import create_table, stmt_message_table_create, stmt_user_table_create
from src.secure.secure import JWTBearer


app = FastAPI(
    title='Онлайн чат на FastAPI'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=JWTBearer())

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    for stmt in [stmt_message_table_create, stmt_user_table_create]:
        asyncio.run(create_table(stmt))
    uvicorn.run(app="src.main:app", reload=True)
