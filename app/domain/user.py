from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.base import Base
import uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.link import Link

class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    links: Mapped[List["Link"]] = relationship(
        "Link", back_populates="user", default_factory=list
    )
