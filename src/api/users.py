from fastapi import APIRouter
from src.services.users import SQLAlchemyRepository as UserService
from src.schemas.users import UserSchema, UserSchemaAdd


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("")
async def add_user(user: UserSchemaAdd):
    request = """"""
    user_id = await UserService().add_user(user)
    return {"user_id": user_id}


# @router.get("")
# async def get_users(uow: UOWDep):
#     users = await UserService().get_users(uow)
#     return users
#
#
# @router.get("/{id}")
# async def get_user(uow: UOWDep, id: int, user: UserSchema):
#     user = await UserService().get_user(uow, id, user)
#     return user
