"""Interacts with the QuestionUser and QuestionCount database tables."""

import logging
from sqlite3 import Cursor

from gwenbotv3.database_handling import User, UserContext, connect
from gwenbotv3.database_handling._models.exceptions import (
    AmountNotInt,
    LimitTooHigh,
)
from gwenbotv3.database_handling.get_context import context
from gwenbotv3.database_handling.handlers.user_handler import UserHandler


class SymbolHandler:
    """Anything to do with the QuestionUser and QuestionCount tables.

    This is for the symbol counting and leaderboard feature.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.user_handler = UserHandler()

    @connect
    def fetch_amount(self, cur: Cursor, ctx: UserContext) -> int:
        """Fetches the total amount of sent symbols in a server.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Raises:
            AmountNotInt: If no amount is found
            AmountNotInt: If the amount fetched is not an integer

        Returns:
            int: Amount
        """
        res = cur.execute(
            "SELECT amount FROM QuestionCount WHERE server=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            raise AmountNotInt

        res = res[0]

        try:
            res = int(res)
        except ValueError as exc:
            raise AmountNotInt from exc

        self.logger.debug("Fetched amount: %i", res)
        return res

    @connect
    def fetch_user_amount(self, cur: Cursor, ctx: UserContext) -> int:
        """Fetches the amount of symbols sent in a server by a specific user.
        The user is given through the UserContext.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Raises:
            AmountNotInt: If the amount fetched was not an integer.

        Returns:
            int: Amount.
        """
        if not ctx.user:
            return 0

        res = cur.execute(
            "SELECT amount FROM QuestionUser WHERE user=? AND questions_server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        if not res:
            self.logger.debug("Fetched amount from user not in the database.")
            return 0

        res = res[0]

        try:
            res = int(res)
        except ValueError as exc:
            raise AmountNotInt from exc

        self.logger.debug("Fetched amount for user %s: %i", ctx.user.id, res)

        return res

    @connect
    def _set_latest_user(self, cur: Cursor, ctx: UserContext) -> None:
        """Sets the latest user in a server to ctx.user.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
        """
        if not ctx.user:
            self.logger.critical(
                "Tried to set the latest user from a context with no user."
            )
            return

        cur.execute(
            "UPDATE QuestionCount SET latest_user=? WHERE server=?",
            (ctx.user.id, ctx.server.id),
        )

        self.logger.debug(
            "Set latest user in server %s to %s", ctx.server.id, ctx.user.id
        )

    @connect
    def fetch_latest_user(self, cur: Cursor, ctx: UserContext) -> User:
        """Fetches the latest user in a server.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Returns:
            User: Latest user.
        """
        res = cur.execute(
            "SELECT u.user_id, u.user_name, u.is_anonymised "
            "FROM QuestionCount qc "
            "JOIN Users u ON qc.latest_user = u.user_id "
            "WHERE qc.server = ?",
            (ctx.server.id,),
        ).fetchone()

        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx.user = context(ctx.ctx).user

        if not res:
            self._set_latest_user(ctx)
        else:
            if len(res) < 3:
                self.logger.critical(
                    (
                        "Successfully fetched a user, yet not all information "
                        "was fetched properly. On user: %s"
                    ),
                    ctx.ctx.author.id,  # Had to do this because pylance is shit
                )

        user = User(id=res[0], name=res[1], is_anonymised=res[2])

        new_user: User | None = None

        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            new_user = context(ctx.ctx).user

        self.logger.debug("Fetched user: %s", user)

        return new_user if new_user else user

    @connect
    def update(self, cur: Cursor, ctx: UserContext) -> None:
        """Updates the database.
        Increments the server amount by one;
        Increments the user amount by one;
        Sets the latest user to ctx.author.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
        """
        amount = self.fetch_amount(ctx) + 1
        user_amount = self.fetch_user_amount(ctx) + 1

        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:  # To stop pylance from being genuinely fucking stupid.
            return

        cur.execute(
            "UPDATE QuestionCount SET amount=?, latest_user=? WHERE server=?",
            (amount, ctx.user.id, ctx.server.id),
        )

        self.logger.debug(
            "Set on QuestionCount server=%s, amount=%s, latest_user=%s",
            ctx.server.id,
            amount,
            ctx.user.id,
        )

        cur.execute(
            "UPDATE QuestionUser SET amount=? WHERE user=? AND questions_server=?",
            (user_amount, ctx.user.id, ctx.server.id),
        )

        self.logger.debug(
            "Set on QuestionUser question_server=%s, amount=%s, user=%s",
            ctx.server.id,
            amount,
            ctx.user.id,
        )

    @connect
    def initialise(
        self, cur: Cursor, ctx: UserContext, symbol: str, channel_id: int
    ) -> None:
        """Initialises the symbol counter for a server.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
            symbol (str): The symbol to count.
            channel_id (int): The channel to count in.
        """
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            (
                "INSERT INTO QuestionCount(amount, latest_user, server, "
                "channel_id, symbol, creating_user) "
                "VALUES(?,?,?,?,?,?)"
            ),
            (0, None, ctx.server.id, channel_id, symbol, ctx.user.id),
        )

        self.logger.info(
            "Initialised Symbol counter for server=%s, channel_id=%s, "
            "symbol=%s, creating_user=%s",
            ctx.server.id,
            channel_id,
            symbol,
            ctx.user.id,
        )

    @connect
    def change_symbol(self, cur: Cursor, ctx: UserContext, symbol: str) -> None:
        """Changes the counted symbol.
        Note that by itself, it will not refresh the counted symbols.
            But if a recount is ever done, prior symbol counts are lost.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
            symbol (str): The symbol to now count.
        """
        cur.execute(
            "UPDATE QuestionCount SET symbol=? WHERE server=?",
            (symbol, ctx.server.id),
        )

        self.logger.info(
            "Updated symbol for server=%s, new symbol=%s", ctx.server.id, symbol
        )

    @connect
    def fetch_lb(
        self, cur: Cursor, ctx: UserContext, limit: int = 10
    ) -> list[tuple[User, int]]:
        """Fetches the symbol counter leaderboard.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
            limit (int, optional): How many rows should be fetched. Defaults to 10.

        Raises:
            LimitTooHigh: If the limit given is greater than 20.

        Returns:
            list[tuple[User, int]]: Maps users to their amount,
                ordered by the amount.
        """
        if limit > 20:
            raise LimitTooHigh(limit)

        res = cur.execute(
            "SELECT u.user_id, u.user_name, u.is_anonymised, qu.amount "
            "FROM QuestionUser qu "
            "JOIN Users u ON u.user_id = qu.user "
            "WHERE qu.questions_server=? "
            "ORDER BY qu.amount DESC, u.user_id ASC "
            "LIMIT ?",
            (ctx.server.id, limit),
        ).fetchall()

        user_list = [
            (User(id=row[0], name=row[1], is_anonymised=bool(row[2])), row[3])
            for row in res
            if row is not None
        ]

        self.logger.debug(
            "Fetched Leaderboard for server=%s, limit=%i", ctx.server.id, limit
        )

        return user_list

    @connect
    def fetch_channel(self, cur: Cursor, ctx: UserContext) -> int:
        """Fetches the channel where the counter was set up in a server.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Returns:
            int: Channel ID.
        """
        res = cur.execute(
            "SELECT channel_id FROM QuestionCount WHERE server=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            return 0

        # self.logger.debug("Fetched channel %s for server %s", res[0], ctx.server.id)
        return int(res[0])

    @connect
    def fetch_symbol(self, cur: Cursor, ctx: UserContext) -> str:
        """Fetches the symbol to be counted in a server.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Returns:
            str: Symbol.
        """
        res = cur.execute(
            "SELECT symbol FROM QuestionCount WHERE server=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            self.logger.warning(
                "Tried to fetch symbol from a server "
                "without a counter set up. server=%s",
                ctx.server.id,
            )
            return ""

        self.logger.debug("Fetched symbol=%s for server=%s", res[0], ctx.server.id)

        if not isinstance(res[0], str):
            self.logger.critical("Fetched a non-string from fetch_symbol")
            raise TypeError

        return res[0]

    @connect
    def fetch_creating_user(self, cur: Cursor, ctx: UserContext) -> int:
        """Fetches the user that first initialised the counter.

        Args:
            ctx (UserContext): UserContext object. See database._models.models

        Returns:
            int: User ID.
        """
        res = cur.execute(
            "SELECT creating_user FROM QuestionCount WHERE server=?",
            (ctx.server.id,),
        ).fetchone()

        if not res:
            self.logger.warning(
                "Tried to fetch creating_user from a server "
                "without a counter set up. server=%s",
                ctx.server.id,
            )
            return 0

        if not isinstance(res[0], int):
            self.logger.critical("Fetched non-int from creating user")
            raise TypeError

        self.logger.debug(
            "Fetched creating_user=%s for server=%s", res[0], ctx.server.id
        )

        return res[0]

    @connect
    def set_amount(self, cur: Cursor, ctx: UserContext, amount: int) -> None:
        """Sets the overall server amount to a given value.

        Args:
            ctx (UserContext): UserContext object. See database._models.models
            amount (int): Amount to set it to.
        """
        cur.execute(
            "UPDATE QuestionCount SET amount=? WHERE server=?",
            (amount, ctx.server.id),
        )
        self.logger.debug("Set amount=%s on server=%s", amount, ctx.server.id)
