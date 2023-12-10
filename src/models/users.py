from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


from src.database.db import Base
from src.schemas.users import UserSchema


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            name=self.username
        )
