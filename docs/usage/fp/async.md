# Asynchronous code with [trcks.fp][]

???+ tip "See also"
    The [object-oriented async page](../oop/async.md)
    covers the same operations using method chaining.

## Single-track code with [trcks.fp.monads.awaitable][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a `collections.abc.Awaitable[T]` type,
the following function must accept this `collections.abc.Awaitable[T]` type
as its input.
However, functions with input type `collections.abc.Awaitable[T]`
tend to contain unnecessary `await` statements.
Therefore, the module [trcks.fp.monads.awaitable][] provides
some higher-order functions named `map*`
that turn functions with input type `T`
into functions with input type `collections.abc.Awaitable[T]`.

???+ example

    ```pycon
    >>> import asyncio
    >>> from collections.abc import Awaitable
    >>> from typing import Literal
    >>> from trcks import AwaitableResult, Result
    >>> from trcks.fp.composition import (
    ...     Pipeline1,
    ...     Pipeline2,
    ...     Pipeline3,
    ...     Pipeline5,
    ...     Pipeline6,
    ...     pipe,
    ... )
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

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
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

    ```

???+ note
    The values `pipe(p1)`, `pipe(p2)`, and `pipe(p3)` are all of the type [collections.abc.Awaitable][].
    On Python versions older than 3.14, [asyncio.run][] expects the input type
    [collections.abc.Coroutine][].
    Therefore,
    we use the function [trcks.fp.monads.awaitable.to_coroutine][] to convert
    the [collections.abc.Awaitable][]s to [collections.abc.Coroutine][]s.

The higher-order function [trcks.fp.monads.awaitable.tap][]
allows us to execute synchronous side effects.
Similarly, the higher-order function [trcks.fp.monads.awaitable.tap_to_awaitable][]
allows us to execute asynchronous side effects.

???+ example

    ```pycon
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

    ```

## Double-track code with [trcks.fp.monads.awaitable_result][]

If one of the functions in a [trcks.fp.composition.Pipeline][] returns
a `trcks.AwaitableResult[F, S]` type,
the following function must accept this `trcks.AwaitableResult[F, S]` type
as its input.
However, functions with input type `trcks.AwaitableResult[F, S]` tend to
contain unnecessary `await` statements and
violate the "do one thing and do it well" principle.
Therefore, the module [trcks.fp.monads.awaitable_result][] provides
some higher-order functions named `map*`
that turn functions with input type `F` and functions with input type `S`
into functions with input type `trcks.AwaitableResult[F, S]`.

???+ example

    ```pycon
    >>> from trcks.fp.monads import awaitable_result as ar
    >>>
    >>> ReadErrorLiteral = Literal["read error"]
    >>> WriteErrorLiteral = Literal["write error"]
    >>> OutOfDiskSpace = Literal["Out of disk space"]
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

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
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

    ```

???+ note
    The values `pipe(p1)`, `pipe(p2)`, and `pipe(p3)` are all
    of type [trcks.AwaitableResult][].
    On Python versions older than 3.14, [asyncio.run][] expects the input type
    [collections.abc.Coroutine][].
    Therefore,
    we use the function [trcks.fp.monads.awaitable_result.to_coroutine_result][]
    to convert the [trcks.AwaitableResult][]s to [collections.abc.Coroutine][]s.

The higher-order functions [trcks.fp.monads.awaitable_result.tap_failure][]
and [trcks.fp.monads.awaitable_result.tap_success][]
allow us to execute synchronous side effects
in the failure case or in the success case, respectively:

???+ example

    ```pycon
    >>> async def read_from_disk(path: str) -> Result[ReadErrorLiteral, str]:
    ...     if path != "input.txt":
    ...         return "failure", "read error"
    ...     await asyncio.sleep(0.001)
    ...     return "success", "Hello, world!"
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
    ...         ar.tap_success(lambda _: print("LOG: Successfully wrote to disk.")),
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

    ```

Sometimes, side effects themselves can fail and
need to return an [trcks.AwaitableResult][] type.
The higher-order function [trcks.fp.monads.awaitable_result.tap_success_to_awaitable_result][]
allows us to execute such asynchronous side effects in the success case.
If the side effect returns an [trcks.AwaitableFailure][], that failure is propagated.
If the side effect returns an [trcks.AwaitableSuccess][],
the original success value is preserved:

???+ example

    ```pycon
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

    ```
