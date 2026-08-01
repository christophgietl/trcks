# Asynchronous code with [trcks.oop][]

???+ tip "See also"
    The [functional async page](../fp/async.md)
    covers the same operations using function composition.

## Single-track code with [trcks.oop.AwaitableWrapper][]

While the class [trcks.oop.Wrapper][] and its method `map` allow
the chaining of synchronous functions,
they cannot chain asynchronous functions.
To understand why,
we first need to understand the return type of asynchronous functions:

???+ example

    ```pycon
    >>> import asyncio
    >>> from collections.abc import Awaitable, Coroutine
    >>> from typing import Literal
    >>> from trcks import Result
    >>> from trcks.oop import Wrapper
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     s = "Hello, world!"
    ...     print(f"Read '{s}' from file {path}.")
    ...     return s
    ...
    >>> # Examine the return value of read_from_disk:
    >>> return_value = read_from_disk("input.txt")
    >>> return_value
    <coroutine object read_from_disk at ...>
    >>> asyncio.run(return_value)
    Read 'Hello, world!' from file input.txt.
    'Hello, world!'
    >>> # Examine the type of the return value:
    >>> return_type = type(return_value)
    >>> return_type
    <class 'coroutine'>
    >>> issubclass(return_type, Coroutine)
    True
    >>> issubclass(Coroutine, Awaitable)
    True

    ```

So, whenever we define a function using the `async def ... -> T` syntax,
we actually get a function with the return type [collections.abc.Awaitable][]`[T]`.
The method [trcks.oop.Wrapper.map_to_awaitable][] and the class [trcks.oop.AwaitableWrapper][]
allow us to combine [collections.abc.Awaitable][]-returning functions
with other [collections.abc.Awaitable][]-returning functions or
with "regular" functions:

???+ example

    ```pycon
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
    ...     return await (
    ...         Wrapper(core=input_path)
    ...         .map_to_awaitable(read_from_disk)
    ...         .map(transform)
    ...         .map_to_awaitable(lambda s: write_to_disk(s, output_path))
    ...         .core
    ...     )
    ...
    >>> asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> from typing import Any
    >>> from trcks.oop import AwaitableWrapper
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="input.txt")
    >>> wrapped
    Wrapper(core='input.txt')
    >>> # 2. Apply the asynchronous function read_from_disk:
    >>> mapped_once: AwaitableWrapper[str] = wrapped.map_to_awaitable(read_from_disk)
    >>> mapped_once
    AwaitableWrapper(core=<coroutine object ...>)
    >>> # 3. Apply the function transform:
    >>> mapped_twice: AwaitableWrapper[str] = mapped_once.map(transform)
    >>> mapped_twice
    AwaitableWrapper(core=<coroutine object ...>)
    >>> # 4. Apply the asynchronous function write_to_disk:
    >>> mapped_thrice: AwaitableWrapper[None] = mapped_twice.map_to_awaitable(
    ...     lambda s: write_to_disk(s, "output.txt")
    ... )
    >>> mapped_thrice
    AwaitableWrapper(core=<coroutine object ...>)
    >>> # 5. Unwrap the output coroutine:
    >>> unwrapped: Coroutine[Any, Any, None] = mapped_thrice.core_as_coroutine
    >>> unwrapped
    <coroutine object ...>
    >>> # 6. Run the output coroutine:
    >>> asyncio.run(unwrapped)
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.

    ```

???+ note
    The property `core` of the class [trcks.oop.AwaitableWrapper][]
    has type [collections.abc.Awaitable][].
    On Python versions older than 3.14, [asyncio.run][] expects a
    [collections.abc.Coroutine][] object.
    Therefore, on Python versions older than 3.14,
    we need to use the property `core_as_coroutine` instead.

The method [trcks.oop.AwaitableWrapper.tap][]
allows us to execute synchronous side effects.
Similarly, the method [trcks.oop.AwaitableWrapper.tap_to_awaitable][]
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
    ...     return await (
    ...         Wrapper(core=input_path)
    ...         .map_to_awaitable(read_from_disk)
    ...         .tap(lambda s: print(f"Read '{s}' from disk."))
    ...         .map(transform)
    ...         .tap_to_awaitable(lambda s: write_to_disk(s, output_path))
    ...         .tap(lambda s: print(f"Wrote '{s}' to disk."))
    ...         .core
    ...     )
    ...
    >>> return_value = asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    Read 'Hello, world!' from disk.
    Wrote 'Length: 13' to disk.
    >>> return_value
    'Length: 13'

    ```

## Double-track code with [trcks.oop.AwaitableResultWrapper][]

Whenever we define a function using the `async def ... -> Result[F, S]` syntax,
we actually get a function with
the return type [collections.abc.Awaitable][]`[trcks.Result[F, S]]`.
The package [trcks][] provides the type alias [trcks.AwaitableResult][]`[F, S]`
for this type.
Moreover, the method [trcks.oop.Wrapper.map_to_awaitable_result][] and
the class [trcks.oop.AwaitableResultWrapper][]
allow us to combine [trcks.AwaitableResult][]-returning functions
with other [trcks.AwaitableResult][]-returning functions or
with "regular" functions:

???+ example

    ```pycon
    >>> ReadErrorLiteral = Literal["read error"]
    >>> WriteErrorLiteral = Literal["write error"]
    >>> OutOfDiskSpace = Literal["Out of disk space"]
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
    >>>
    >>> async def read_and_transform_and_write(
    ...     input_path: str, output_path: str
    ... ) -> Result[ReadErrorLiteral | WriteErrorLiteral, None]:
    ...     return await (
    ...         Wrapper(core=input_path)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .map_success(transform)
    ...         .map_success_to_awaitable_result(lambda s: write_to_disk(s, output_path))
    ...         .core
    ...     )
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
    >>> from trcks.oop import AwaitableResultWrapper
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="input.txt")
    >>> wrapped
    Wrapper(core='input.txt')
    >>> # 2. Apply the AwaitableResult function read_from_disk:
    >>> mapped_once: AwaitableResultWrapper[ReadErrorLiteral, str] = (
    ...     wrapped.map_to_awaitable_result(read_from_disk)
    ... )
    >>> mapped_once
    AwaitableResultWrapper(core=<coroutine object ...>)
    >>> # 3. Apply the function transform in the success case:
    >>> mapped_twice: AwaitableResultWrapper[ReadErrorLiteral, str] = mapped_once.map_success(
    ...     transform
    ... )
    >>> mapped_twice
    AwaitableResultWrapper(core=<coroutine object ...>)
    >>> # 4. Apply the AwaitableResult function write_to_disk in the success case:
    >>> mapped_thrice: AwaitableResultWrapper[
    ...     ReadErrorLiteral | WriteErrorLiteral, None
    ... ] = mapped_twice.map_success_to_awaitable_result(
    ...     lambda s: write_to_disk(s, "output.txt")
    ... )
    >>> mapped_thrice
    AwaitableResultWrapper(core=<coroutine object ...>)
    >>> # 5. Unwrap the output coroutine:
    >>> unwrapped: Coroutine[
    ...     Any, Any, Result[ReadErrorLiteral | WriteErrorLiteral, None]
    ... ] = mapped_thrice.core_as_coroutine
    >>> unwrapped
    <coroutine object ...>
    >>> # 6. Run the output coroutine:
    >>> asyncio.run(unwrapped)
    Read 'Hello, world!' from file input.txt.
    Wrote 'Length: 13' to file output.txt.
    ('success', None)

    ```

The methods [trcks.oop.AwaitableResultWrapper.tap_failure][] and
[trcks.oop.AwaitableResultWrapper.tap_success][]
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
    ...     return await (
    ...         Wrapper(core=input_path)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .tap_success(lambda s: print(f"LOG: Read '{s}' from disk."))
    ...         .map_success(transform)
    ...         .map_success_to_awaitable_result(lambda s: write_to_disk(s, output_path))
    ...         .tap_success(lambda _: print("LOG: Successfully wrote to disk."))
    ...         .tap_failure(lambda err: print(f"LOG: Failed with error: {err}"))
    ...         .core
    ...     )
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
The method [trcks.oop.AwaitableResultWrapper.tap_success_to_awaitable_result][]
allows us to execute such asynchronous side effects in the success case.
If the side effect returns a [trcks.AwaitableFailure][], that failure is propagated.
If the side effect returns a [trcks.AwaitableSuccess][],
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
    ...     return await (
    ...         Wrapper(core=input_path)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .tap_success(lambda s: print(f"LOG: Persisting '{s}'."))
    ...         .tap_success_to_awaitable_result(write_to_disk)
    ...         .core
    ...     )
    ...
    >>> result = asyncio.run(read_and_persist("input.txt"))
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')

    ```
