from sqlalchemy import BigInteger, Time, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time, datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    notification_time: Mapped[time] = mapped_column(
        Time, nullable=False, default=time(9, 0, 0)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    def __repr__(self):
        return f"<User {self.telegram_id}>"
