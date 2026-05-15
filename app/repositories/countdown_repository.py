from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Countdown


class CountdownRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, countdown_id: int) -> Countdown | None:
        result = await self.session.execute(
            select(Countdown).where(Countdown.id == countdown_id)
        )
        return result.scalar_one_or_none()

    async def get_user_countdowns(self, user_id: int) -> list[Countdown]:
        result = await self.session.execute(
            select(Countdown).where(Countdown.user_id == user_id)
        )
        return result.scalars().all()

    async def create(
        self,
        user_id: int,
        title: str,
        emoji: str,
        target_date,
        repeat_type: str = "none",
    ) -> Countdown:
        countdown = Countdown(
            user_id=user_id,
            title=title,
            emoji=emoji,
            target_date=target_date,
            repeat_type=repeat_type,
        )
        self.session.add(countdown)
        await self.session.commit()
        return countdown

    async def delete(self, countdown_id: int) -> bool:
        countdown = await self.get_by_id(countdown_id)
        if countdown:
            await self.session.delete(countdown)
            await self.session.commit()
            return True
        return False
