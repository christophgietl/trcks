# Frequently asked questions (FAQs)

This section answers some questions that might come to your mind.

## Where can I learn more about railway-oriented programming?

Scott Wlaschin's blog post
[Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
comes with lots of examples and illustrations as well as
videos and slides from his talks.

## Should I replace all raised exceptions with [trcks.Result][]?

No, you should not.
Scott Wlaschin's blog post
[Against Railway-Oriented Programming](https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/)
lists eight scenarios
where raising or not catching an exception is the better choice.

## Why does `trcks` arrange its types, monads, and wrappers as `Awaitable` > `Result` > `tuple`?

`trcks` provides generic types based on the sequence
`Awaitable` > `Result` > `tuple` and its subsequences
(e.g. [trcks.AwaitableResultTuple][], [trcks.AwaitableResult][],
[trcks.ResultTuple][], and [trcks.Result][]).
It also provides matching monads and matching wrapper classes.
It does not provide types, monads, or wrapper classes based on permutations
such as `Result` > `Awaitable` > `tuple`.

The reason is that the sequence `Awaitable` > `Result` > `tuple`
mirrors the behavior of a tuple-returning and exception-raising
asynchronous function in conventional Python.
Each layer corresponds to one trait of such a function,
and the outer-to-inner order matches the order
in which the caller unwraps the value:

1. The function is asynchronous, so the caller awaits it first (`Awaitable`).
2. The function may raise an exception when it is awaited,
   so the caller handles success or failure around that await (`Result`).
3. The function returns a homogeneous tuple,
   so the caller finally processes the tuple elements (`tuple`).

A permutation like `Result` > `Awaitable` > `tuple`
would describe a synchronous function
that returns either a failure or an awaitable tuple.
This does not match the conventional Python pattern,
so `trcks` does not provide it.

???+ example

    ```pycon
    >>> import asyncio
    >>> from trcks import AwaitableResultTuple, ResultTuple
    >>>
    >>> # A conventional asynchronous function that returns a tuple
    >>> # or raises a ValueError looks like this:
    >>> async def read_scores(user_id: int) -> tuple[int, ...]:
    ...     await asyncio.sleep(0.001)
    ...     if user_id != 1:
    ...         raise ValueError("User does not exist")
    ...     return (90, 85, 100)
    ...
    >>> # The trcks equivalent returns the failure instead of raising it.
    >>> # Calling it returns an AwaitableResultTuple.
    >>> # And awaiting that returns a ResultTuple:
    >>> async def read_scores_rop(user_id: int) -> ResultTuple[str, int]:
    ...     await asyncio.sleep(0.001)
    ...     if user_id != 1:
    ...         return "failure", "User does not exist"
    ...     return "success", (90, 85, 100)
    ...
    >>> async def main() -> None:
    ...     a_rslt: AwaitableResultTuple[str, int] = read_scores_rop(2)
    ...     rslt: ResultTuple[str, int] = await a_rslt
    ...     print(rslt)
    ...
    >>> asyncio.run(main())
    ('failure', 'User does not exist')

    ```

## Which static type checkers does `trcks` support?

`trcks` is compatible with current versions of `mypy`, `pyrefly`, and `pyright`.
For setup instructions, see
[Setting up a compatible static type checker](setup.md#setting-up-a-compatible-static-type-checker).

Other type checkers may also work.

???+ note

    Unlike `mypy` and `pyright`, `pyrefly` (as of version 1.0.0)
    does not reliably narrow [trcks.Result][] types in `match` statements:

    ```python
    from typing_extensions import reveal_type

    from trcks import Result


    def f(rslt: Result[str, int]) -> None:
        match rslt:
            case "failure", description:
                reveal_type(description)  # revealed type: int | str
            case "success", n:
                reveal_type(n)  # revealed type: int | str
    ```

    This can be resolved by adopting a different pattern matching style
    (or by using `if` statements):

    ```python
    from typing_extensions import reveal_type

    from trcks import Result


    def f(rslt: Result[str, int]) -> None:
        match rslt[0]:
            case "failure":
                reveal_type(rslt[1])  # revealed type: str
            case "success":
                reveal_type(rslt[1])  # revealed type: int
    ```

## Which alternatives to `trcks` are there?

[returns](https://pypi.org/project/returns/) supports
object-oriented style and functional style (like `trcks`).
It provides
the [returns.result.Result][] container (and multiple other containers)
for synchronous code and
the [returns.future.Future][] and the [returns.future.FutureResult][] container
for asynchronous code.
Whereas the [returns.result.Result][] container is pretty similar to
[trcks.Result][], the [returns.future.Future][] container and the
[returns.future.FutureResult][] container
deviate from [collections.abc.Awaitable][] and [trcks.AwaitableResult][].
Other major differences are:

- `returns` provides
  [do notation](https://returns.readthedocs.io/en/0.25.0/pages/do-notation.html)
  and
  [dependency injection](https://returns.readthedocs.io/en/0.25.0/pages/context.html).
- The authors of `returns`
  [recommend using `mypy`](https://returns.readthedocs.io/en/0.25.0/pages/quickstart.html#typechecking-and-other-integrations)
  along with
  [their suggested `mypy` configuration](https://returns.readthedocs.io/en/0.25.0/pages/contrib/mypy_plugins.html#configuration)
  and
  [their custom `mypy` plugin](https://returns.readthedocs.io/en/0.25.0/pages/contrib/mypy_plugins.html#mypy-plugin).

[Expression](https://pypi.org/project/Expression/) supports
object-oriented style ("fluent syntax") and
functional style (like `trcks`).
It provides the [expression.core.result.Result][] class
(and multiple other container classes)
for synchronous code.
The [expression.core.result.Result][] class is pretty similar to
[trcks.Result][] and [trcks.oop.ResultWrapper][].
An `AsyncResult` type based on [collections.abc.AsyncGenerator][]
[will be added in a future version](https://github.com/dbrattli/Expression/pull/247).

## Which libraries have inspired `trcks`?

`trcks` is mostly inspired
by the Python libraries mentioned in the previous section and
by the TypeScript library [fp-ts](https://www.npmjs.com/package/fp-ts).

## Where can I find examples for using `trcks`?

The repository [trcks-example-cyclopts](https://github.com/christophgietl/trcks-example-cyclopts)
contains an example CLI application that uses `trcks` along with
[cyclopts](https://pypi.org/project/cyclopts/).

The repository [trcks-example-fastapi](https://github.com/christophgietl/trcks-example-fastapi)
contains an example backend application that uses `trcks` along with
[FastAPI](https://pypi.org/project/fastapi/).
