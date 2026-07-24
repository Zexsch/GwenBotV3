"""Interacts with the user table in the database."""

import logging
from sqlite3 import Cursor

from discord import Message
from discord.ext.commands import Context

from gwenbotv3.database import User, connect
from gwenbotv3.database._models.exceptions import (
    EmptyDataclass,
    UserNotAnonymised,
    UserOrCtxNotGiven,
)


class UserHandler:
    """Class housing methods used to interact with the user table in the database."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _create_user(self, ctx: Context | Message):
        """Creates a User object given a discord.commands.Context or discord.Message argument"""
        return User(ctx.author.id, ctx.author.name, False)

    @connect
    def _check_user(self, cur: Cursor, user: User) -> bool:
        """Checks if a user is in the database.

        Args:
            user (User): User to check

        Returns:
            bool: True if the user is found, else False
        """
        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user.id,)).fetchone()

        return True if res else False

    @connect
    def insert_user(
        self,
        cur: Cursor,
        ctx: Context | Message | None = None,
        user: User | None = None,
    ) -> User:
        """Inserts a user into the database.
        Does nothing if the user is already in the database.

        Args:
            ctx (Optional[Context  |  Message], optional): discord Context.
                Use either this or a User object. Defaults to None.
            user (Optional[User], optional): User object.
                Use either this or a discord Context. Defaults to None.

        Raises:
            UserOrCtxNotGiven: If no discord Context nor User object is given.
            EmptyDataclass: If the User object given is empty.

        Returns:
            User: Inserted user as an object
        """
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
        """Inserts a user to the database by their id and name.

        Args:
            user_id (int): User discord id
            user_name (str): User discord name

        Returns:
            User: Inserted user as an object
        """
        user = User(id=user_id, name=user_name, is_anonymised=False)

        cur.execute(
            "INSERT INTO Users(user_id, user_name) VALUES(?,?)", (user.id, user.name)
        )

        self.logger.info("Added user by ID: %s", user)

        return user

    @connect
    def fetch_user(self, cur: Cursor, ctx: Context | Message) -> User:
        """Returns a user from the database.
        Will automatically insert the user into the database if they're not yet in it.

        Args:
            ctx (Context | Message): Discord context.

        Returns:
            User: Fetched user.
        """
        user = self._create_user(ctx)

        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user.id,)).fetchone()

        if not res:
            self.insert_user(ctx)
            return user

        if len(res) < 3:
            self.logger.critical(
                (
                    "Successfully fetched a user, yet not all information was fetched properly. "
                    + "On user: %s"
                ),
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
        """Anonymises a user.
        Sets their name to Unknown User and sets is_anonymised to true.

        Args:
            ctx (Context): discord Context.
        """
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
        """Inverse of anonymise_user.
        Reverts their is_anonymised field to False and adds their name to the database.

        Args:
            ctx (Context): discord Context.

        Raises:
            UserNotAnonymised: If a user is not in the database.
            UserNotAnonymised: If a user is not anonymised.
        """
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
    def fetch_user_by_id(self, cur: Cursor, user_id: int) -> User | None:
        """Fetches a user from the database using their ID.
        Use fetch_user if a User object is present instead.

        Args:
            user_id (int): ID of the user to be fetched.

        Returns:
            Optional[User]: User object if found, else None
        """
        res = cur.execute("SELECT * FROM Users WHERE user_id=?", (user_id,)).fetchone()

        if not res:
            return None

        user = User(id=res[0], name=res[1], is_anonymised=res[2])

        return user
