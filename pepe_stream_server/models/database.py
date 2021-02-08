from os import path
import sqlite3 as db
import logging
from typing import Optional

TABLES = [
    "CREATE TABLE IF NOT EXISTS streams(id INTEGER PRIMARY KEY AUTOINCREMENT, stream_name TEXT NOT NULL, rtsp_address TEXT NOT NULL, start_on_boot INTEGER DEFAULT 1, is_connected INTEGER DEFAULT 0, pid TEXT DEFAULT NULL)"
]

INDEXES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS stream_name_index ON streams (stream_name);",
    "CREATE INDEX IF NOT EXISTS rtsp_address_index ON streams (rtsp_address);",
]


class Database:

    LOGGER_NAME = "pepe_database"

    def __init__(self, db_path: str = "pepe.db"):
        self.db_path: str = db_path
        self.initialized: bool = False
        self.conn: Optional[db.Connection] = None

        self._logger = logging.getLogger(self.LOGGER_NAME)

    def _setup(self) -> None:
        self._logger.info("Preparing to setup database...")
        c = self.conn.cursor()

        try:
            self._logger.info("Creating database tables...")
            for table_sql in TABLES:
                c.execute(table_sql)

            self._logger.info("Creating table indexes")
            for table_index in INDEXES:
                c.execute(table_index)
        finally:
            c.close()

        self._logger.info("Setup database has finished!")

    def create_conn(self) -> None:
        if self.initialized:
            return

        self._logger.info("Creating database connection...")

        db_exists = path.exists(self.db_path)
        self.conn = db.connect(self.db_path, check_same_thread=False)

        if db_exists:
            self._logger.info("Database already exists, setup is not necessary...")
        else:
            self._setup()

        self.initialized = True

    def close(self) -> None:
        self._logger.info("Closing database connection...")
        self.conn.close()
        self.initialized = False