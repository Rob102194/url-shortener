from __future__ import annotations
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.domain.base import Base
from typing import TYPE_CHECKING, Dict, Any
import uuid

if TYPE_CHECKING:
    from app.domain.user import User

class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    short_code: Mapped[str] = mapped_column(unique=True, index=True)
    url: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(
        "User", back_populates="links", default=None
    )
    stats: Mapped["LinkStats"] = relationship(
        "LinkStats", back_populates="link", default=None
    )

class LinkStats(Base):
    __tablename__ = "link_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"))
    link: Mapped["Link"] = relationship(
        "Link", back_populates="stats", default=None
    )
    clicks: Mapped[int] = mapped_column(default=0)
    countries: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default_factory=dict
    )
