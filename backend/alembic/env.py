from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Import your settings and your Base
from app.core.config import settings
from app.db.base import Base  # This is where your metadata lives

# 2. IMPORTANT: Import your models so Base.metadata is populated
from app.models.interview import InterviewSession, InterviewQuestion, Answer
from app.models.user import User 
from app.models.question import Subject, Question, question_subjects 

# 3. Access the Alembic Config
config = context.config

# 4. Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. Set the Target Metadata (THIS IS WHAT WAS MISSING)
target_metadata = Base.metadata

# 6. Override the sqlalchemy.url from your settings.py/env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create the engine from the config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata  # Passing metadata to the connection
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()