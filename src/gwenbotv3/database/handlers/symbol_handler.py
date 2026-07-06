from sqlite3 import Cursor

from gwenbotv3 import SingletonLogger
from gwenbotv3.database import connect
from gwenbotv3.database import UserContext, User
from gwenbotv3.database._models.exceptions import (
    AmountNotInt,
    NoUserFound,
    LimitTooHigh,
)
from gwenbotv3.database.handlers.user_handler import UserHandler
from gwenbotv3.database.get_context import context


class SymbolHandler:
    def __init__(self):
        self.logger = SingletonLogger().get_logger()
        self.user_handler = UserHandler()

    @connect
    def fetch_amount(self, cur: Cursor, ctx: UserContext) -> int:
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

        return res

    @connect
    def fetch_user_amount(self, cur: Cursor, ctx: UserContext) -> int:
        if not ctx.user:
            return 0

        res = cur.execute(
            "SELECT amount FROM QuestionUser WHERE user=? AND server=?",
            (ctx.user.id, ctx.server.id),
        ).fetchone()

        if not res:
            raise AmountNotInt

        res = res[0]

        try:
            res = int(res)
        except ValueError as exc:
            raise AmountNotInt from exc

        return res

    @connect
    def _set_latest_user(self, cur: Cursor, ctx: UserContext) -> None:
        if not ctx.user:
            return

        cur.execute(
            "UPDATE QuestionCount SET latest_user=? WHERE server=?",
            (ctx.user.id, ctx.server.id),
        )

    @connect
    def fetch_latest_user(self, cur: Cursor, ctx: UserContext) -> User:
        res = cur.execute(
            "SELECT u.user_id, u.user_name, u.is_anonymised "
            + "FROM QuestionCount qc "
            + "JOIN Users u ON qc.latest_user = u.user_id "
            + "WHERE qc.server = ?",
            (ctx.server.id,),
        ).fetchone()

        if not res:
            raise NoUserFound

        user = User(id=res[0], name=res[1], is_anonymised=res[2])

        return user

    @connect
    def update(self, cur: Cursor, ctx: UserContext) -> None:
        amount = self.fetch_amount(ctx) + 1
        user_amount = self.fetch_user_amount(ctx) + 1

        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "UPDATE QuestionCount SET amount=?, latest_user=? WHERE server=?",
            (amount, ctx.user.id, ctx.server.id),
        )

        cur.execute(
            "UPDATE QuestionUser "
            "SET amount=? "
            "WHERE user=? AND questions_server=?",
            (user_amount, ctx.user.id, ctx.server.id),
        )

    @connect
    def initialise(
        self, cur: Cursor, ctx: UserContext, symbol: str, channel_id: int
    ) -> None:
        if not ctx.user:
            self.user_handler.insert_user(ctx.ctx)
            ctx = context(ctx.ctx)

        if not ctx.user:
            return

        cur.execute(
            "INSERT INTO QuestionCount(amount, latest_user, server, channel_id, symbol, creating_user) "
            "VALUES(?,?,?,?,?,?)",
            (0, None, ctx.server.id, channel_id, symbol, ctx.user.id),
        )

    @connect
    def change_symbol(self, cur: Cursor, ctx: UserContext, symbol: str) -> None:
        cur.execute(
            "UPDATE QuestionCount SET symbol=? WHERE server=?",
            (symbol, ctx.server.id),
        )

    @connect
    def fetch_lb(
        self, cur: Cursor, ctx: UserContext, limit: int = 10
    ) -> list[tuple[User, int]]:
        if limit > 20:
            raise LimitTooHigh

        res = cur.execute(
            "SELECT u.user_id, u.user_name, u.is_anonymised, qu.amount "
            + "FROM QuestionUser qu "
            + "JOIN Users u ON u.user_id = qu.user "
            + "WHERE qu.questions_server=? "
            + "ORDER BY qu.amount DESC, u.user_id ASC "
            + "LIMIT ?",
            (ctx.server.id, limit),
        ).fetchall()

        return [
            (User(id=row[0], name=row[1], is_anonymised=bool(row[2])), row[3])
            for row in res
            if row is not None
        ]

    @connect
    def fetch_channel(self, cur: Cursor, ctx: UserContext) -> int:
        res = cur.execute(
            "SELECT channel_id FROM QuestionCount WHERE server=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            return 0

        return int(res[0])

    @connect
    def fetch_symbol(self, cur: Cursor, ctx: UserContext) -> str:
        res = cur.execute(
            "SELECT symbol FROM QuestionCount WHERE server=?", (ctx.server.id,)
        ).fetchone()

        if not res:
            return ""

        return res[0]

    @connect
    def fetch_creating_user(self, cur: Cursor, ctx: UserContext) -> int:
        res = cur.execute(
            "SELECT creating_user FROM QuestionCount WHERE server=?",
            (ctx.server.id,),
        ).fetchone()

        if not res:
            return 0

        return res[0]

    @connect
    def set_amount(self, cur: Cursor, ctx: UserContext, amount: int) -> None:
        cur.execute(
            "UPDATE QuestionCount SET amount=? WHERE server=?",
            (amount, ctx.server.id),
        )
