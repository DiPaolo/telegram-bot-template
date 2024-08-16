1. ```alembic init alembic```

2. **alembic/env.py**:  
  ```target_metadata = Base.metadata```

    ```
    from deepeasy_timezones_bot import config as cfg
    config.set_main_option("sqlalchemy.url", get_db_url(cfg.DB_FILENAME))
    ```

3. (optional) for SQLite:  
  **alembic.ini**:  
  ```sqlalchemy.url = sqlite:////<path>/db/deepeasy_timezones_bot.db```

4. **alembic.ini**:  
  ```sqlalchemy.url = 'will be set dynamically'```

5. запуск бота чтобы создать базу

6. ```alembic revision --autogenerate -m 'initial'```
