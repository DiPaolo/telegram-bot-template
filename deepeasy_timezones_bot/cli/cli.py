#!/usr/bin/env python
import logging
import os
import sys

import click as click

import deepeasy_timezones_bot.bot as bot_impl
import deepeasy_timezones_bot.service.db as db_service
# import deepeasy_timezones_bot.service.matches as matches_service
import deepeasy_timezones_bot.service.tg_notifier as tg_notifier_service
# import deepeasy_timezones_bot.service.news as news_service
from deepeasy_timezones_bot import config
from deepeasy_timezones_bot.cli.schedule_thread import ScheduleThread
from deepeasy_timezones_bot.db import init_db


@click.group()
@click.option('--debug/--no-debug', default=None)
@click.option('--pg-database', default=None, help='PostgreSQL database name')
@click.option('--pg-host', default=None, help='PostgreSQL server host')
@click.option('--pg-port', default=None, help='PostgreSQL server port')
@click.option('--pg-username', default=None, help='PostgreSQL username')
@click.option('--pg-password', default=None, help='PostgreSQL password')
def cli(debug: bool, pg_database: str, pg_host: str, pg_port: str, pg_username: str, pg_password: str):
    # apply env variables first;
    # command line parameters have higher priority, so it goes after
    _apply_env_variables_to_config()

    if debug is not None:
        config.DEBUG_PRINT = debug

    if pg_database is not None:
        config.DB_FILENAME = pg_database

    if pg_host is not None:
        config.DB_PG_HOST = pg_host

    if pg_port is not None:
        config.DB_PG_PORT = pg_port

    if pg_username is not None:
        config.DB_PG_USER = pg_username

    if pg_password is not None:
        config.DB_PG_PWD = pg_password


@click.group()
def bot():
    pass


cli.add_command(bot)


@bot.command()
@click.option('-t', '--token', default=None, help='Bot token')
def start(token: str):
    if token is not None:
        config.BOT_TOKEN = token

    if config.BOT_TOKEN is None:
        logging.error('Bot token is not set')
        click.echo("ERROR: Bot token is not set. Please specify it via environment variable or specify "
                   "'-t' / '--token' command line argument")
        sys.exit(1)

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    # matches_service.init()
    tg_notifier_service.init(bot_impl.send_message)
    init_db(config.DB_FILENAME)

    try:
        bot_impl.start(config.BOT_TOKEN)
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt. Successfully exiting application')
        sys.exit(0)
    except Exception as ex:
        logging.critical(f'Exiting application: {ex}')
        sys.exit(1)


@click.group()
def parser():
    pass


cli.add_command(parser)


@parser.command()
def start():
    continuous_thread = ScheduleThread()
    continuous_thread.start()

    init_db(config.DB_FILENAME)
    # matches_service.init()


@click.group()
def admin():
    pass


cli.add_command(admin)


@admin.command()
def users():
    init_db(config.DB_FILENAME)

    idx = 1
    for u in db_service.get_users():
        print(f'{idx}:\t{u.username} ({u.telegram_id})')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


@admin.command()
@click.option('-n/--number', default=None)
def recent(n: int):
    if n is None:
        n = 10

    init_db(config.DB_FILENAME)

    requests = db_service.get_recent_user_requests(n)
    idx = 1
    for r in requests:
        print(f'{idx}:\t{r.telegram_utc_time} user {r.user.telegram_id}: {r.text}')
        idx += 1

    print(f'\n'
          f'Total: {idx - 1} users')


@click.group()
def db():
    pass


@db.command()
def upgrade():
    import alembic.config
    import alembic.command

    cur_file_dir = os.path.dirname(os.path.realpath(__file__))
    project_root_dir = os.path.abspath(os.path.join(cur_file_dir, '..', '..'))
    alembic_config = alembic.config.Config(os.path.join(project_root_dir, 'alembic.ini'))
    alembic_config.set_main_option('script_location', os.path.join(project_root_dir, 'alembic'))
    alembic.command.upgrade(alembic_config, 'head')


cli.add_command(db)


@click.group()
def news():
    pass


# @news.command()
# def recent():
#     init_db(config.DB_FILENAME)
#
#     cur_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
#     news_items = db_service.get_recent_news(datetime.datetime.utcnow() - datetime.timedelta(hours=12), 3)
#     idx = 1
#     for n in news_items:
#         print(f'{idx}:\t{n.date_time_utc.astimezone(cur_timezone)} {n.title} ({n.url})')
#         idx += 1
#
#
# cli.add_command(news)


def init_app():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def _get_env_val_as_bool(val) -> bool:
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


def _apply_env_variables_to_config():
    env_debug_val = os.environ.get('DEEPEASY_TIMEZONES_TG_BOT_DEBUG')
    if env_debug_val:
        config.DEBUG = _get_env_val_as_bool(env_debug_val)

    env_token_val = os.environ.get('DEEPEASY_TIMEZONES_TG_BOT_TOKEN')
    if env_token_val:
        config.BOT_TOKEN = env_token_val
