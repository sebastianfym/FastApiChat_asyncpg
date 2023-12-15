from sqlalchemy import Column, Integer, String

from src.database.db import Base
from src.schemas.message import MessagesSchema


class MessagesModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message = Column(String)

    def to_read_model(self) -> MessagesSchema:
        return MessagesSchema(
            message=self.message
        )

