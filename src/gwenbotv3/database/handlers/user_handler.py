import logging
from sqlite3 import Cursor
from typing import Optional

from discord import Message
from discord.ext.commands import Context

from gwenbotv3.database import connect
from gwenbotv3.database import User
from gwenbotv3.database._models.exceptions import (
    UserOrCtxNotGiven,
    EmptyDataclass,
    UserNotAnonymised,
)


class UserHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _create_user(self, ctx: Context | Message):
        return User(ctx.author.id, ctx.author.name, False)

    @connect
    def _check_user(self, cur: Cursor, user: User) -> bool:
        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user.id,)).fetchone()

        return True if res else False

    @connect
    def insert_user(
        self,
        cur: Cursor,
        ctx: Optional[Context | Message] = None,
        user: Optional[User] = None,
    ) -> User:
        if user is None and ctx is None:
            raise UserOrCtxNotGiven(self.insert_user)

        if ctx:
            user = self._create_user(ctx)

        if not user:
            raise EmptyDataclass(user, self.insert_user)

        if self._check_user(user):
            return user

        cur.execute(
            "INSERT INTO Users(user_id, user_name) VALUES(?,?)", (user.id, user.name)
        )

        self.logger.info("Added user: %s", user)

        return user

    @connect
    def insert_user_by_id(self, cur: Cursor, user_id: int, user_name: str) -> User:
        user = User(id=user_id, name=user_name, is_anonymised=False)

        cur.execute(
            "INSERT INTO Users(user_id, user_name) VALUES(?,?)", (user.id, user.name)
        )

        self.logger.info("Added user by ID: %s", user)

        return user

    @connect
    def fetch_user(self, cur: Cursor, ctx: Context | Message) -> User:
        user = self._create_user(ctx)

        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user.id,)).fetchone()

        if not res:
            self.insert_user(ctx)
            return user

        if len(res) < 3:
            self.logger.critical(
                "Successfully fetched a user, yet not all information was fetched properly. On user: %s",
                user,
            )
            self.insert_user(ctx)
            return user

        if res[1] != user.name and not res[2]:
            self.logger.info(
                "Updated user name of id %s - From %s to %s", user.id, res[1], user.name
            )
            cur.execute(
                "UPDATE Users SET user_name=(?) WHERE user_id=?",
                (ctx.author.name, user.id),
            )

        return user

    @connect
    def anonymise_user(self, cur: Cursor, ctx: Context) -> None:
        user = self._create_user(ctx)

        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user.id,)).fetchone()

        if res[2]:
            self.logger.debug(
                "Tried to anonymise user which is already anonymised: %s", user.id
            )
            return

        cur.execute(
            "UPDATE Users SET is_anonymised=TRUE, user_name=? WHERE user_id=?",
            ("Unknown User", user.id),
        )
        self.logger.info("Anonymised user: %s", user.id)

    @connect
    def deanonymise_user(self, cur: Cursor, ctx: Context) -> None:
        user = self._create_user(ctx)

        res = cur.execute(
            "SELECT is_anonymised FROM Users WHERE user_id=?", (user.id,)
        ).fetchone()

        if not res:
            self.insert_user(ctx)
            self.logger.debug("Tried to deanonymise user which did not exist: %s", user)
            raise UserNotAnonymised

        if not res[0]:
            self.logger.debug(
                "Tried to deanonymise user which not anonymised: %s", user
            )
            raise UserNotAnonymised

        self.logger.info("Deanonymised user: %s", user)
        cur.execute("UPDATE Users SET is_anonymised=FALSE WHERE user_id=?", (user.id,))

    @connect
    def fetch_user_by_id(self, cur: Cursor, user_id: int) -> Optional[User]:
        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user_id,)).fetchone()

        if not res:
            return None

        user = User(id=res[0], name=res[1], is_anonymised=res[2])

        return user
