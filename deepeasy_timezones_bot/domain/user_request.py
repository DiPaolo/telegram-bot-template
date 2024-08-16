import datetime
from dataclasses import dataclass

from deepeasy_timezones_bot.domain import Chat, User


@dataclass
class UserRequest(object):
    chat: Chat
    user: User
    utc_time: datetime.datetime
    telegram_utc_time: datetime.datetime
    telegram_message_id: int
    text: str
