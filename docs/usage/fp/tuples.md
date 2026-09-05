# Tuple code with [trcks.fp][]

???+ tip "See also"
    The [object-oriented tuple page](../oop/tuples.md)
    covers the same operations using method chaining.

## Synchronous single-track code with [trcks.fp.monads.tuple_][]

If we want to apply a pipeline of functions to each element
in a [tuple][],
the module [trcks.fp.monads.tuple_][] provides
some higher-order functions named `map*` and `tap*`
that turn element-wise functions into functions
operating on entire tuples.

???+ example

    ```pycon
    >>> import asyncio
    >>> from typing import Literal
    >>> from trcks import AwaitableResultTuple, AwaitableTuple, Result, ResultTuple
    >>> from trcks.fp.composition import (
    ...     Pipeline0,
    ...     Pipeline1,
    ...     Pipeline2,
    ...     Pipeline3,
    ...     Pipeline4,
    ...     Pipeline5,
    ...     Pipeline7,
    ...     pipe,
    ... )
    >>> from trcks.fp.monads import tuple_ as t
    >>>
    >>> def normalize_email(email: str) -> str:
    ...     return email.strip().lower()
    >>>
    >>> def to_domain(email: str) -> str:
    ...     return email.split("@")[1]
    >>>
    >>> def get_domains(emails: tuple[str, ...]) -> tuple[str, ...]:
    ...     pipeline: Pipeline2[
    ...         tuple[str, ...],
    ...         tuple[str, ...],
    ...         tuple[str, ...],
    ...     ] = (
    ...         emails,
    ...         t.map_(normalize_email),
    ...         t.map_(to_domain),
    ...     )
    ...     return pipe(pipeline)
    >>>
    >>> get_domains(("  Erika.Mustermann@Domain.ORG ", "JOHN_DOE@Provider.COM  "))
    ('domain.org', 'provider.com')

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> emails: tuple[str, ...] = (
    ...     "  Erika.Mustermann@Domain.ORG ",
    ...     "JOHN_DOE@Provider.COM  ",
    ... )
    >>>
    >>> p0: Pipeline0[tuple[str, ...]] = (emails,)
    >>> pipe(p0)
    ('  Erika.Mustermann@Domain.ORG ', 'JOHN_DOE@Provider.COM  ')
    >>>
    >>> p1: Pipeline1[tuple[str, ...], tuple[str, ...]] = (
    ...     emails,
    ...     t.map_(normalize_email),
    ... )
    >>> pipe(p1)
    ('erika.mustermann@domain.org', 'john_doe@provider.com')
    >>>
    >>> p2: Pipeline2[tuple[str, ...], tuple[str, ...], tuple[str, ...]] = (
    ...     emails,
    ...     t.map_(normalize_email),
    ...     t.map_(to_domain),
    ... )
    >>> pipe(p2)
    ('domain.org', 'provider.com')

    ```

???+ note
    The higher-order function [trcks.fp.monads.tuple_.map_to_iterable][]
    applies a function that returns a [collections.abc.Iterable][]
    to each element and flattens the results (like a "flat map"):

    ```pycon
    >>> pipe(
    ...     (
    ...         ("ab", "cd"),
    ...         t.map_to_iterable(tuple),
    ...     )
    ... )
    ('a', 'b', 'c', 'd')

    ```

The higher-order function [trcks.fp.monads.tuple_.tap][]
allows us to execute side effects for each element:

???+ example

    ```pycon
    >>> def get_domains(emails: tuple[str, ...]) -> tuple[str, ...]:
    ...     pipeline: Pipeline3[
    ...         tuple[str, ...],
    ...         tuple[str, ...],
    ...         tuple[str, ...],
    ...         tuple[str, ...],
    ...     ] = (
    ...         emails,
    ...         t.map_(normalize_email),
    ...         t.tap(lambda e: print(f"LOG: Processing '{e}'.")),
    ...         t.map_(to_domain),
    ...     )
    ...     return pipe(pipeline)
    >>>
    >>> result = get_domains(("  Erika.Mustermann@Domain.ORG ", "JOHN_DOE@Provider.COM  "))
    LOG: Processing 'erika.mustermann@domain.org'.
    LOG: Processing 'john_doe@provider.com'.
    >>> result
    ('domain.org', 'provider.com')

    ```

## Synchronous double-track code with [trcks.fp.monads.result_tuple][]

If one of the functions in a [trcks.fp.composition.Pipeline][]
returns a [trcks.ResultTuple][]`[F, S]` type,
the module [trcks.fp.monads.result_tuple][] provides
some higher-order functions named `map_successes*` and `tap_successes*`
that turn element-wise functions into functions
operating on [trcks.ResultTuple][] values.
The success track functions use the plural `map_successes` (instead of `map_success`)
because they operate on each element in the [trcks.SuccessTuple][] individually.
Processing short-circuits on the first [trcks.Failure][].

???+ example

    ```pycon
    >>> from trcks import ResultTuple, SuccessTuple
    >>> from trcks.fp.composition import Pipeline4
    >>> from trcks.fp.monads import result_tuple as rt
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
    >>>
    >>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscription, int]:
    ...     if user_id == 1:
    ...         return "success", 42
    ...     return "failure", "User does not have a subscription"
    >>>
    >>> def get_subscription_fee(subscription_id: int) -> float:
    ...     return subscription_id * 0.1
    >>>
    >>> def get_subscription_fees_by_email(
    ...     user_emails: tuple[str, ...],
    ... ) -> ResultTuple[FailureDescription, float]:
    ...     pipeline: Pipeline4[
    ...         tuple[str, ...],
    ...         SuccessTuple[str],
    ...         ResultTuple[UserDoesNotExist, int],
    ...         ResultTuple[FailureDescription, int],
    ...         ResultTuple[FailureDescription, float],
    ...     ] = (
    ...         user_emails,
    ...         rt.construct_successes_from_iterable,
    ...         rt.map_successes_to_result(get_user_id),
    ...         rt.map_successes_to_result(get_subscription_id),
    ...         rt.map_successes(get_subscription_fee),
    ...     )
    ...     return pipe(pipeline)
    >>>
    >>> get_subscription_fees_by_email(("erika.mustermann@domain.org",))
    ('success', (4.2,))
    >>> get_subscription_fees_by_email(("erika.mustermann@domain.org", "john_doe@provider.com"))
    ('failure', 'User does not have a subscription')
    >>> get_subscription_fees_by_email(("jane_doe@provider.com",))
    ('failure', 'User does not exist')

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> from trcks.fp.composition import Pipeline4
    >>>
    >>> p0: Pipeline0[tuple[str, ...]] = (("erika.mustermann@domain.org",),)
    >>> pipe(p0)
    ('erika.mustermann@domain.org',)
    >>>
    >>> p1: Pipeline1[
    ...     tuple[str, ...],
    ...     SuccessTuple[str],
    ... ] = (
    ...     ("erika.mustermann@domain.org",),
    ...     rt.construct_successes_from_iterable,
    ... )
    >>> pipe(p1)
    ('success', ('erika.mustermann@domain.org',))
    >>>
    >>> p2: Pipeline2[
    ...     tuple[str, ...],
    ...     SuccessTuple[str],
    ...     ResultTuple[UserDoesNotExist, int],
    ... ] = (
    ...     ("erika.mustermann@domain.org",),
    ...     rt.construct_successes_from_iterable,
    ...     rt.map_successes_to_result(get_user_id),
    ... )
    >>> pipe(p2)
    ('success', (1,))
    >>>
    >>> p3: Pipeline3[
    ...     tuple[str, ...],
    ...     SuccessTuple[str],
    ...     ResultTuple[UserDoesNotExist, int],
    ...     ResultTuple[FailureDescription, int],
    ... ] = (
    ...     ("erika.mustermann@domain.org",),
    ...     rt.construct_successes_from_iterable,
    ...     rt.map_successes_to_result(get_user_id),
    ...     rt.map_successes_to_result(get_subscription_id),
    ... )
    >>> pipe(p3)
    ('success', (42,))
    >>>
    >>> p4: Pipeline4[
    ...     tuple[str, ...],
    ...     SuccessTuple[str],
    ...     ResultTuple[UserDoesNotExist, int],
    ...     ResultTuple[FailureDescription, int],
    ...     ResultTuple[FailureDescription, float],
    ... ] = (
    ...     ("erika.mustermann@domain.org",),
    ...     rt.construct_successes_from_iterable,
    ...     rt.map_successes_to_result(get_user_id),
    ...     rt.map_successes_to_result(get_subscription_id),
    ...     rt.map_successes(get_subscription_fee),
    ... )
    >>> pipe(p4)
    ('success', (4.2,))

    ```

???+ note
    The function [trcks.fp.monads.result_tuple.construct_successes_from_iterable][]
    converts a [collections.abc.Iterable][] into a [tuple][] and wraps it into
    a [trcks.SuccessTuple][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.result_tuple][].

    While [trcks.fp.monads.result.map_failure][]
    and [trcks.fp.monads.result.map_success][]
    operate on single-value [trcks.Result][] types,
    [trcks.fp.monads.result_tuple.map_successes][] (plural)
    operates on each element in the tuple.

The higher-order functions [trcks.fp.monads.result_tuple.tap_successes][]
and [trcks.fp.monads.result_tuple.tap_failure][]
allow us to execute side effects
in the success case (for each element) or in the failure case, respectively.

???+ example

    ```pycon
    >>> from trcks.fp.composition import Pipeline7
    >>> def get_subscription_fees_by_email(
    ...     user_emails: tuple[str, ...],
    ... ) -> ResultTuple[FailureDescription, float]:
    ...     pipeline: Pipeline7[
    ...         tuple[str, ...],
    ...         SuccessTuple[str],
    ...         ResultTuple[UserDoesNotExist, int],
    ...         ResultTuple[UserDoesNotExist, int],
    ...         ResultTuple[FailureDescription, int],
    ...         ResultTuple[FailureDescription, float],
    ...         ResultTuple[FailureDescription, float],
    ...         ResultTuple[FailureDescription, float],
    ...     ] = (
    ...         user_emails,
    ...         rt.construct_successes_from_iterable,
    ...         rt.map_successes_to_result(get_user_id),
    ...         rt.tap_successes(lambda n: print(f"LOG: User ID: {n}.")),
    ...         rt.map_successes_to_result(get_subscription_id),
    ...         rt.map_successes(get_subscription_fee),
    ...         rt.tap_successes(lambda x: print(f"LOG: Subscription fee: {x}.")),
    ...         rt.tap_failure(lambda fd: print(f"LOG: Failure: {fd}.")),
    ...     )
    ...     return pipe(pipeline)
    >>>
    >>> fees_erika = get_subscription_fees_by_email(("erika.mustermann@domain.org",))
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fees_erika
    ('success', (4.2,))
    >>>
    >>> fees_john = get_subscription_fees_by_email(("john_doe@provider.com",))
    LOG: User ID: 2.
    LOG: Failure: User does not have a subscription.
    >>> fees_john
    ('failure', 'User does not have a subscription')
    >>>
    >>> fees_jane = get_subscription_fees_by_email(("jane_doe@provider.com",))
    LOG: Failure: User does not exist.
    >>> fees_jane
    ('failure', 'User does not exist')

    ```

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] type.
The higher-order function [trcks.fp.monads.result_tuple.tap_successes_to_result][]
allows us to execute such side effects for each element in the success case.
If the side effect returns a [trcks.Failure][] for any element,
that failure is propagated.
If the side effect returns a [trcks.Success][] for all elements,
the original success values are preserved.

???+ example

    ```pycon
    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>>
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    >>>
    >>> def get_and_persist_user_ids(
    ...     user_emails: tuple[str, ...],
    ... ) -> ResultTuple[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     pipeline: Pipeline3[
    ...         tuple[str, ...],
    ...         SuccessTuple[str],
    ...         ResultTuple[UserDoesNotExist, int],
    ...         ResultTuple[UserDoesNotExist | OutOfDiskSpace, int],
    ...     ] = (
    ...         user_emails,
    ...         rt.construct_successes_from_iterable,
    ...         rt.map_successes_to_result(get_user_id),
    ...         rt.tap_successes_to_result(write_to_disk),
    ...     )
    ...     return pipe(pipeline)
    >>>
    >>> ids_erika = get_and_persist_user_ids(("erika.mustermann@domain.org",))
    LOG: Wrote 1 to disk.
    >>> ids_erika
    ('success', (1,))
    >>>
    >>> ids_john = get_and_persist_user_ids(("john_doe@provider.com",))
    >>> ids_john
    ('failure', 'Out of disk space')
    >>>
    >>> ids_jane = get_and_persist_user_ids(("jane_doe@provider.com",))
    >>> ids_jane
    ('failure', 'User does not exist')

    ```

To demonstrate that processing truly short-circuits on the first
[trcks.Failure][], we can add logging to `get_user_id`.
When the second element fails, the third element is never evaluated:

???+ example

    ```pycon
    >>> def get_user_id_logged(user_email: str) -> Result[UserDoesNotExist, int]:
    ...     print(f"LOG: Looking up '{user_email}'.")
    ...     return get_user_id(user_email)
    >>>
    >>> pipe(
    ...     (
    ...         (
    ...             "erika.mustermann@domain.org",
    ...             "jane_doe@provider.com",
    ...             "john_doe@provider.com",
    ...         ),
    ...         rt.construct_successes_from_iterable,
    ...         rt.map_successes_to_result(get_user_id_logged),
    ...     )
    ... )
    LOG: Looking up 'erika.mustermann@domain.org'.
    LOG: Looking up 'jane_doe@provider.com'.
    ('failure', 'User does not exist')

    ```

`"john_doe@provider.com"` is never looked up:
as soon as `"jane_doe@provider.com"` returns a [trcks.Failure][],
the remaining elements are skipped.

## Asynchronous single-track code with [trcks.fp.monads.awaitable_tuple][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a [trcks.AwaitableTuple][]`[T]` type,
the following function must accept this [trcks.AwaitableTuple][]`[T]` type
as its input.
The module [trcks.fp.monads.awaitable_tuple][] provides
some higher-order functions named `map*`
that turn element-wise functions
into functions operating on [trcks.AwaitableTuple][] values.

???+ example

    ```pycon
    >>> from trcks import AwaitableTuple
    >>> from trcks.fp.monads import awaitable_tuple as at
    >>>
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return contents[path]
    >>>
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    >>>
    >>> async def read_and_transform(
    ...     input_paths: tuple[str, ...],
    ... ) -> tuple[str, ...]:
    ...     p: Pipeline3[
    ...         tuple[str, ...],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...     ] = (
    ...         input_paths,
    ...         at.construct_from_iterable,
    ...         at.map_to_awaitable(read_from_disk),
    ...         at.map_(transform),
    ...     )
    ...     return await pipe(p)
    >>>
    >>> asyncio.run(read_and_transform(("a.txt", "b.txt")))
    ('Length: 5', 'Length: 5')

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> from trcks import AwaitableTuple
    >>>
    >>> p1: Pipeline1[tuple[str, ...], AwaitableTuple[str]] = (
    ...     ("a.txt", "b.txt"),
    ...     at.construct_from_iterable,
    ... )
    >>> asyncio.run(at.to_coroutine_tuple(pipe(p1)))
    ('a.txt', 'b.txt')
    >>>
    >>> p2: Pipeline2[
    ...     tuple[str, ...],
    ...     AwaitableTuple[str],
    ...     AwaitableTuple[str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     at.construct_from_iterable,
    ...     at.map_to_awaitable(read_from_disk),
    ... )
    >>> asyncio.run(at.to_coroutine_tuple(pipe(p2)))
    ('Hello', 'World')
    >>>
    >>> p3: Pipeline3[
    ...     tuple[str, ...],
    ...     AwaitableTuple[str],
    ...     AwaitableTuple[str],
    ...     AwaitableTuple[str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     at.construct_from_iterable,
    ...     at.map_to_awaitable(read_from_disk),
    ...     at.map_(transform),
    ... )
    >>> asyncio.run(at.to_coroutine_tuple(pipe(p3)))
    ('Length: 5', 'Length: 5')

    ```

???+ note
    The function [trcks.fp.monads.awaitable_tuple.construct_from_iterable][]
    converts a [collections.abc.Iterable][] into a [tuple][] and wraps it into
    a [trcks.AwaitableTuple][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.awaitable_tuple][].

    The values `pipe(p1)`, `pipe(p2)`, and `pipe(p3)` are all
    of type [trcks.AwaitableTuple][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function
    [trcks.fp.monads.awaitable_tuple.to_coroutine_tuple][]
    to convert the [trcks.AwaitableTuple][]s
    to [collections.abc.Coroutine][]s.

The higher-order function [trcks.fp.monads.awaitable_tuple.tap][]
allows us to execute synchronous side effects for each element.
Similarly, the higher-order function
[trcks.fp.monads.awaitable_tuple.tap_to_awaitable][]
allows us to execute asynchronous side effects for each element.

???+ example

    ```pycon
    >>> from trcks.fp.composition import Pipeline5
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return contents[path]
    >>>
    >>> async def read_and_transform(
    ...     input_paths: tuple[str, ...],
    ... ) -> tuple[str, ...]:
    ...     p: Pipeline5[
    ...         tuple[str, ...],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...         AwaitableTuple[str],
    ...     ] = (
    ...         input_paths,
    ...         at.construct_from_iterable,
    ...         at.map_to_awaitable(read_from_disk),
    ...         at.tap(lambda s: print(f"Read '{s}' from disk.")),
    ...         at.map_(transform),
    ...         at.tap(lambda s: print(f"Transformed to '{s}'.")),
    ...     )
    ...     return await pipe(p)
    >>>
    >>> asyncio.run(read_and_transform(("a.txt", "b.txt")))
    Read 'Hello' from disk.
    Read 'World' from disk.
    Transformed to 'Length: 5'.
    Transformed to 'Length: 5'.
    ('Length: 5', 'Length: 5')

    ```

## Asynchronous double-track code with [trcks.fp.monads.awaitable_result_tuple][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a [trcks.AwaitableResultTuple][]`[F, S]` type,
the module [trcks.fp.monads.awaitable_result_tuple][] provides
some higher-order functions named `map_successes*` and `tap_successes*`
that turn element-wise functions into functions
operating on [trcks.AwaitableResultTuple][] values.
The success track functions use the plural `map_successes` (instead of `map_success`)
because they operate on each element individually.
Processing short-circuits on the first [trcks.Failure][],
just as in the synchronous case above.

???+ example

    ```pycon
    >>> from trcks import AwaitableResultTuple, AwaitableSuccessTuple
    >>> from trcks.fp.monads import awaitable_result_tuple as art
    >>>
    >>> ReadErrorLiteral = Literal["read error"]
    >>> WriteErrorLiteral = Literal["write error"]
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return "success", contents[path]
    >>>
    >>> def transform(s: str) -> str:
    ...     return f"Length: {len(s)}"
    >>>
    >>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{s}' to file {path}.")
    ...     return "success", None
    >>>
    >>> async def read_and_transform_and_write(
    ...     input_paths: tuple[str, ...], output_path: str
    ... ) -> ResultTuple[ReadErrorLiteral | WriteErrorLiteral, str]:
    ...     p: Pipeline4[
    ...         tuple[str, ...],
    ...         AwaitableSuccessTuple[str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral | WriteErrorLiteral, str],
    ...     ] = (
    ...         input_paths,
    ...         art.construct_successes_from_iterable,
    ...         art.map_successes_to_awaitable_result(read_from_disk),
    ...         art.map_successes(transform),
    ...         art.tap_successes_to_awaitable_result(lambda s: write_to_disk(s, output_path)),
    ...     )
    ...     return await pipe(p)
    >>>
    >>> asyncio.run(read_and_transform_and_write(("a.txt", "b.txt"), "output.txt"))
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ('Length: 5', 'Length: 5'))

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> p1: Pipeline1[
    ...     tuple[str, ...],
    ...     AwaitableSuccessTuple[str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     art.construct_successes_from_iterable,
    ... )
    >>> asyncio.run(art.to_coroutine_result_tuple(pipe(p1)))
    ('success', ('a.txt', 'b.txt'))
    >>>
    >>> p2: Pipeline2[
    ...     tuple[str, ...],
    ...     AwaitableSuccessTuple[str],
    ...     AwaitableResultTuple[ReadErrorLiteral, str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     art.construct_successes_from_iterable,
    ...     art.map_successes_to_awaitable_result(read_from_disk),
    ... )
    >>> asyncio.run(art.to_coroutine_result_tuple(pipe(p2)))
    ('success', ('Hello', 'World'))
    >>>
    >>> p3: Pipeline3[
    ...     tuple[str, ...],
    ...     AwaitableSuccessTuple[str],
    ...     AwaitableResultTuple[ReadErrorLiteral, str],
    ...     AwaitableResultTuple[ReadErrorLiteral, str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     art.construct_successes_from_iterable,
    ...     art.map_successes_to_awaitable_result(read_from_disk),
    ...     art.map_successes(transform),
    ... )
    >>> asyncio.run(art.to_coroutine_result_tuple(pipe(p3)))
    ('success', ('Length: 5', 'Length: 5'))
    >>>
    >>> p4: Pipeline4[
    ...     tuple[str, ...],
    ...     AwaitableSuccessTuple[str],
    ...     AwaitableResultTuple[ReadErrorLiteral, str],
    ...     AwaitableResultTuple[ReadErrorLiteral, str],
    ...     AwaitableResultTuple[ReadErrorLiteral | WriteErrorLiteral, str],
    ... ] = (
    ...     ("a.txt", "b.txt"),
    ...     art.construct_successes_from_iterable,
    ...     art.map_successes_to_awaitable_result(read_from_disk),
    ...     art.map_successes(transform),
    ...     art.tap_successes_to_awaitable_result(lambda s: write_to_disk(s, "output.txt")),
    ... )
    >>> asyncio.run(art.to_coroutine_result_tuple(pipe(p4)))
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ('Length: 5', 'Length: 5'))

    ```

???+ note
    The function
    [trcks.fp.monads.awaitable_result_tuple.construct_successes_from_iterable][]
    converts a [collections.abc.Iterable][] into a [tuple][] and wraps it into
    a [trcks.AwaitableSuccessTuple][],
    which can then be used with the higher-order functions
    from [trcks.fp.monads.awaitable_result_tuple][].

    The values `pipe(p1)`, `pipe(p2)`, `pipe(p3)`, and `pipe(p4)` are all
    of type [trcks.AwaitableResultTuple][].
    Since [asyncio.run][] expects the input type [collections.abc.Coroutine][],
    we use the function
    [trcks.fp.monads.awaitable_result_tuple.to_coroutine_result_tuple][]
    to convert the [trcks.AwaitableResultTuple][]s
    to [collections.abc.Coroutine][]s.

The higher-order functions
[trcks.fp.monads.awaitable_result_tuple.tap_failure][]
and [trcks.fp.monads.awaitable_result_tuple.tap_successes][]
allow us to execute synchronous side effects
in the failure case or in the success case (for each element), respectively:

???+ example

    ```pycon
    >>> from trcks.fp.composition import Pipeline7
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return "success", contents[path]
    >>>
    >>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
    ...     if path != "output.txt":
    ...         return "failure", "write error"
    ...     await asyncio.sleep(0.001)
    ...     return "success", None
    >>>
    >>> async def read_and_transform_and_write(
    ...     input_paths: tuple[str, ...], output_path: str
    ... ) -> ResultTuple[ReadErrorLiteral | WriteErrorLiteral, str]:
    ...     pipeline: Pipeline7[
    ...         tuple[str, ...],
    ...         AwaitableSuccessTuple[str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral | WriteErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral | WriteErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral | WriteErrorLiteral, str],
    ...     ] = (
    ...         input_paths,
    ...         art.construct_successes_from_iterable,
    ...         art.map_successes_to_awaitable_result(read_from_disk),
    ...         art.tap_successes(lambda s: print(f"LOG: Read '{s}' from disk.")),
    ...         art.map_successes(transform),
    ...         art.tap_successes_to_awaitable_result(lambda s: write_to_disk(s, output_path)),
    ...         art.tap_successes(lambda _: print("LOG: Successfully wrote to disk.")),
    ...         art.tap_failure(lambda err: print(f"LOG: Failed with error: {err}")),
    ...     )
    ...     return await pipe(pipeline)
    >>>
    >>> result_1 = asyncio.run(read_and_transform_and_write(("a.txt", "b.txt"), "output.txt"))
    LOG: Read 'Hello' from disk.
    LOG: Read 'World' from disk.
    LOG: Successfully wrote to disk.
    LOG: Successfully wrote to disk.
    >>> result_1
    ('success', ('Length: 5', 'Length: 5'))
    >>>
    >>> result_2 = asyncio.run(read_and_transform_and_write(("missing.txt",), "output.txt"))
    LOG: Failed with error: read error
    >>> result_2
    ('failure', 'read error')

    ```

Sometimes, side effects themselves can fail and
need to return a [trcks.AwaitableResult][] type.
The higher-order function
[trcks.fp.monads.awaitable_result_tuple.tap_successes_to_awaitable_result][]
allows us to execute such asynchronous side effects
for each element in the success case.
If the side effect returns a [trcks.Failure][] for any element,
that failure is propagated.
If the side effect returns a [trcks.Success][] for all elements,
the original success values are preserved:

???+ example

    ```pycon
    >>> async def write_to_disk(s: str) -> Result[OutOfDiskSpace, None]:
    ...     await asyncio.sleep(0.001)
    ...     if len(s) > 10:
    ...         return "failure", "Out of disk space"
    ...     return "success", None
    >>>
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "a.txt" and path != "b.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hi", "b.txt": "Hello, world!"}
    ...     return "success", contents[path]
    >>>
    >>> async def read_and_persist(
    ...     input_paths: tuple[str, ...],
    ... ) -> ResultTuple[ReadErrorLiteral | OutOfDiskSpace, str]:
    ...     pipeline: Pipeline4[
    ...         tuple[str, ...],
    ...         AwaitableSuccessTuple[str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral, str],
    ...         AwaitableResultTuple[ReadErrorLiteral | OutOfDiskSpace, str],
    ...     ] = (
    ...         input_paths,
    ...         art.construct_successes_from_iterable,
    ...         art.map_successes_to_awaitable_result(read_from_disk),
    ...         art.tap_successes(lambda s: print(f"LOG: Persisting '{s}'.")),
    ...         art.tap_successes_to_awaitable_result(write_to_disk),
    ...     )
    ...     return await pipe(pipeline)
    >>>
    >>> result = asyncio.run(read_and_persist(("a.txt", "b.txt")))
    LOG: Persisting 'Hi'.
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')

    ```
