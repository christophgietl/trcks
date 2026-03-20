# Railway-oriented programming with [trcks.fp][]

This page describes how to use [trcks.fp][] for railway-oriented programming.
Single-track and double-track code are both discussed.
So are synchronous and asynchronous code.

## Synchronous single-track code with [trcks.fp.composition][]

The function [trcks.fp.composition.pipe][] allows us to chain functions:

???+ example

    >>> from trcks.fp.composition import pipe
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return pipe((s, len, lambda n: f"Length: {n}"))
    ...
    >>> to_length_string("Hello, world!")
    'Length: 13'

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> pipe(("Hello, world!",))
    'Hello, world!'
    >>> pipe(("Hello, world!", len))
    13
    >>> pipe(("Hello, world!", len, lambda n: f"Length: {n}"))
    'Length: 13'

???+ note
    The function [trcks.fp.composition.pipe][] expects a [trcks.fp.composition.Pipeline][],
    i.e. a tuple consisting of a start value followed by up to seven compatible functions.

Side effects like logging or writing to a file tend to
"consume" their input and return [None][] instead.
To avoid this, we can use the higher-order function [trcks.fp.monads.identity.tap][].
This higher-order function turns each function into a function
that behaves like the original function but returns the input value.

???+ example

    >>> from trcks.fp.monads import identity as i
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return pipe(
    ...         (
    ...             s,
    ...             i.tap(lambda o: print(f"LOG: Received '{o}'.")),
    ...             len,
    ...             lambda n: f"Length: {n}",
    ...             i.tap(lambda o: print(f"LOG: Returning '{o}'.")),
    ...         ),
    ...     )
    ...
    >>> output = to_length_string("Hello, world!")
    LOG: Received 'Hello, world!'.
    LOG: Returning 'Length: 13'.
    >>> output
    'Length: 13'

## Synchronous double-track code with [trcks.fp.composition][] and [trcks.fp.monads.result][]

If one of the functions in a [trcks.fp.composition.Pipeline][]
returns a `trcks.Result[F, S]` type,
the following function must accept this `trcks.Result[F, S]` type as its input.
However, functions with input type `trcks.Result[F, S]` tend to violate
the "do one thing and do it well" principle.
Therefore, the module [trcks.fp.monads.result][] provides
some higher-order functions named `map_*`
that turn functions with input type `F` and functions with input type `S`
into functions with input type `trcks.Result[F, S]`.

???+ example

    >>> from typing import Literal
    >>> from trcks import Result
    >>> from trcks.fp.monads import result as r
    >>>
    >>> UserDoesNotExist = Literal["User does not exist"]
    >>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
    >>> FailureDescription = UserDoesNotExist | UserDoesNotHaveASubscription
    >>>
    >>> def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
    ...     if user_email == "erika.mustermann@domain.org":
    ...         return "success", 1
    ...     if user_email == "john_doe@provider.com":
    ...         return "success", 2
    ...     return "failure", "User does not exist"
    ...
    >>> def get_subscription_id(
    ...     user_id: int
    ... ) -> Result[UserDoesNotHaveASubscription, int]:
    ...     if user_id == 1:
    ...         return "success", 42
    ...     return "failure", "User does not have a subscription"
    ...
    >>> def get_subscription_fee(subscription_id: int) -> float:
    ...     return subscription_id * 0.1
    ...
    >>> def get_subscription_fee_by_email(
    ...     user_email: str
    ... ) -> Result[FailureDescription, float]:
    ...     # Explicitly assigning a type to `pipeline` might
    ...     # help your static type checker understand that
    ...     # `pipeline` is a valid argument for `pipe`:
    ...     pipeline: Pipeline3[
    ...         str,
    ...         Result[UserDoesNotExist, int],
    ...         Result[FailureDescription, int],
    ...         Result[FailureDescription, float],
    ...     ] = (
    ...         user_email,
    ...         get_user_id,
    ...         r.map_success_to_result(get_subscription_id),
    ...         r.map_success(get_subscription_fee),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> get_subscription_fee_by_email("erika.mustermann@domain.org")
    ('success', 4.2)
    >>> get_subscription_fee_by_email("john_doe@provider.com")
    ('failure', 'User does not have a subscription')
    >>> get_subscription_fee_by_email("jane_doe@provider.com")
    ('failure', 'User does not exist')

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> from trcks.fp.composition import (
    ...     Pipeline0, Pipeline1, Pipeline2, Pipeline3, pipe
    ... )
    >>>
    >>> p0: Pipeline0[str] = ("erika.mustermann@domain.org",)
    >>> pipe(p0)
    'erika.mustermann@domain.org'
    >>>
    >>> p1: Pipeline1[str, Result[UserDoesNotExist, int]] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ... )
    >>> pipe(p1)
    ('success', 1)
    >>>
    >>> p2: Pipeline2[
    ...     str, Result[UserDoesNotExist, int], Result[FailureDescription, int]
    ... ] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ...     r.map_success_to_result(get_subscription_id),
    ... )
    >>> pipe(p2)
    ('success', 42)
    >>>
    >>> p3: Pipeline3[
    ...     str,
    ...     Result[UserDoesNotExist, int],
    ...     Result[FailureDescription, int],
    ...     Result[FailureDescription, float],
    ... ] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ...     r.map_success_to_result(get_subscription_id),
    ...     r.map_success(get_subscription_fee),
    ... )
    >>> pipe(p3)
    ('success', 4.2)

While [trcks.fp.monads.result.map_failure][] and [trcks.fp.monads.result.map_success][]
allow us to apply functions in the failure case or in the success case, respectively,
the higher-order functions [trcks.fp.monads.result.tap_failure][] and [trcks.fp.monads.result.tap_success][]
allow us to execute side effects in the failure case or in the success case, respectively.

???+ example

    >>> from trcks.fp.composition import Pipeline6
    >>>
    >>> def get_subscription_fee_by_email(
    ...     user_email: str
    ... ) -> Result[FailureDescription, float]:
    ...     pipeline: Pipeline6[
    ...         str,
    ...         Result[UserDoesNotExist, int],
    ...         Result[UserDoesNotExist, int],
    ...         Result[FailureDescription, int],
    ...         Result[FailureDescription, float],
    ...         Result[FailureDescription, float],
    ...         Result[FailureDescription, float],
    ...     ] = (
    ...         user_email,
    ...         get_user_id,
    ...         r.tap_success(lambda n: print(f"LOG: User ID: {n}.")),
    ...         r.map_success_to_result(get_subscription_id),
    ...         r.map_success(get_subscription_fee),
    ...         r.tap_success(lambda x: print(f"LOG: Subscription fee: {x}.")),
    ...         r.tap_failure(lambda fd: print(f"LOG: Failure description: {fd}.")),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> fee_erika = get_subscription_fee_by_email("erika.mustermann@domain.org")
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fee_erika
    ('success', 4.2)
    >>>
    >>> fee_john = get_subscription_fee_by_email("john_doe@provider.com")
    LOG: User ID: 2.
    LOG: Failure description: User does not have a subscription.
    >>> fee_john
    ('failure', 'User does not have a subscription')
    >>>
    >>> fee_jane = get_subscription_fee_by_email("jane_doe@provider.com")
    LOG: Failure description: User does not exist.
    >>> fee_jane
    ('failure', 'User does not exist')

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] value.
The higher-order function [trcks.fp.monads.result.tap_success_to_result][]
allows us to execute such side effects in the success case.
If the side effect returns a [trcks.Failure][], that failure is propagated.
If the side effect returns a [trcks.Success][], the original success value is preserved.

???+ example

    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>>
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    ...
    >>> def get_and_persist_user_id(
    ...     user_email: str
    ... ) -> Result[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     pipeline: Pipeline2[
    ...         str,
    ...         Result[UserDoesNotExist, int],
    ...         Result[UserDoesNotExist | OutOfDiskSpace, int],
    ...     ] = (
    ...         user_email,
    ...         get_user_id,
    ...         r.tap_success_to_result(write_to_disk),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> id_erika = get_and_persist_user_id("erika.mustermann@domain.org")
    LOG: Wrote 1 to disk.
    >>> id_erika
    ('success', 1)
    >>>
    >>> id_john = get_and_persist_user_id("john_doe@provider.com")
    >>> id_john
    ('failure', 'Out of disk space')
    >>>
    >>> id_jane = get_and_persist_user_id("jane_doe@provider.com")
    >>> id_jane
    ('failure', 'User does not exist')

## Asynchronous single-track code with [trcks.fp.composition][] and [trcks.fp.monads.awaitable][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a `collections.abc.Awaitable[T]` type,
the following function must accept this `collections.abc.Awaitable[T]` type
as its input.
However, functions with input type `collections.abc.Awaitable[T]`
tend to contain unnecessary `await` statements.
Therefore, the module [trcks.fp.monads.awaitable][] provides
some higher-order functions named `map_*`
that turn functions with input type `T`
into functions with input type `collections.abc.Awaitable[T]`.

???+ example

    >>> import asyncio
    >>> from collections.abc import Awaitable
    >>> from trcks.fp.monads import awaitable as a
    >>>
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     s = "Hello, world!"
    ...     print(f"Read '{s}' from file {path}.")
    ...     return s
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def write_to_disk(s: str, path: str) -> None:
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{s}' to file {path}.")
    ...
    >>> async def read_and_transform_and_write(
    ...     input_path: str, output_path: str
    ... ) -> None:
    ...     p: Pipeline3[
    ...         str, Awaitable[str], Awaitable[str], Awaitable[None]
    ...     ] = (
    ...         input_path,
    ...         read_from_disk,
    ...         a.map_(transform),
    ...         a.map_to_awaitable(lambda s: write_to_disk(s, output_path)),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> p1: Pipeline1[str, Awaitable[str]] = (
    ...     "input.txt",
    ...     read_from_disk,
    ... )
    >>> asyncio.run(a.to_coroutine(pipe(p1)))
    Read 'Hello, world!' from file input.txt.
    'Hello, world!'
    >>>
    >>> p2: Pipeline2[str, Awaitable[str], Awaitable[str]] = (
    ...     "input.txt",
    ...     read_from_disk,
    ...     a.map_(transform),
    ... )
    >>> asyncio.run(a.to_coroutine(pipe(p2)))
    Read 'Hello, world!' from file input.txt.
    'Length: 13'
    >>>
    >>> p3: Pipeline3[str, Awaitable[str], Awaitable[str], Awaitable[None]] = (
    ...     "input.txt",
    ...     read_from_disk,
    ...     a.map_(transform),
    ...     a.map_to_awaitable(lambda s: write_to_disk(s, "output.txt")),
    ... )
    >>> asyncio.run(a.to_coroutine(pipe(p3)))
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.

???+ note
    The values `pipe(p1)`, `pipe(p2)` and `pipe(p3)` are all of the type [collections.abc.Awaitable][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function [trcks.fp.monads.awaitable.to_coroutine][] to convert
    the [collections.abc.Awaitable][]s to [collections.abc.Coroutine][]s.

The higher-order function [trcks.fp.monads.awaitable.tap][]
allows us to execute synchronous side effects.
Similarly, the higher-order function [trcks.fp.monads.awaitable.tap_to_awaitable][]
allows us to execute asynchronous side effects.

???+ example

    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     return "Hello, world!"
    ...
    >>> async def write_to_disk(s: str, path: str) -> None:
    ...     await asyncio.sleep(0.001)
    ...
    >>> async def read_and_transform_and_write(
    ...     input_path: str, output_path: str
    ... ) -> str:
    ...     p: Pipeline5[
    ...         str,
    ...         Awaitable[str],
    ...         Awaitable[str],
    ...         Awaitable[str],
    ...         Awaitable[str],
    ...         Awaitable[str],
    ...     ] = (
    ...         input_path,
    ...         read_from_disk,
    ...         a.tap(lambda s: print(f"Read '{s}' from disk.")),
    ...         a.map_(transform),
    ...         a.tap_to_awaitable(lambda s: write_to_disk(s, output_path)),
    ...         a.tap(lambda s: print(f"Wrote '{s}' to disk.")),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    Read 'Hello, world!' from disk.
    Wrote 'Length: 13' to disk.
    'Length: 13'

## Asynchronous double-track code with [trcks.fp.composition][] and [trcks.fp.monads.awaitable_result][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a `trcks.AwaitableResult[F, S]` type,
the following function must accept this `trcks.AwaitableResult[F, S]` type
as its input.
However, functions with input type `trcks.AwaitableResult[F, S]` tend to
contain unnecessary `await` statements and
violate the "do one thing and do it well" principle.
Therefore, the module [trcks.fp.monads.awaitable_result][] provides
some higher-order functions named `map_*`
that turn functions with input type `F` and functions with input type `S`
into functions with input type `trcks.AwaitableResult[F, S]`.

???+ example

    >>> from trcks.fp.monads import awaitable_result as ar
    >>>
    >>> ReadErrorLiteral = Literal["read error"]
    >>> WriteErrorLiteral = Literal["write error"]
    >>>
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "input.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     s = "Hello, world!"
    ...     print(f"Read '{s}' from file {path}.")
    ...     return "success", s
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{s}' to file {path}.")
    ...     return "success", None
    ...
    >>> async def read_and_transform_and_write(
    ...     input_path: str, output_path: str
    ... ) -> Result[ReadErrorLiteral | WriteErrorLiteral, None]:
    ...     p: Pipeline3[
    ...         str,
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral | WriteErrorLiteral, None],
    ...     ] = (
    ...         input_path,
    ...         read_from_disk,
    ...         ar.map_success(transform),
    ...         ar.map_success_to_awaitable_result(lambda s: write_to_disk(s, output_path)),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.
    ('success', None)

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> from trcks import AwaitableResult, Result
    >>>
    >>> p1: Pipeline1[str, AwaitableResult[ReadErrorLiteral, str]] = (
    ...     "input.txt",
    ...     read_from_disk,
    ... )
    >>> asyncio.run(ar.to_coroutine_result(pipe(p1)))
    Read 'Hello, world!' from file input.txt.
    ('success', 'Hello, world!')
    >>>
    >>> p2: Pipeline2[
    ...     str,
    ...     AwaitableResult[ReadErrorLiteral, str],
    ...     AwaitableResult[ReadErrorLiteral, str],
    ... ] = (
    ...     "input.txt",
    ...     read_from_disk,
    ...     ar.map_success(transform),
    ... )
    >>> asyncio.run(ar.to_coroutine_result(pipe(p2)))
    Read 'Hello, world!' from file input.txt.
    ('success', 'Length: 13')
    >>>
    >>> p3: Pipeline3[
    ...     str,
    ...     AwaitableResult[ReadErrorLiteral, str],
    ...     AwaitableResult[ReadErrorLiteral, str],
    ...     AwaitableResult[ReadErrorLiteral | WriteErrorLiteral, None],
    ... ] = (
    ...     "input.txt",
    ...     read_from_disk,
    ...     ar.map_success(transform),
    ...     ar.map_success_to_awaitable_result(lambda s: write_to_disk(s, "output.txt")),
    ... )
    >>> asyncio.run(ar.to_coroutine_result(pipe(p3)))
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.
    ('success', None)

???+ note
    The values `pipe(p1)`, `pipe(p2)` and `pipe(p3)` all are
    of type [trcks.AwaitableResult][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function [trcks.fp.monads.awaitable_result.to_coroutine_result][]
    to convert the [trcks.AwaitableResult][]s to [collections.abc.Coroutine][]s.

The higher-order functions [trcks.fp.monads.awaitable_result.tap_failure][]
and [trcks.fp.monads.awaitable_result.tap_success][]
allow us to execute synchronous side effects
in the failure case or in the success case, respectively:

???+ example

    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "input.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     return "success", "Hello, world!"
    ...
    >>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     return "success", None
    ...
    >>> async def read_and_transform_and_write(
    ...     input_path: str, output_path: str
    ... ) -> Result[ReadErrorLiteral | WriteErrorLiteral, None]:
    ...     pipeline: Pipeline6[
    ...         str,
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral | WriteErrorLiteral, None],
    ...         AwaitableResult[ReadErrorLiteral | WriteErrorLiteral, None],
    ...         AwaitableResult[ReadErrorLiteral | WriteErrorLiteral, None],
    ...     ] = (
    ...         input_path,
    ...         read_from_disk,
    ...         ar.tap_success(lambda s: print(f"LOG: Read '{s}' from disk.")),
    ...         ar.map_success(transform),
    ...         ar.map_success_to_awaitable_result(lambda s: write_to_disk(s, output_path)),
    ...         ar.tap_success(lambda _: print(f"LOG: Successfully wrote to disk.")),
    ...         ar.tap_failure(lambda err: print(f"LOG: Failed with error: {err}")),
    ...     )
    ...     return await pipe(pipeline)
    ...
    >>> result_1 = asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    LOG: Read 'Hello, world!' from disk.
    LOG: Successfully wrote to disk.
    >>> result_1
    ('success', None)
    >>>
    >>> result_2 = asyncio.run(read_and_transform_and_write("missing.txt", "output.txt"))
    LOG: Failed with error: read error
    >>> result_2
    ('failure', 'read error')

Sometimes, side effects themselves can fail and
need to return an [trcks.AwaitableResult][] type.
The higher-order function [trcks.fp.monads.awaitable_result.tap_success_to_awaitable_result][]
allows us to execute such asynchronous side effects in the success case.
If the side effect returns an [trcks.AwaitableFailure][], that failure is propagated.
If the side effect returns an [trcks.AwaitableSuccess][],
the original success value is preserved:

???+ example

    >>> async def write_to_disk(s: str) -> Result[OutOfDiskSpace, None]:
    ...     await asyncio.sleep(0.001)
    ...     if len(s) > 10:
    ...         return "failure", "Out of disk space"
    ...     return "success", None
    ...
    >>> async def read_and_persist(
    ...     input_path: str
    ... ) -> Result[ReadErrorLiteral | OutOfDiskSpace, str]:
    ...     pipeline: Pipeline3[
    ...         str,
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral, str],
    ...         AwaitableResult[ReadErrorLiteral | OutOfDiskSpace, str],
    ...     ] = (
    ...         input_path,
    ...         read_from_disk,
    ...         ar.tap_success(lambda s: print(f"LOG: Persisting '{s}'.")),
    ...         ar.tap_success_to_awaitable_result(write_to_disk),
    ...     )
    ...     return await pipe(pipeline)
    ...
    >>> result = asyncio.run(read_and_persist("input.txt"))
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')

## Synchronous single-track code with [trcks.fp.composition][] and [trcks.fp.monads.sequence][]

If we want to apply a pipeline of functions to each element
in a [collections.abc.Sequence][],
the module [trcks.fp.monads.sequence][] provides
some higher-order functions named `map_*` and `tap`
that turn element-wise functions into functions
operating on entire sequences.

???+ example

    >>> from collections.abc import Sequence
    >>> from trcks.fp.monads import sequence as s
    >>>
    >>> def normalize_email(email: str) -> str:
    ...     return email.strip().lower()
    ...
    >>> def to_domain(email: str) -> str:
    ...     return email.split("@")[1]
    ...
    >>> def get_domains(emails: list[str]) -> Sequence[str]:
    ...     pipeline: Pipeline2[
    ...         Sequence[str],
    ...         Sequence[str],
    ...         Sequence[str],
    ...     ] = (
    ...         emails,
    ...         s.map_(normalize_email),
    ...         s.map_(to_domain),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> get_domains(["  Erika@Domain.ORG ", "JOHN@Provider.COM  "])
    ['domain.org', 'provider.com']

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> from collections.abc import Sequence
    >>>
    >>> emails: list[str] = ["  Erika@Domain.ORG ", "JOHN@Provider.COM  "]
    >>>
    >>> p0: Pipeline0[list[str]] = (emails,)
    >>> pipe(p0)
    ['  Erika@Domain.ORG ', 'JOHN@Provider.COM  ']
    >>>
    >>> p1: Pipeline1[list[str], Sequence[str]] = (
    ...     emails,
    ...     s.map_(normalize_email),
    ... )
    >>> pipe(p1)
    ['erika@domain.org', 'john@provider.com']
    >>>
    >>> p2: Pipeline2[list[str], Sequence[str], Sequence[str]] = (
    ...     emails,
    ...     s.map_(normalize_email),
    ...     s.map_(to_domain),
    ... )
    >>> pipe(p2)
    ['domain.org', 'provider.com']

???+ note
    The higher-order function [trcks.fp.monads.sequence.map_to_sequence][]
    applies a function that returns a [collections.abc.Sequence][]
    to each element and flattens the results (like a "flat map"):

        >>> pipe(
        ...     (
        ...         ["ab", "cd"],
        ...         s.map_to_sequence(list),
        ...     )
        ... )
        ['a', 'b', 'c', 'd']

The higher-order function [trcks.fp.monads.sequence.tap][]
allows us to execute side effects for each element:

???+ example

    >>> def get_domains(emails: list[str]) -> Sequence[str]:
    ...     pipeline: Pipeline3[
    ...         list[str],
    ...         Sequence[str],
    ...         Sequence[str],
    ...         Sequence[str],
    ...     ] = (
    ...         emails,
    ...         s.map_(normalize_email),
    ...         s.tap(lambda e: print(f"LOG: Processing '{e}'.")),
    ...         s.map_(to_domain),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> result = get_domains(["  Erika@Domain.ORG ", "JOHN@Provider.COM  "])
    LOG: Processing 'erika@domain.org'.
    LOG: Processing 'john@provider.com'.
    >>> result
    ['domain.org', 'provider.com']

## Synchronous double-track code with [trcks.fp.composition][] and [trcks.fp.monads.result_sequence][]

If one of the functions in a [trcks.fp.composition.Pipeline][]
returns a [trcks.ResultSequence][][F, S] type,
the module [trcks.fp.monads.result_sequence][] provides
some higher-order functions named `map_successes*` and `tap_successes*`
that turn element-wise functions into functions
operating on [trcks.ResultSequence][] values.
The success track functions use the plural `map_successes` (instead of `map_success`)
because they operate on each element in the [trcks.SuccessSequence][] individually.
Processing short-circuits on the first [trcks.Failure][].

???+ example

    >>> from trcks import ResultSequence, SuccessSequence
    >>> from trcks.fp.monads import result_sequence as rs_
    >>>
    >>> UserDoesNotExist = Literal["User does not exist"]
    >>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
    >>> FailureDescription = UserDoesNotExist | UserDoesNotHaveASubscription
    >>>
    >>> def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
    ...     if user_email == "erika.mustermann@domain.org":
    ...         return "success", 1
    ...     if user_email == "john_doe@provider.com":
    ...         return "success", 2
    ...     return "failure", "User does not exist"
    ...
    >>> def get_subscription_id(
    ...     user_id: int
    ... ) -> Result[UserDoesNotHaveASubscription, int]:
    ...     if user_id == 1:
    ...         return "success", 42
    ...     return "failure", "User does not have a subscription"
    ...
    >>> def get_subscription_fee(subscription_id: int) -> float:
    ...     return subscription_id * 0.1
    ...
    >>> def get_subscription_fees_by_email(
    ...     user_emails: list[str],
    ... ) -> ResultSequence[FailureDescription, float]:
    ...     pipeline: Pipeline4[
    ...         list[str],
    ...         SuccessSequence[str],
    ...         ResultSequence[UserDoesNotExist, int],
    ...         ResultSequence[FailureDescription, int],
    ...         ResultSequence[FailureDescription, float],
    ...     ] = (
    ...         user_emails,
    ...         rs_.construct_successes_from_sequence,
    ...         rs_.map_successes_to_result(get_user_id),
    ...         rs_.map_successes_to_result(get_subscription_id),
    ...         rs_.map_successes(get_subscription_fee),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> get_subscription_fees_by_email(["erika.mustermann@domain.org"])
    ('success', [4.2])
    >>> get_subscription_fees_by_email(
    ...     ["erika.mustermann@domain.org", "john_doe@provider.com"]
    ... )
    ('failure', 'User does not have a subscription')
    >>> get_subscription_fees_by_email(["jane_doe@provider.com"])
    ('failure', 'User does not exist')

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> from trcks.fp.composition import Pipeline4
    >>>
    >>> p0: Pipeline0[list[str]] = (["erika.mustermann@domain.org"],)
    >>> pipe(p0)
    ['erika.mustermann@domain.org']
    >>>
    >>> p1: Pipeline1[
    ...     list[str],
    ...     SuccessSequence[str],
    ... ] = (
    ...     ["erika.mustermann@domain.org"],
    ...     rs_.construct_successes_from_sequence,
    ... )
    >>> pipe(p1)
    ('success', ['erika.mustermann@domain.org'])
    >>>
    >>> p2: Pipeline2[
    ...     list[str],
    ...     SuccessSequence[str],
    ...     ResultSequence[UserDoesNotExist, int],
    ... ] = (
    ...     ["erika.mustermann@domain.org"],
    ...     rs_.construct_successes_from_sequence,
    ...     rs_.map_successes_to_result(get_user_id),
    ... )
    >>> pipe(p2)
    ('success', [1])
    >>>
    >>> p3: Pipeline3[
    ...     list[str],
    ...     SuccessSequence[str],
    ...     ResultSequence[UserDoesNotExist, int],
    ...     ResultSequence[FailureDescription, int],
    ... ] = (
    ...     ["erika.mustermann@domain.org"],
    ...     rs_.construct_successes_from_sequence,
    ...     rs_.map_successes_to_result(get_user_id),
    ...     rs_.map_successes_to_result(get_subscription_id),
    ... )
    >>> pipe(p3)
    ('success', [42])
    >>>
    >>> p4: Pipeline4[
    ...     list[str],
    ...     SuccessSequence[str],
    ...     ResultSequence[UserDoesNotExist, int],
    ...     ResultSequence[FailureDescription, int],
    ...     ResultSequence[FailureDescription, float],
    ... ] = (
    ...     ["erika.mustermann@domain.org"],
    ...     rs_.construct_successes_from_sequence,
    ...     rs_.map_successes_to_result(get_user_id),
    ...     rs_.map_successes_to_result(get_subscription_id),
    ...     rs_.map_successes(get_subscription_fee),
    ... )
    >>> pipe(p4)
    ('success', [4.2])

???+ note
    The function [trcks.fp.monads.result_sequence.construct_successes_from_sequence][]
    wraps a [collections.abc.Sequence][] into a [trcks.SuccessSequence][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.result_sequence][].

    While [trcks.fp.monads.result.map_failure][]
    and [trcks.fp.monads.result.map_success][]
    operate on single-value [trcks.Result][] types,
    [trcks.fp.monads.result_sequence.map_successes][] (plural)
    operates on each element in the sequence.

The higher-order functions [trcks.fp.monads.result_sequence.tap_successes][]
and [trcks.fp.monads.result_sequence.tap_failure][]
allow us to execute side effects
in the success case (for each element) or in the failure case, respectively.

???+ example

    >>> def get_subscription_fees_by_email(
    ...     user_emails: list[str],
    ... ) -> ResultSequence[FailureDescription, float]:
    ...     pipeline: Pipeline7[
    ...         list[str],
    ...         SuccessSequence[str],
    ...         ResultSequence[UserDoesNotExist, int],
    ...         ResultSequence[UserDoesNotExist, int],
    ...         ResultSequence[FailureDescription, int],
    ...         ResultSequence[FailureDescription, float],
    ...         ResultSequence[FailureDescription, float],
    ...         ResultSequence[FailureDescription, float],
    ...     ] = (
    ...         user_emails,
    ...         rs_.construct_successes_from_sequence,
    ...         rs_.map_successes_to_result(get_user_id),
    ...         rs_.tap_successes(lambda n: print(f"LOG: User ID: {n}.")),
    ...         rs_.map_successes_to_result(get_subscription_id),
    ...         rs_.map_successes(get_subscription_fee),
    ...         rs_.tap_successes(lambda x: print(f"LOG: Subscription fee: {x}.")),
    ...         rs_.tap_failure(lambda fd: print(f"LOG: Failure: {fd}.")),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> fees_erika = get_subscription_fees_by_email(
    ...     ["erika.mustermann@domain.org"]
    ... )
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fees_erika
    ('success', [4.2])
    >>>
    >>> fees_john = get_subscription_fees_by_email(
    ...     ["john_doe@provider.com"]
    ... )
    LOG: User ID: 2.
    LOG: Failure: User does not have a subscription.
    >>> fees_john
    ('failure', 'User does not have a subscription')
    >>>
    >>> fees_jane = get_subscription_fees_by_email(
    ...     ["jane_doe@provider.com"]
    ... )
    LOG: Failure: User does not exist.
    >>> fees_jane
    ('failure', 'User does not exist')

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] value.
The higher-order function [trcks.fp.monads.result_sequence.tap_successes_to_result][]
allows us to execute such side effects for each element in the success case.
If the side effect returns a [trcks.Failure][] for any element,
that failure is propagated.
If the side effect returns a [trcks.Success][] for all elements,
the original success values are preserved.

???+ example

    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>>
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    ...
    >>> def get_and_persist_user_ids(
    ...     user_emails: list[str],
    ... ) -> ResultSequence[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     pipeline: Pipeline3[
    ...         list[str],
    ...         SuccessSequence[str],
    ...         ResultSequence[UserDoesNotExist, int],
    ...         ResultSequence[UserDoesNotExist | OutOfDiskSpace, int],
    ...     ] = (
    ...         user_emails,
    ...         rs_.construct_successes_from_sequence,
    ...         rs_.map_successes_to_result(get_user_id),
    ...         rs_.tap_successes_to_result(write_to_disk),
    ...     )
    ...     return pipe(pipeline)
    ...
    >>> ids_erika = get_and_persist_user_ids(["erika.mustermann@domain.org"])
    LOG: Wrote 1 to disk.
    >>> ids_erika
    ('success', [1])
    >>>
    >>> ids_john = get_and_persist_user_ids(["john_doe@provider.com"])
    >>> ids_john
    ('failure', 'Out of disk space')
    >>>
    >>> ids_jane = get_and_persist_user_ids(["jane_doe@provider.com"])
    >>> ids_jane
    ('failure', 'User does not exist')

## Asynchronous single-track code with [trcks.fp.composition][] and [trcks.fp.monads.awaitable_sequence][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a [trcks.AwaitableSequence][][T] type,
the following function must accept this [trcks.AwaitableSequence][][T] type
as its input.
The module [trcks.fp.monads.awaitable_sequence][] provides
some higher-order functions named `map_*`
that turn element-wise functions
into functions operating on [trcks.AwaitableSequence][] values.

???+ example

    >>> from trcks.fp.monads import awaitable_sequence as as_
    >>>
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return contents[path]
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def read_and_transform(
    ...     input_paths: list[str],
    ... ) -> Sequence[str]:
    ...     p: Pipeline3[
    ...         list[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...     ] = (
    ...         input_paths,
    ...         as_.construct_from_sequence,
    ...         as_.map_to_awaitable(read_from_disk),
    ...         as_.map_(transform),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(read_and_transform(["a.txt", "b.txt"]))
    ['Length: 5', 'Length: 5']

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> from trcks import AwaitableSequence
    >>>
    >>> p1: Pipeline1[list[str], AwaitableSequence[str]] = (
    ...     ["a.txt", "b.txt"],
    ...     as_.construct_from_sequence,
    ... )
    >>> asyncio.run(as_.to_coroutine_sequence(pipe(p1)))
    ['a.txt', 'b.txt']
    >>>
    >>> p2: Pipeline2[
    ...     list[str],
    ...     AwaitableSequence[str],
    ...     AwaitableSequence[str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     as_.construct_from_sequence,
    ...     as_.map_to_awaitable(read_from_disk),
    ... )
    >>> asyncio.run(as_.to_coroutine_sequence(pipe(p2)))
    ['Hello', 'World']
    >>>
    >>> p3: Pipeline3[
    ...     list[str],
    ...     AwaitableSequence[str],
    ...     AwaitableSequence[str],
    ...     AwaitableSequence[str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     as_.construct_from_sequence,
    ...     as_.map_to_awaitable(read_from_disk),
    ...     as_.map_(transform),
    ... )
    >>> asyncio.run(as_.to_coroutine_sequence(pipe(p3)))
    ['Length: 5', 'Length: 5']

???+ note
    The function [trcks.fp.monads.awaitable_sequence.construct_from_sequence][]
    wraps a [collections.abc.Sequence][] into
    an [trcks.AwaitableSequence][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.awaitable_sequence][].

    The values `pipe(p1)`, `pipe(p2)` and `pipe(p3)` are all
    of type [trcks.AwaitableSequence][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function
    [trcks.fp.monads.awaitable_sequence.to_coroutine_sequence][]
    to convert the [trcks.AwaitableSequence][]s
    to [collections.abc.Coroutine][]s.

The higher-order function [trcks.fp.monads.awaitable_sequence.tap][]
allows us to execute synchronous side effects for each element.
Similarly, the higher-order function
[trcks.fp.monads.awaitable_sequence.tap_to_awaitable][]
allows us to execute asynchronous side effects for each element.

???+ example

    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return contents[path]
    ...
    >>> async def read_and_transform(
    ...     input_paths: list[str],
    ... ) -> Sequence[str]:
    ...     p: Pipeline5[
    ...         list[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...         AwaitableSequence[str],
    ...     ] = (
    ...         input_paths,
    ...         as_.construct_from_sequence,
    ...         as_.map_to_awaitable(read_from_disk),
    ...         as_.tap(lambda s: print(f"Read '{s}' from disk.")),
    ...         as_.map_(transform),
    ...         as_.tap(lambda s: print(f"Transformed to '{s}'.")),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(read_and_transform(["a.txt", "b.txt"]))
    Read 'Hello' from disk.
    Read 'World' from disk.
    Transformed to 'Length: 5'.
    Transformed to 'Length: 5'.
    ['Length: 5', 'Length: 5']

## Asynchronous double-track code with [trcks.fp.composition][] and [trcks.fp.monads.awaitable_result_sequence][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a [trcks.AwaitableResultSequence][][F, S] type,
the module [trcks.fp.monads.awaitable_result_sequence][] provides
some higher-order functions named `map_successes*` and `tap_successes*`
that turn element-wise functions into functions
operating on [trcks.AwaitableResultSequence][] values.
The success track functions use the plural `map_successes` (instead of `map_success`)
because they operate on each element individually.
Processing short-circuits on the first [trcks.Failure][].

???+ example

    >>> from trcks import AwaitableResultSequence, AwaitableSuccessSequence
    >>> from trcks.fp.monads import awaitable_result_sequence as ars
    >>>
    >>> ReadErrorLiteral = Literal["read error"]
    >>> WriteErrorLiteral = Literal["write error"]
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return "success", contents[path]
    ...
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    ...
    >>> async def write_to_disk(
    ...     s: str, path: str
    ... ) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{s}' to file {path}.")
    ...     return "success", None
    ...
    >>> async def read_and_transform_and_write(
    ...     input_paths: list[str], output_path: str
    ... ) -> ResultSequence[ReadErrorLiteral | WriteErrorLiteral, str]:
    ...     p: Pipeline4[
    ...         list[str],
    ...         AwaitableSuccessSequence[str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral | WriteErrorLiteral, str],
    ...     ] = (
    ...         input_paths,
    ...         ars.construct_successes_from_sequence,
    ...         ars.map_successes_to_awaitable_result(read_from_disk),
    ...         ars.map_successes(transform),
    ...         ars.tap_successes_to_awaitable_result(
    ...             lambda s: write_to_disk(s, output_path)
    ...         ),
    ...     )
    ...     return await pipe(p)
    ...
    >>> asyncio.run(
    ...     read_and_transform_and_write(["a.txt", "b.txt"], "output.txt")
    ... )
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ['Length: 5', 'Length: 5'])

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    >>> p1: Pipeline1[
    ...     list[str],
    ...     AwaitableSuccessSequence[str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     ars.construct_successes_from_sequence,
    ... )
    >>> asyncio.run(ars.to_coroutine_result_sequence(pipe(p1)))
    ('success', ['a.txt', 'b.txt'])
    >>>
    >>> p2: Pipeline2[
    ...     list[str],
    ...     AwaitableSuccessSequence[str],
    ...     AwaitableResultSequence[ReadErrorLiteral, str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     ars.construct_successes_from_sequence,
    ...     ars.map_successes_to_awaitable_result(read_from_disk),
    ... )
    >>> asyncio.run(ars.to_coroutine_result_sequence(pipe(p2)))
    ('success', ['Hello', 'World'])
    >>>
    >>> p3: Pipeline3[
    ...     list[str],
    ...     AwaitableSuccessSequence[str],
    ...     AwaitableResultSequence[ReadErrorLiteral, str],
    ...     AwaitableResultSequence[ReadErrorLiteral, str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     ars.construct_successes_from_sequence,
    ...     ars.map_successes_to_awaitable_result(read_from_disk),
    ...     ars.map_successes(transform),
    ... )
    >>> asyncio.run(ars.to_coroutine_result_sequence(pipe(p3)))
    ('success', ['Length: 5', 'Length: 5'])
    >>>
    >>> p4: Pipeline4[
    ...     list[str],
    ...     AwaitableSuccessSequence[str],
    ...     AwaitableResultSequence[ReadErrorLiteral, str],
    ...     AwaitableResultSequence[ReadErrorLiteral, str],
    ...     AwaitableResultSequence[ReadErrorLiteral | WriteErrorLiteral, str],
    ... ] = (
    ...     ["a.txt", "b.txt"],
    ...     ars.construct_successes_from_sequence,
    ...     ars.map_successes_to_awaitable_result(read_from_disk),
    ...     ars.map_successes(transform),
    ...     ars.tap_successes_to_awaitable_result(
    ...         lambda s: write_to_disk(s, "output.txt")
    ...     ),
    ... )
    >>> asyncio.run(ars.to_coroutine_result_sequence(pipe(p4)))
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ['Length: 5', 'Length: 5'])

???+ note
    The function
    [trcks.fp.monads.awaitable_result_sequence.construct_successes_from_sequence][]
    wraps a [collections.abc.Sequence][]
    into an [trcks.AwaitableSuccessSequence][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.awaitable_result_sequence][].

    The values `pipe(p1)`, `pipe(p2)`, `pipe(p3)` and `pipe(p4)` are all
    of type [trcks.AwaitableResultSequence][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function
    [trcks.fp.monads.awaitable_result_sequence.to_coroutine_result_sequence][]
    to convert the [trcks.AwaitableResultSequence][]s
    to [collections.abc.Coroutine][]s.

The higher-order functions
[trcks.fp.monads.awaitable_result_sequence.tap_failure][]
and [trcks.fp.monads.awaitable_result_sequence.tap_successes][]
allow us to execute synchronous side effects
in the failure case or in the success case (for each element), respectively:

???+ example

    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return "success", contents[path]
    ...
    >>> async def write_to_disk(
    ...     s: str, path: str
    ... ) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     return "success", None
    ...
    >>> async def read_and_transform_and_write(
    ...     input_paths: list[str], output_path: str
    ... ) -> ResultSequence[ReadErrorLiteral | WriteErrorLiteral, str]:
    ...     pipeline: Pipeline7[
    ...         list[str],
    ...         AwaitableSuccessSequence[str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral | WriteErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral | WriteErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral | WriteErrorLiteral, str],
    ...     ] = (
    ...         input_paths,
    ...         ars.construct_successes_from_sequence,
    ...         ars.map_successes_to_awaitable_result(read_from_disk),
    ...         ars.tap_successes(lambda s: print(f"LOG: Read '{s}' from disk.")),
    ...         ars.map_successes(transform),
    ...         ars.tap_successes_to_awaitable_result(
    ...             lambda s: write_to_disk(s, output_path)
    ...         ),
    ...         ars.tap_successes(lambda _: print("LOG: Successfully wrote to disk.")),
    ...         ars.tap_failure(lambda err: print(f"LOG: Failed with error: {err}")),
    ...     )
    ...     return await pipe(pipeline)
    ...
    >>> result_1 = asyncio.run(
    ...     read_and_transform_and_write(["a.txt", "b.txt"], "output.txt")
    ... )
    LOG: Read 'Hello' from disk.
    LOG: Read 'World' from disk.
    LOG: Successfully wrote to disk.
    LOG: Successfully wrote to disk.
    >>> result_1
    ('success', ['Length: 5', 'Length: 5'])
    >>>
    >>> result_2 = asyncio.run(
    ...     read_and_transform_and_write(["missing.txt"], "output.txt")
    ... )
    LOG: Failed with error: read error
    >>> result_2
    ('failure', 'read error')

Sometimes, side effects themselves can fail and
need to return an [trcks.AwaitableResult][] type.
The higher-order function
[trcks.fp.monads.awaitable_result_sequence.tap_successes_to_awaitable_result][]
allows us to execute such asynchronous side effects
for each element in the success case.
If the side effect returns a [trcks.Failure][] for any element,
that failure is propagated.
If the side effect returns a [trcks.Success][] for all elements,
the original success values are preserved:

???+ example

    >>> async def write_to_disk(s: str) -> Result[OutOfDiskSpace, None]:
    ...     await asyncio.sleep(0.001)
    ...     if len(s) > 10:
    ...         return "failure", "Out of disk space"
    ...     return "success", None
    ...
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hi", "b.txt": "Hello, world!"}
    ...     return "success", contents[path]
    ...
    >>> async def read_and_persist(
    ...     input_paths: list[str],
    ... ) -> ResultSequence[ReadErrorLiteral | OutOfDiskSpace, str]:
    ...     pipeline: Pipeline4[
    ...         list[str],
    ...         AwaitableSuccessSequence[str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral, str],
    ...         AwaitableResultSequence[ReadErrorLiteral | OutOfDiskSpace, str],
    ...     ] = (
    ...         input_paths,
    ...         ars.construct_successes_from_sequence,
    ...         ars.map_successes_to_awaitable_result(read_from_disk),
    ...         ars.tap_successes(lambda s: print(f"LOG: Persisting '{s}'.")),
    ...         ars.tap_successes_to_awaitable_result(write_to_disk),
    ...     )
    ...     return await pipe(pipeline)
    ...
    >>> result = asyncio.run(read_and_persist(["a.txt", "b.txt"]))
    LOG: Persisting 'Hi'.
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')
