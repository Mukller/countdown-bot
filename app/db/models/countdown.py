from sqlalchemy import BigInteger, String, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from app.db.base import Base


class Countdown(Base):
    __tablename__ = "countdowns"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    repeat_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="none"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )

    def __repr__(self):
        return f"<Countdown {self.title}>"
