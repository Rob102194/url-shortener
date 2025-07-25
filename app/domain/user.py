from sqlalchemy.orm import Mapped, mapped_column
from app.domain.base import Base
import uuid

class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
