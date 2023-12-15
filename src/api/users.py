from fastapi import APIRouter, HTTPException, Depends, Header
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST

from src.config.config import templates
from src.database.database import add_user, check_user_in_db, get_user
from src.models.users import User
from src.secure.secure import pwd_context, create_jwt_token, get_current_user
from src.schemas.users import UserSchema, UserSchemaAdd, UserSchemaAuth

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/create_user")
async def create_user(user_data: UserSchemaAdd):
    user = await check_user_in_db(user_data.username)
    if user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username'ом уже зарегестрирован"
        )
    else:
        password = pwd_context.hash(user_data.password)
        new_user_id = await add_user(user_data.username, password)
        return {"detail": f"Пользователь создан", "user_id": new_user_id}


@router.get("/")
def get_auth_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/auth")
async def authenticate_user(user_data: UserSchemaAuth):
    user = await get_user(user_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(user_data.password, user['password'])

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    jwt_token = create_jwt_token({"sub": user['username']})
    return {"access_token": jwt_token}


@router.get("/me")
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user


