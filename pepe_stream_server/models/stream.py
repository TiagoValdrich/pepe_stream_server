from typing import List, Optional, Tuple
from sqlite3 import Connection
from asyncio import get_event_loop
from functools import partial
from subprocess import Popen
import os
import signal


class Stream:
    def __init__(
        self,
        stream_name: str,
        rtsp_address: str,
        start_on_boot: int = 1,
        is_connected: int = 0,
        pid: Optional[str] = None,
        id: Optional[int] = None,
    ) -> None:
        self.id = id
        self.stream_name = stream_name
        self.rtsp_address = rtsp_address
        self.start_on_boot = start_on_boot
        self.is_connected = is_connected
        self.pid = pid

    @staticmethod
    def build_from_row(row: Tuple, raw_dict: bool = False) -> "Stream":
        s = Stream(
            id=row[0],
            stream_name=row[1],
            rtsp_address=row[2],
            start_on_boot=row[3],
            is_connected=row[4],
            pid=row[5],
        )

        if raw_dict:
            return s.__dict__

        return s

    @staticmethod
    def build_from_rows(rows: List[Tuple], raw_dict: bool = False) -> List["Stream"]:
        streams = []

        for row in rows:
            s = Stream.build_from_row(row)
            streams.append(s.__dict__ if raw_dict else s)

        return streams

    async def create(self, conn: Connection) -> None:
        loop = get_event_loop()

        with conn as c:
            execute_f = partial(
                c.execute,
                "INSERT INTO streams VALUES(?, ?, ?, ?, ?, ?)",
                [
                    self.id,
                    self.stream_name,
                    self.rtsp_address,
                    self.start_on_boot,
                    self.is_connected,
                    self.pid,
                ],
            )

            await loop.run_in_executor(
                None,
                execute_f,
            )

    async def delete(self, conn: Connection) -> None:
        loop = get_event_loop()

        with conn as c:
            execute_f = partial(
                c.execute,
                "DELETE FROM streams WHERE stream_name = ?",
                [self.stream_name],
            )

            await loop.run_in_executor(
                None,
                execute_f,
            )

    @staticmethod
    async def delete_stream(conn: Connection, stream_name: str) -> None:
        loop = get_event_loop()

        with conn as c:
            execute_f = partial(
                c.execute, "DELETE FROM streams WHERE stream_name = ?", [stream_name]
            )

            await loop.run_in_executor(
                None,
                execute_f,
            )

    async def update(self, conn: Connection) -> None:
        loop = get_event_loop()

        with conn as c:
            execute_f = partial(
                c.execute,
                "UPDATE streams SET stream_name = ?, rtsp_address = ?, start_on_boot = ?, is_connected = ?, pid = ? WHERE stream_name = ?",
                [
                    self.stream_name,
                    self.rtsp_address,
                    self.start_on_boot,
                    self.is_connected,
                    self.pid,
                    self.stream_name,
                ],
            )

            await loop.run_in_executor(None, execute_f)

    @staticmethod
    async def get_all_streams(
        conn: Connection, raw_dict: bool = True
    ) -> List["Stream"]:
        loop = get_event_loop()
        c = conn.cursor()

        try:
            execute_f = partial(c.execute, "SELECT * FROM streams")
            fetch_all_f = partial(c.fetchall)

            await loop.run_in_executor(None, execute_f)
            rows = await loop.run_in_executor(None, fetch_all_f)

            streams = Stream.build_from_rows(rows, raw_dict=raw_dict)

            return streams
        finally:
            c.close()

    @staticmethod
    async def find_stream_by_name(conn: Connection, stream_name: str) -> "Stream":
        loop = get_event_loop()
        c = conn.cursor()

        try:
            execute_f = partial(
                c.execute, "SELECT * FROM streams WHERE stream_name = ?", [stream_name]
            )
            fetch_one_f = partial(c.fetchone)

            await loop.run_in_executor(None, execute_f)
            row = await loop.run_in_executor(None, fetch_one_f)

            if not row:
                return None

            stream = Stream.build_from_row(row)

            return stream
        finally:
            c.close()

    async def connect(self, conn: Connection) -> None:
        path = os.getcwd() + "/live/" + self.stream_name

        if not os.path.exists(path):
            os.mkdir(path)

        p = Popen(
            [
                "ffmpeg",
                "-i",
                self.rtsp_address,
                "-y",
                "-an",
                "-c:v",
                "libx264",
                "-preset:v",
                "ultrafast",
                "-hls_time",
                "5",
                "-hls_list_size",
                "5",
                "-start_number",
                "1",
                path + "/playlist.m3u8",
            ]
        )

        self.is_connected = 1
        self.pid = str(p.pid)

        await self.update(conn)

    async def disconnect(self, conn: Connection) -> None:
        os.kill(int(self.pid), signal.SIGTERM)

        self.is_connected = 0
        self.pid = None

        await self.update(conn)
