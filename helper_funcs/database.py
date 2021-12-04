import pymongo 
import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

import threading

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


def start() -> scoped_session:
    engine = create_engine(Config.DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()



class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            notif=True,
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason="",
            ),
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        await self.col.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason,
        )
        await self.col.update_one({"id": user_id}, {"$set": {"ban_status": ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason="",
        )
        user = await self.col.find_one({"id": int(id)})
        return user.get("ban_status", default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({"ban_status.is_banned": True})
        return banned_users

    async def set_notif(self, id, notif):
        await self.col.update_one({"id": id}, {"$set": {"notif": notif}})

    async def get_notif(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("notif", False)

    async def get_all_notif_user(self):
        notif_users = self.col.find({"notif": True})
        return notif_users

    async def total_notif_users_count(self):
        count = await self.col.count_documents({"notif": True})
        return count


class Thumbnail(BASE):
    __tablename__ = "thumbnail"
    id = Column(Integer, primary_key=True)
    msg_id = Column(Integer)
    
    def __init__(self, id, msg_id):
        self.id = id
        self.msg_id = msg_id

Thumbnail.__table__.create(checkfirst=True)

async def df_thumb(id, msg_id):
    with INSERTION_LOCK:
        msg = SESSION.query(Thumbnail).get(id)
        if not msg:
            msg = Thumbnail(id, msg_id)
            SESSION.add(msg)
            SESSION.flush()
        else:
            SESSION.delete(msg)
            file = Thumbnail(id, msg_id)
            SESSION.add(file)
        SESSION.commit()

async def del_thumb(id):
    with INSERTION_LOCK:
        msg = SESSION.query(Thumbnail).get(id)
        SESSION.delete(msg)
        SESSION.commit()

async def thumb(id):
    try:
        t = SESSION.query(Thumbnail).get(id)
        return t
    finally:
        SESSION.close()
