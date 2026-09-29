import sqlite3
from pathlib import Path
from datetime import datetime


class JobDatabase:

    def __init__(self, db_path="database/jobhunter.db"):

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    def _create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                source TEXT NOT NULL,

                external_id TEXT NOT NULL,

                url TEXT NOT NULL,

                title TEXT,

                company TEXT,

                location TEXT,

                description TEXT,

                published_at TEXT,

                status TEXT NOT NULL DEFAULT 'NEW',

                match_percentage REAL,

                job_profile TEXT,

                match_result TEXT,

                first_seen TEXT NOT NULL,

                last_seen TEXT NOT NULL,

                processed_at TEXT,

                error TEXT,

                UNIQUE(source, external_id)
            )
        """)

        # Añadir columnas si la tabla ya existía
        self._add_column_if_missing(
            cursor,
            "job_profile",
            "TEXT"
        )

        self._add_column_if_missing(
            cursor,
            "match_result",
            "TEXT"
        )

        self.connection.commit()

    def _add_column_if_missing(
        self,
        cursor,
        column_name,
        column_type
    ):

        cursor.execute("""
            PRAGMA table_info(jobs)
        """)

        columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if column_name not in columns:

            cursor.execute(
                f"""
                ALTER TABLE jobs
                ADD COLUMN {column_name} {column_type}
                """
            )

    def exists(
        self,
        source: str,
        external_id: str
    ) -> bool:

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT 1
            FROM jobs
            WHERE source = ?
            AND external_id = ?
            LIMIT 1
        """, (
            source,
            external_id
        ))

        return cursor.fetchone() is not None

    def add_job(self, job: dict) -> int:

        now = datetime.now().isoformat()

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO jobs (
                source,
                external_id,
                url,
                title,
                company,
                location,
                description,
                published_at,
                status,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["source"],
            job["external_id"],
            job["url"],
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("description"),
            job.get("published_at"),
            "NEW",
            now,
            now
        ))

        self.connection.commit()

        return cursor.lastrowid

    def update_status(
        self,
        source,
        external_id,
        status,
        match_percentage=None,
        error=None
    ):

        now = datetime.now().isoformat()

        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE jobs
            SET
                status = ?,
                match_percentage = ?,
                last_seen = ?,
                processed_at = ?,
                error = ?
            WHERE source = ?
            AND external_id = ?
        """, (
            status,
            match_percentage,
            now,
            now,
            error,
            source,
            external_id
        ))

        self.connection.commit()

    def update_analysis(
        self,
        source,
        external_id,
        job_profile=None,
        match_result=None,
        match_percentage=None,
        status=None,
        error=None
    ):

        now = datetime.now().isoformat()

        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE jobs
            SET
                job_profile = ?,
                match_result = ?,
                match_percentage = ?,
                status = COALESCE(?, status),
                last_seen = ?,
                processed_at = ?,
                error = ?
            WHERE source = ?
            AND external_id = ?
        """, (
            job_profile,
            match_result,
            match_percentage,
            status,
            now,
            now,
            error,
            source,
            external_id
        ))

        self.connection.commit()

    def get_job(
        self,
        source,
        external_id
    ):

        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE source = ?
            AND external_id = ?
        """, (
            source,
            external_id
        ))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def get_jobs(self, status=None):

        cursor = self.connection.cursor()

        if status is None:

            cursor.execute("""
                SELECT *
                FROM jobs
                ORDER BY first_seen DESC
            """)

        else:

            cursor.execute("""
                SELECT *
                FROM jobs
                WHERE status = ?
                ORDER BY first_seen DESC
            """, (status,))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_job_by_id(self, job_id):
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM jobs
            WHERE id = ?
        """, (job_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def close(self):

        self.connection.close()