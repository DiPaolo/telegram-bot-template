import datetime
import logging

from sqlalchemy.orm import Session
from telegram import Update

import deepeasy_timezones_bot.db as db
from deepeasy_timezones_bot.db.common import get_engine


def log_command(engine: Update):
    cur_time = datetime.datetime.utcnow()

    with Session(get_engine()) as session:
        c = engine.effective_chat
        chat = db.get_chat_by_telegram_id(c.id, session)
        if chat is None:
            chat_id = db.add_chat(c.id, c.title, c.type, session)
            chat = db.get_chat(chat_id, session)
            if chat is None:
                logging.error(
                    f"failed to log command: failed to create chat (telegram_id={c.id}, title={c.title}, type={c.type})")
                return

        u = engine.effective_user
        user = db.get_user_by_telegram_id(u.id, session)
        if user is None:
            user_id = db.add_user(u.id, u.username, u.first_name, u.last_name, u.is_bot, u.is_premium, u.language_code,
                                  session)
            user = db.get_user(user_id, session)
            if user is None:
                logging.error(
                    f"failed to log command: failed to create user (telegram_id={u.id}, username={u.username}, "
                    f"is_bot={u.is_bot})")
                return

        m = engine.effective_message

        texts = list()

        query = engine.callback_query
        if query is not None:
            texts.append(f"button data: '{query.data}'")

        location = engine.effective_message.location
        if location is not None:
            texts.append(f"location: {location.latitude}, {location.longitude}")

        texts.append(f"text: '{m.text}'")

        db.add_user_request(chat.id, user.id, cur_time, m.date, m.message_id, ', '.join(texts), session)


def log_send_message(engine: Update):
    pass
