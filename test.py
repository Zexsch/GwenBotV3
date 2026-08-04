from typing import TypeVar, Union, Generic, Callable, Any, Concatenate, ParamSpec
from collections.abc import Coroutine


class Bot: ...
class AutoShardedBot: ...
class Cog: ...

BotT = TypeVar('BotT', bound=Bot, covariant=True)
T = TypeVar('T')
P = ParamSpec('P')

class Context(Generic[BotT]): ...

GenericAlias = type(list[int])

CogT = TypeVar('CogT', bound='Cog')

Coro = Coroutine[Any, Any, T]

ContextT = TypeVar('ContextT', bound='Context[Any]')
ContextT2 = TypeVar('ContextT2', bound='Context[Any]')

CommandCallback = Union[
    Callable[Concatenate[CogT, ContextT, P], Coro[T]],
    Callable[Concatenate[ContextT, P], Coro[T]],
]

class Command(Generic[CogT, P, T]): ...


class locale_str: ...
class _MissingSentinel: ...

MISSING: Any = _MissingSentinel()
class HybridCommand(Command[CogT, P, T]): ...

def hybrid_command() -> Callable[[CommandCallback[CogT, ContextT, P, T]], HybridCommand[CogT, P, T]]:
    def decorator(func: CommandCallback[CogT, ContextT, P, T]) -> HybridCommand[CogT, P, T]:
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return HybridCommand()

    return decorator

class Test(Cog):
    @hybrid_command()
    async def t(self, ctx: Context, *args): ... # No errors

    @hybrid_command()
    async def t_any(self, ctx: Context[Any], *args): ... # No errors

    @hybrid_command()
    async def t_err(self, ctx: Context[Bot], *args): ... # Errors out
