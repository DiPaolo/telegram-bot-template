import logging
from typing import List

from sqlalchemy.orm import Session

from deepeasy_timezones_bot import db
from deepeasy_timezones_bot import domain
from deepeasy_timezones_bot.db import RetCode
from deepeasy_timezones_bot.db.common import get_engine


def subscribe_chat_by_telegram_id(tg_id: int) -> RetCode:
    with Session(get_engine()) as session:
        subs = db.get_subscriber_by_telegram_id(tg_id, session)
        if subs is not None:
            return RetCode.ALREADY_EXIST

        chat = db.get_chat_by_telegram_id(tg_id, session)
        if chat is None:
            logging.error(f'failed to subscribe user/chat: no such chat (telegram_id={tg_id}) in DB')
            return RetCode.ERROR

        ret = db.add_subscriber_from_domain_object(chat, session)
        if ret is None:
            return RetCode.ERROR

        return RetCode.OK


def unsubscribe_chat_by_telegram_id(tg_id) -> RetCode:
    with Session(get_engine()) as session:
        db_subscriber = db.get_subscriber_by_telegram_id(tg_id, session)
        if db_subscriber is None:
            return RetCode.NOT_EXIST

        return db.delete_subscriber_by_id(db_subscriber.id, session)


def get_users() -> List[domain.User]:
    out = list()

    with Session(get_engine()) as session:
        db_users = db.get_users(session)
        for db_user in db_users:
            out.append(db_user.to_domain_object())

    return out


def get_recent_user_requests(n: int) -> List[domain.UserRequest]:
    out = list()

    with Session(get_engine()) as session:
        db_user_requests = db.get_recent_user_requests(n, session)
        for db_user_req in db_user_requests:
            out.append(db_user_req.to_domain_object(session))

    return out


def get_subscribers() -> List[domain.User]:
    out = list()

    with Session(get_engine()) as session:
        db_subscribers = db.get_subscribers(session)
        for db_sub in db_subscribers:
            db_user = db.get_chat(db_sub.chat_id, session)
            if db_user is not None:
                out.append(db_user)

    return out
