import os
os.environ["TESTING"] = "1"

from alembic.config import Config
from alembic import command

# Create Alembic configuration
alembic_cfg = Config("alembic.ini")

# Run the migration
command.upgrade(alembic_cfg, "head")
