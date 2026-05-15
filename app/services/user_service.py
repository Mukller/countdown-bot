from app.repositories.user_repository import UserRepository
from app.db.models import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_or_create_user(self, telegram_id: int) -> User:
        return await self.user_repo.get_or_create(telegram_id)

    async def get_user(self, telegram_id: int) -> User | None:
        return await self.user_repo.get_by_telegram_id(telegram_id)
