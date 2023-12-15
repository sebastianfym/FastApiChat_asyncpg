from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.database import Base
from src.schemas.users import UserSchema


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    tokens = relationship("Token", back_populates="user")

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            name=self.username
        )
