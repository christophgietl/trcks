# Frequently asked questions (FAQs)

This page answers some questions that might come to mind.

## Where can I learn more about railway-oriented programming (ROP)?

Scott Wlaschin's blog post
[Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
comes with many examples and illustrations as well as
videos and slides from his talks.

## Should I replace all raised exceptions with `trcks.Result` values?

No, you should not.
Scott Wlaschin's blog post
[Against Railway-Oriented Programming](https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/)
lists eight scenarios
where a result type is not the right tool.
Raising an exception, catching an exception, or
returning an optional value are often better choices.

## Why does `trcks` arrange its types, monads, and wrappers as `Awaitable` > `Result` > `tuple`?

`trcks` provides generic types based on the sequence
`Awaitable` > `Result` > `tuple` and its subsequences
(e.g. [trcks.AwaitableResultTuple][], [trcks.AwaitableResult][],
[trcks.ResultTuple][], and [trcks.Result][]).
It also provides matching monads and matching wrapper classes.
It does not provide types, monads, or wrapper classes based on permutations
such as `Result` > `Awaitable` > `tuple`.

The reason is that the sequence `Awaitable` > `Result` > `tuple`
mirrors the behavior of a conventional asynchronous Python function
that returns a tuple and raises exceptions.
Each layer corresponds to one trait of such a function,
and the outer-to-inner order matches the order
in which the caller unwraps the value:

1. The function is asynchronous, so the caller awaits it (`Awaitable`).
2. Awaiting either yields a value or raises an exception,
   so `trcks` models this as success or failure (`Result`).
3. In the success case, the function returns a homogeneous tuple,
   so the caller processes the tuple elements (`tuple`).

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
    >>>
    >>> # The trcks equivalent returns the failure instead of raising it.
    >>> # Calling it returns an AwaitableResultTuple.
    >>> # Awaiting that returns a ResultTuple:
    >>> async def read_scores_rop(user_id: int) -> ResultTuple[str, int]:
    ...     await asyncio.sleep(0.001)
    ...     if user_id != 1:
    ...         return "failure", "User does not exist"
    ...     return "success", (90, 85, 100)
    >>>
    >>> async def main() -> None:
    ...     a_rslt: AwaitableResultTuple[str, int] = read_scores_rop(2)
    ...     rslt: ResultTuple[str, int] = await a_rslt
    ...     print(rslt)
    >>>
    >>> asyncio.run(main())
    ('failure', 'User does not exist')

    ```

## Which static type checkers does `trcks` support?

`trcks` is compatible with current versions of `mypy`, `pyrefly`, and `pyright`.
For setup instructions, see
[Setting up a compatible static type checker](setup.md#setting-up-a-compatible-static-type-checker).

Other type checkers may also work.

## What makes `trcks` different from other Python libraries for type-safe ROP?

`trcks` differs from other libraries for type-safe ROP in four main ways:

- **Plain values, no imports:**
  The type [trcks.Result][] is a mere type alias that combines [tuple][]
  and [typing.Literal][].
  You can create values as easily as `("failure", whatever_you_like)` or
  `("success", whatever_you_like)`.
  You do not need any imports for this.
  You can even avoid the import of [trcks.Result][] by
  importing `Literal` from `typing` and
  replacing `trcks.Result[F, S]` with
  `tuple[Literal["failure"], F] | tuple[Literal["success"], S]`.
- **Two equivalent APIs, no logic in the type:**
  As a type alias, [trcks.Result][] contains no logic.
  All logic therefore lives outside the type, which allows `trcks` to offer
  two distinct but equivalent APIs:
  [trcks.oop][] offers a method chaining API, and
  [trcks.fp][] offers a function composition API.
  Both APIs are comprehensive.
  Each of them handles plain values and values of types
  [collections.abc.Awaitable][], [trcks.Result][],
  homogeneous [tuple][], and
  [combinations thereof](#why-does-trcks-arrange-its-types-monads-and-wrappers-as-awaitable-result-tuple).
- **Descriptive names, no jargon:**
  `trcks` avoids functional programming jargon outside the [trcks.fp][]
  subpackage.
  Class and method names in [trcks.oop][] are descriptive and
  self-explanatory.
  Take [trcks.oop.TupleWrapper.map_to_awaitable_result][], for example.
  Even inside [trcks.fp][], `trcks` uses the terminology coined in
  [trcks.oop][] rather than functional programming jargon
  (e.g. [trcks.fp.monads.tuple_.map_to_awaitable_result][]).
  This makes adopting `trcks` and switching between [trcks.oop][]
  and [trcks.fp][] as easy as possible.
- **Extra arguments, no boilerplate:**
  The `map*` and `tap*` functions in the modules under [trcks.fp.monads][]
  and the `map*` and `tap*` methods of the wrapper classes in [trcks.oop][]
  accept extra positional and keyword arguments
  and forward them to the given function.
  Take [trcks.fp.monads.result.map_success][] and
  [trcks.oop.ResultWrapper.map_success][], for example.
  You do not need a lambda or [functools.partial][] merely to bind
  an extra argument.

## Which alternatives to `trcks` are there?

Both of the following libraries represent failures and successes with
container classes rather than with the plain type alias [trcks.Result][]
(see the previous section).

[returns](https://pypi.org/project/returns/) supports
object-oriented style and functional style (like `trcks`).
It provides
the [returns.result.Result][] container (and multiple other containers)
for synchronous code and
the [returns.future.Future][] and [returns.future.FutureResult][] containers
for asynchronous code.
The [returns.result.Result][] container serves the same purpose as
[trcks.Result][].
The [returns.future.Future][] container deviates from
[collections.abc.Awaitable][], and the
[returns.future.FutureResult][] container deviates from
[trcks.AwaitableResult][].
Further differences between `returns` and `trcks`:

- `returns` offers
  [do notation](https://returns.readthedocs.io/en/0.28.0/pages/do-notation.html)
  and
  [dependency injection](https://returns.readthedocs.io/en/0.28.0/pages/context.html).
- The authors of `returns`
  [recommend using `mypy`](https://returns.readthedocs.io/en/0.28.0/pages/quickstart.html#typechecking-and-other-integrations)
  along with
  [their suggested `mypy` configuration](https://returns.readthedocs.io/en/0.28.0/pages/contrib/mypy_plugins.html#configuration)
  and
  [their custom `mypy` plugin](https://returns.readthedocs.io/en/0.28.0/pages/contrib/mypy_plugins.html#mypy-plugin),
  whereas `trcks` works with plain `mypy`, `pyrefly`, and `pyright`.

[Expression](https://pypi.org/project/Expression/) supports
object-oriented style ("fluent syntax") and
functional style (like `trcks`).
It provides the [expression.core.result.Ok][] and
[expression.core.result.Error][] case classes
(and multiple other container classes)
for synchronous code and
the [expression.effect.async_result][] builder
for asynchronous code.
The `Result` type is the union of the `Ok` and `Error` case classes.
The case classes combine the roles of
[trcks.Result][] and [trcks.oop.ResultWrapper][].
`Expression` works with standard type checkers such as `pyright`
and needs no plugins.

## Which libraries have inspired `trcks`?

The Python libraries mentioned in the previous section and
the TypeScript library [fp-ts](https://www.npmjs.com/package/fp-ts)
have inspired `trcks` the most.

## Where can I find examples for using `trcks`?

The repository [trcks-example-cyclopts](https://github.com/christophgietl/trcks-example-cyclopts)
contains an example CLI application that uses `trcks` along with
[cyclopts](https://pypi.org/project/cyclopts/).

The repository [trcks-example-fastapi](https://github.com/christophgietl/trcks-example-fastapi)
contains an example backend application that uses `trcks` along with
[FastAPI](https://pypi.org/project/fastapi/).
