"""Async SQLite persistence layer used by main.py."""
import json
import aiosqlite


class MusicDatabase:
    def __init__(self, path: str = "music.db"):
        self.path = path
        self.db = None

    async def connect(self):
        if self.db is not None:
            return
        self.db = await aiosqlite.connect(self.path)
        self.db.row_factory = aiosqlite.Row
        await self.db.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS servers (
            server_id INTEGER PRIMARY KEY, name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS voice_channels (
            channel_id INTEGER PRIMARY KEY, server_id INTEGER NOT NULL, name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS plays (
            id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER NOT NULL,
            channel_id INTEGER, user_id INTEGER NOT NULL, user_name TEXT NOT NULL,
            title TEXT NOT NULL, author TEXT NOT NULL, uri TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 0, source TEXT NOT NULL DEFAULT 'unknown',
            played_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, server_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL, user_name TEXT NOT NULL, query TEXT NOT NULL,
            results INTEGER NOT NULL DEFAULT 0,
            searched_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS sessions (
            server_id INTEGER PRIMARY KEY, channel_id INTEGER NOT NULL,
            current_track TEXT, queue_data TEXT NOT NULL DEFAULT '[]',
            position INTEGER NOT NULL DEFAULT 0, volume INTEGER NOT NULL DEFAULT 100,
            is_paused INTEGER NOT NULL DEFAULT 0, loop_mode TEXT NOT NULL DEFAULT 'normal',
            auto_resume INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """)
        await self.db.commit()

    async def close(self):
        if self.db is not None:
            await self.db.close()
            self.db = None

    def _conn(self):
        if self.db is None:
            raise RuntimeError("Database is not connected")
        return self.db

    async def register_server(self, server_id, name):
        await self._conn().execute("INSERT INTO servers(server_id,name) VALUES(?,?) ON CONFLICT(server_id) DO UPDATE SET name=excluded.name", (server_id, name))
        await self.db.commit()

    async def register_voice_channel(self, channel_id, server_id, name):
        await self._conn().execute("INSERT INTO voice_channels(channel_id,server_id,name) VALUES(?,?,?) ON CONFLICT(channel_id) DO UPDATE SET server_id=excluded.server_id,name=excluded.name", (channel_id, server_id, name))
        await self.db.commit()

    async def log_music_play(self, server_id, channel_id, user_id, user_name, track_title, track_author, track_uri, track_duration, track_source):
        await self._conn().execute("INSERT INTO plays(server_id,channel_id,user_id,user_name,title,author,uri,duration,source) VALUES(?,?,?,?,?,?,?,?,?)", (server_id, channel_id, user_id, user_name, track_title, track_author, track_uri, track_duration, track_source))
        await self.db.commit()

    async def log_search(self, server_id, user_id, user_name, search_query, results_count):
        await self._conn().execute("INSERT INTO searches(server_id,user_id,user_name,query,results) VALUES(?,?,?,?,?)", (server_id, user_id, user_name, search_query, results_count))
        await self.db.commit()

    async def save_playback_session(self, server_id, channel_id, current_track, queue_data, position, volume, is_paused, loop_mode, auto_resume):
        await self._conn().execute("""INSERT INTO sessions(server_id,channel_id,current_track,queue_data,position,volume,is_paused,loop_mode,auto_resume)
        VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(server_id) DO UPDATE SET channel_id=excluded.channel_id,current_track=excluded.current_track,queue_data=excluded.queue_data,position=excluded.position,volume=excluded.volume,is_paused=excluded.is_paused,loop_mode=excluded.loop_mode,auto_resume=excluded.auto_resume,updated_at=datetime('now')""",
        (server_id, channel_id, json.dumps(current_track) if current_track else None, json.dumps(queue_data), position, volume, int(is_paused), loop_mode, int(auto_resume)))
        await self.db.commit()

    async def get_all_active_sessions(self):
        rows = await (await self._conn().execute("SELECT * FROM sessions WHERE auto_resume=1")).fetchall()
        return [dict(r) | {"current_track": json.loads(r["current_track"]) if r["current_track"] else None,
                           "queue_data": json.loads(r["queue_data"]), "is_paused": bool(r["is_paused"]),
                           "auto_resume": bool(r["auto_resume"])} for r in rows]

    async def get_server_stats(self, server_id):
        row = await (await self._conn().execute("""SELECT COUNT(*) total_plays, COUNT(DISTINCT user_id) unique_listeners,
        SUM(CASE WHEN played_at >= datetime('now','-7 days') THEN 1 ELSE 0 END) plays_this_week
        FROM plays WHERE server_id=?""", (server_id,))).fetchone()
        searches = await (await self._conn().execute("SELECT COUNT(*) n FROM searches WHERE server_id=?", (server_id,))).fetchone()
        return {"total_plays": row["total_plays"] or 0, "unique_listeners": row["unique_listeners"] or 0,
                "plays_this_week": row["plays_this_week"] or 0, "total_searches": searches["n"] or 0}

    async def get_top_tracks(self, server_id, limit=10):
        rows = await (await self._conn().execute("SELECT title,author,COUNT(*) play_count FROM plays WHERE server_id=? GROUP BY uri ORDER BY play_count DESC LIMIT ?", (server_id, limit))).fetchall()
        return [dict(r) for r in rows]

    async def get_user_listening_history(self, server_id, user_id, limit=10):
        rows = await (await self._conn().execute("SELECT title,author,duration FROM plays WHERE server_id=? AND user_id=? ORDER BY id DESC LIMIT ?", (server_id, user_id, limit))).fetchall()
        return [dict(r) for r in rows]

    async def get_user_stats(self, server_id, user_id):
        row = await (await self._conn().execute("SELECT COUNT(*) total_listens,COALESCE(SUM(duration),0) total_duration FROM plays WHERE server_id=? AND user_id=?", (server_id, user_id))).fetchone()
        result = dict(row)
        return result if result["total_listens"] else None

    async def get_recent_searches(self, server_id, limit=10):
        rows = await (await self._conn().execute("SELECT query,user_name,results FROM searches WHERE server_id=? ORDER BY id DESC LIMIT ?", (server_id, limit))).fetchall()
        return [dict(r) for r in rows]
