1. ```alembic init alembic```

1. **alembic/env.py**:
  ```target_metadata = Base.metadata```

  ```
  from deepeasy_timezones_bot import config as cfg
  config.set_main_option("sqlalchemy.url", get_db_url(cfg.DB_FILENAME))
  ```

1. **alembic.ini**:
  ```sqlalchemy.url = 'will be set dynamically'```

1. запуск бота чтобы создать базу

1. ```alembic revision --autogenerate -m 'initial'```