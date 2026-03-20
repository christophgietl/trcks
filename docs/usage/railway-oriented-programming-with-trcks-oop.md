# Railway-oriented programming with [trcks.oop][]

The following subsections describe how to use [trcks.oop][]
for railway-oriented programming.
Single-track and double-track code are both discussed.
So are synchronous and asynchronous code.

## Synchronous single-track code for a single value with [trcks.oop.Wrapper][]

The generic class [trcks.oop.Wrapper][][T] allows us to chain functions:

???+ example

    ```pycon
    >>> from trcks.oop import Wrapper
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return Wrapper(core=s).map(len).map(lambda n: f"Length: {n}").core
    ...
    >>> to_length_string("Hello, world!")
    'Length: 13'

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="Hello, world!")
    >>> wrapped
    Wrapper(core='Hello, world!')
    >>> # 2. Apply the builtin function len:
    >>> mapped: Wrapper[int] = wrapped.map(len)
    >>> mapped
    Wrapper(core=13)
    >>> # 3. Apply a lambda function:
    >>> mapped_again: Wrapper[str] = mapped.map(lambda n: f"Length: {n}")
    >>> mapped_again
    Wrapper(core='Length: 13')
    >>> # 4. Unwrap the output string:
    >>> unwrapped: str = mapped_again.core
    >>> unwrapped
    'Length: 13'

    ```

???+ note
    Instead of the default constructor `trcks.oop.Wrapper(core="Hello, world!")`,
    we can also use the static method `trcks.oop.Wrapper.construct("Hello, world!")`.

By following the pattern of wrapping, mapping and unwrapping,
we can write code that resembles a single-track railway
(or maybe a single-pipe pipeline).

Side effects like logging or writing to a file tend to
"consume" their input and return [None][] instead.
To avoid this, we can use the `tap` method available in
the [trcks.oop.Wrapper][] class.
This method allows executing side effects while preserving the original value:

???+ example

    ```pycon
    >>> def to_length_string(s: str) -> str:
    ...     return (
    ...         Wrapper(core=s)
    ...         .tap(lambda o: print(f"LOG: Received '{o}'."))
    ...         .map(len)
    ...         .map(lambda n: f"Length: {n}")
    ...         .tap(lambda o: print(f"LOG: Returning '{o}'."))
    ...         .core
    ...     )
    ...
    >>> output = to_length_string("Hello, world!")
    LOG: Received 'Hello, world!'.
    LOG: Returning 'Length: 13'.
    >>> output
    'Length: 13'

    ```

## Synchronous double-track code for a single value with [trcks.Result][] and [trcks.oop.ResultWrapper][]

Whenever we encounter something exceptional in conventional Python programming
(e.g. something not working as expected or some edge case in our business logic),
we usually jump
(via `raise` and `try ... except`)
to a completely different place in our codebase
that (hopefully) handles our exception.

In railway-oriented programming, however,
we tend to have two parallel code tracks:

1. a failure track and
2. a success track (a.k.a. "happy path").

This can be achieved by using the generic type [trcks.Result][][F, S]
that contains either

1. a failure value of type `F` or
2. a success value of type `S`.

The generic class [trcks.oop.ResultWrapper][][F, S] simplifies
the implementation of the parallel code tracks.

???+ example

    ```pycon
    >>> from typing import Literal
    >>> from trcks import Result
    >>> from trcks.oop import Wrapper
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
    ...     return (
    ...         Wrapper(core=user_email)
    ...         .map_to_result(get_user_id)
    ...         .map_success_to_result(get_subscription_id)
    ...         .map_success(get_subscription_fee)
    ...         .core
    ...     )
    ...
    >>> get_subscription_fee_by_email("erika.mustermann@domain.org")
    ('success', 4.2)
    >>> get_subscription_fee_by_email("john_doe@provider.com")
    ('failure', 'User does not have a subscription')
    >>> get_subscription_fee_by_email("jane_doe@provider.com")
    ('failure', 'User does not exist')

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> from trcks.oop import ResultWrapper
    >>>
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="erika.mustermann@domain.org")
    >>> wrapped
    Wrapper(core='erika.mustermann@domain.org')
    >>> # 2. Apply the Result function get_user_id:
    >>> mapped_once: ResultWrapper[UserDoesNotExist, int] = wrapped.map_to_result(
    ...     get_user_id
    ... )
    >>> mapped_once
    ResultWrapper(core=('success', 1))
    >>> # 3. Apply the Result function get_subscription_id in the success case:
    >>> mapped_twice: ResultWrapper[
    ...     FailureDescription, int
    ... ] = mapped_once.map_success_to_result(get_subscription_id)
    >>> mapped_twice
    ResultWrapper(core=('success', 42))
    >>> # 4. Apply the function get_subscription_fee in the success case:
    >>> mapped_thrice: ResultWrapper[
    ...     FailureDescription, float
    ... ] = mapped_twice.map_success(get_subscription_fee)
    >>> mapped_thrice
    ResultWrapper(core=('success', 4.2))
    >>> # 5. Unwrap the output result:
    >>> unwrapped: Result[FailureDescription, float] = mapped_thrice.core
    >>> unwrapped
    ('success', 4.2)

    ```

???+ note
    The method [trcks.oop.Wrapper.map_to_result][] returns
    a [trcks.oop.ResultWrapper][] object.
    The corresponding class [trcks.oop.ResultWrapper][]
    has a `map_failure*` and a `map_success*` method
    for each `map*` method of the class [trcks.oop.Wrapper][].

The `tap_success` and `tap_failure` methods allow us to execute side effects
in the success case or in the failure case, respectively:

???+ example

    ```pycon
    >>> def get_subscription_fee_by_email(
    ...     user_email: str
    ... ) -> Result[FailureDescription, float]:
    ...     return (
    ...         Wrapper(core=user_email)
    ...         .map_to_result(get_user_id)
    ...         .tap_success(lambda n: print(f"LOG: User ID: {n}."))
    ...         .map_success_to_result(get_subscription_id)
    ...         .map_success(get_subscription_fee)
    ...         .tap_success(lambda x: print(f"LOG: Subscription fee: {x}."))
    ...         .tap_failure(lambda fd: print(f"LOG: Failure description: {fd}."))
    ...         .core
    ...     )
    ...
    >>> fee_erika = get_subscription_fee_by_email("erika.mustermann@domain.org")
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fee_erika
    ('success', 4.2)
    >>> fee_john = get_subscription_fee_by_email("john_doe@provider.com")
    LOG: User ID: 2.
    LOG: Failure description: User does not have a subscription.
    >>> fee_john
    ('failure', 'User does not have a subscription')
    >>> fee_jane = get_subscription_fee_by_email("jane_doe@provider.com")
    LOG: Failure description: User does not exist.
    >>> fee_jane
    ('failure', 'User does not exist')

    ```

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] type.
The `tap_success_to_result` method allows us to execute such side effects
in the success case.
If the side effect returns a [trcks.Failure][], that failure is propagated.
If the side effect returns a [trcks.Success][], the original success value is preserved.

???+ example

    ```pycon
    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    ...
    >>> def get_and_persist_user_id(
    ...     user_email: str
    ... ) -> Result[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     return (
    ...         Wrapper(core=user_email)
    ...         .map_to_result(get_user_id)
    ...         .tap_success_to_result(write_to_disk)
    ...         .core
    ...     )
    ...
    >>> id_erika = get_and_persist_user_id("erika.mustermann@domain.org")
    LOG: Wrote 1 to disk.
    >>> id_erika
    ('success', 1)
    >>> id_john = get_and_persist_user_id("john_doe@provider.com")
    >>> id_john
    ('failure', 'Out of disk space')
    >>> id_jane = get_and_persist_user_id("jane_doe@provider.com")
    >>> id_jane
    ('failure', 'User does not exist')

    ```

## Asynchronous single-track code for a single value with [collections.abc.Awaitable][] and [trcks.oop.AwaitableWrapper][]

While the class [trcks.oop.Wrapper][] and its method `map` allow
the chaining of synchronous functions,
they cannot chain asynchronous functions.
To understand why,
we first need to understand the return type of asynchronous functions:

???+ example

    ```pycon
    >>> import asyncio
    >>> from collections.abc import Awaitable, Coroutine
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
we actually get a function with the return type [collections.abc.Awaitable][][T].
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

???+ example

    ```pycon
    >>> from typing import Any
    >>> from trcks.oop import AwaitableWrapper
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="input.txt")
    >>> wrapped
    Wrapper(core='input.txt')
    >>> # 2. Apply the Awaitable function read_from_disk:
    >>> mapped_once: AwaitableWrapper[str] = wrapped.map_to_awaitable(read_from_disk)
    >>> mapped_once
    AwaitableWrapper(core=<coroutine object ...>)
    >>> # 3. Apply the function transform:
    >>> mapped_twice: AwaitableWrapper[str] = mapped_once.map(transform)
    >>> mapped_twice
    AwaitableWrapper(core=<coroutine object ...>)
    >>> # 4. Apply the Awaitable function write_to_disk:
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
    Since [asyncio.run][] expects a [collections.abc.Coroutine][] object,
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

## Asynchronous double-track code for a single value with [trcks.AwaitableResult][] and [trcks.oop.AwaitableResultWrapper][]

Whenever we define a function using the `async def ... -> Result[F, S]` syntax,
we actually get a function with
the return type [collections.abc.Awaitable][][[trcks.Result][][F, S]].
The package [trcks][] provides the type alias [trcks.AwaitableResult][][F, S]
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

???+ example

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
    ...         .tap_success(lambda _: print(f"LOG: Successfully wrote to disk."))
    ...         .tap_failure(lambda err: print(f"LOG: Failed with error: {err}"))
    ...         .core
    ...     )
    ...
    >>> result_1 = asyncio.run(read_and_transform_and_write("input.txt", "output.txt"))
    LOG: Read 'Hello, world!' from disk.
    LOG: Successfully wrote to disk.
    >>> result_1
    ('success', None)
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
    ...         .tap_success(lambda s: print(f"LOG: Read '{s}' from disk."))
    ...         .tap_success(lambda s: print(f"LOG: Persisting '{s}'."))
    ...         .tap_success_to_awaitable_result(write_to_disk)
    ...         .core
    ...     )
    ...
    >>> result = asyncio.run(read_and_persist("input.txt"))
    LOG: Read 'Hello, world!' from disk.
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')

    ```

## Synchronous single-track code for a sequence with [collections.abc.Sequence][] and [trcks.oop.SequenceWrapper][]

While the class [trcks.oop.Wrapper][] wraps and operates on a single value,
the class [trcks.oop.SequenceWrapper][] wraps a [collections.abc.Sequence][]
and applies operations to each element individually.
This is useful when we need to process multiple values
through the same chain of transformations:

???+ example

    ```pycon
    >>> from trcks.oop import SequenceWrapper
    >>>
    >>> def normalize_email(email: str) -> str:
    ...     return email.strip().lower()
    ...
    >>> def to_domain(email: str) -> str:
    ...     return email.split("@")[1]
    ...
    >>> emails = ["  Erika@Domain.ORG ", "JOHN@Provider.COM  "]
    >>> (
    ...     SequenceWrapper
    ...     .construct_from_sequence(emails)
    ...     .map(normalize_email)
    ...     .map(to_domain)
    ...     .core
    ... )
    ['domain.org', 'provider.com']

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> from collections.abc import Sequence
    >>> # 1. Wrap the input sequence:
    >>> wrapped: SequenceWrapper[str] = SequenceWrapper.construct_from_sequence(
    ...     ["  Erika@Domain.ORG ", "JOHN@Provider.COM  "]
    ... )
    >>> wrapped
    SequenceWrapper(core=['  Erika@Domain.ORG ', 'JOHN@Provider.COM  '])
    >>> # 2. Apply normalize_email to each element:
    >>> mapped: SequenceWrapper[str] = wrapped.map(normalize_email)
    >>> mapped
    SequenceWrapper(core=['erika@domain.org', 'john@provider.com'])
    >>> # 3. Apply to_domain to each element:
    >>> mapped_again: SequenceWrapper[str] = mapped.map(to_domain)
    >>> mapped_again
    SequenceWrapper(core=['domain.org', 'provider.com'])
    >>> # 4. Unwrap the output sequence:
    >>> unwrapped: Sequence[str] = mapped_again.core
    >>> unwrapped
    ['domain.org', 'provider.com']

    ```

???+ note
    [trcks.oop.SequenceWrapper.construct][] wraps a single value
    in a one-element sequence:
    `SequenceWrapper.construct(42)` produces `SequenceWrapper(core=[42])`.

    The method [trcks.oop.SequenceWrapper.map_to_sequence][]
    applies a function that returns a [collections.abc.Sequence][]
    to each element and flattens the results (like a "flat map"):

    ```pycon
    >>> SequenceWrapper.construct_from_sequence(
    ...     ["ab", "cd"]
    ... ).map_to_sequence(list).core
    ['a', 'b', 'c', 'd']

    ```

The `tap` method allows executing side effects for each element
while preserving the original sequence:

???+ example

    ```pycon
    >>> sequence_wrapper = (
    ...     SequenceWrapper
    ...     .construct_from_sequence(emails)
    ...     .map(normalize_email)
    ...     .tap(lambda e: print(f"LOG: Processing '{e}'."))
    ...     .map(to_domain)
    ... )
    LOG: Processing 'erika@domain.org'.
    LOG: Processing 'john@provider.com'.
    >>> sequence_wrapper.core
    ['domain.org', 'provider.com']

    ```

## Synchronous double-track code for a sequence with [trcks.ResultSequence][] and [trcks.oop.ResultSequenceWrapper][]

When applying a failable function to each element in a sequence,
we need the [trcks.oop.ResultSequenceWrapper][] class.
The success track methods are named `map_successes` and `tap_successes` (plural)
because they operate on each element in the [trcks.SuccessSequence][] individually.
Processing short-circuits on the first [trcks.Failure][].

???+ example

    ```pycon
    >>> from typing import Literal
    >>> from trcks import Result, ResultSequence
    >>> from trcks.oop import SequenceWrapper
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
    ...     return (
    ...         SequenceWrapper
    ...         .construct_from_sequence(user_emails)
    ...         .map_to_result(get_user_id)
    ...         .map_successes_to_result(get_subscription_id)
    ...         .map_successes(get_subscription_fee)
    ...         .core
    ...     )
    ...
    >>> get_subscription_fees_by_email(["erika.mustermann@domain.org"])
    ('success', [4.2])
    >>> get_subscription_fees_by_email(
    ...     ["erika.mustermann@domain.org", "john_doe@provider.com"]
    ... )
    ('failure', 'User does not have a subscription')
    >>> get_subscription_fees_by_email(["jane_doe@provider.com"])
    ('failure', 'User does not exist')

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> from trcks.oop import ResultSequenceWrapper
    >>>
    >>> # 1. Wrap the input sequence:
    >>> wrapped: SequenceWrapper[str] = SequenceWrapper.construct_from_sequence(
    ...     ["erika.mustermann@domain.org"]
    ... )
    >>> wrapped
    SequenceWrapper(core=['erika.mustermann@domain.org'])
    >>> # 2. Apply the Result function get_user_id to each element:
    >>> mapped_once: ResultSequenceWrapper[
    ...     UserDoesNotExist, int
    ... ] = wrapped.map_to_result(get_user_id)
    >>> mapped_once
    ResultSequenceWrapper(core=('success', [1]))
    >>> # 3. Apply the Result function get_subscription_id to each element:
    >>> mapped_twice: ResultSequenceWrapper[
    ...     FailureDescription, int
    ... ] = mapped_once.map_successes_to_result(get_subscription_id)
    >>> mapped_twice
    ResultSequenceWrapper(core=('success', [42]))
    >>> # 4. Apply get_subscription_fee to each element:
    >>> mapped_thrice: ResultSequenceWrapper[
    ...     FailureDescription, float
    ... ] = mapped_twice.map_successes(get_subscription_fee)
    >>> mapped_thrice
    ResultSequenceWrapper(core=('success', [4.2]))
    >>> # 5. Unwrap the output result sequence:
    >>> unwrapped: ResultSequence[FailureDescription, float] = mapped_thrice.core
    >>> unwrapped
    ('success', [4.2])

    ```

???+ note
    The method [trcks.oop.SequenceWrapper.map_to_result][]
    returns a [trcks.oop.ResultSequenceWrapper][] object.
    The corresponding class [trcks.oop.ResultSequenceWrapper][]
    has a `map_failure*` and a `map_successes*` method
    for each `map*` method of the class [trcks.oop.SequenceWrapper][].
    Note the plural `map_successes` (instead of `map_success`)
    since the method operates on each element in the sequence.

The `tap_successes` and `tap_failure` methods allow us to execute side effects
in the success case (for each element) or in the failure case, respectively:

???+ example

    ```pycon
    >>> def get_subscription_fees_by_email(
    ...     user_emails: list[str],
    ... ) -> ResultSequence[FailureDescription, float]:
    ...     return (
    ...         SequenceWrapper
    ...         .construct_from_sequence(user_emails)
    ...         .map_to_result(get_user_id)
    ...         .tap_successes(lambda n: print(f"LOG: User ID: {n}."))
    ...         .map_successes_to_result(get_subscription_id)
    ...         .map_successes(get_subscription_fee)
    ...         .tap_successes(lambda x: print(f"LOG: Subscription fee: {x}."))
    ...         .tap_failure(lambda fd: print(f"LOG: Failure: {fd}."))
    ...         .core
    ...     )
    ...
    >>> fees_erika = get_subscription_fees_by_email(
    ...     ["erika.mustermann@domain.org"]
    ... )
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fees_erika
    ('success', [4.2])
    >>> fees_john = get_subscription_fees_by_email(
    ...     ["john_doe@provider.com"]
    ... )
    LOG: User ID: 2.
    LOG: Failure: User does not have a subscription.
    >>> fees_john
    ('failure', 'User does not have a subscription')
    >>> fees_jane = get_subscription_fees_by_email(
    ...     ["jane_doe@provider.com"]
    ... )
    LOG: Failure: User does not exist.
    >>> fees_jane
    ('failure', 'User does not exist')

    ```

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] type.
The `tap_successes_to_result` method allows us to execute such side effects
for each element in the success case.
If the side effect returns a [trcks.Failure][] for any element,
that failure is propagated.
If the side effect returns a [trcks.Success][] for all elements,
the original success values are preserved.

???+ example

    ```pycon
    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    ...
    >>> def get_and_persist_user_ids(
    ...     user_emails: list[str],
    ... ) -> ResultSequence[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     return (
    ...         SequenceWrapper
    ...         .construct_from_sequence(user_emails)
    ...         .map_to_result(get_user_id)
    ...         .tap_successes_to_result(write_to_disk)
    ...         .core
    ...     )
    ...
    >>> ids_erika = get_and_persist_user_ids(["erika.mustermann@domain.org"])
    LOG: Wrote 1 to disk.
    >>> ids_erika
    ('success', [1])
    >>> ids_john = get_and_persist_user_ids(["john_doe@provider.com"])
    >>> ids_john
    ('failure', 'Out of disk space')
    >>> ids_jane = get_and_persist_user_ids(["jane_doe@provider.com"])
    >>> ids_jane
    ('failure', 'User does not exist')

    ```

## Asynchronous single-track code for a sequence with [trcks.AwaitableSequence][] and [trcks.oop.AwaitableSequenceWrapper][]

While the class [trcks.oop.SequenceWrapper][] and its method `map`
allow the chaining of synchronous functions for each element,
they cannot chain asynchronous functions.
The method [trcks.oop.SequenceWrapper.map_to_awaitable][]
and the class [trcks.oop.AwaitableSequenceWrapper][]
allow us to combine [collections.abc.Awaitable][]-returning functions
with other [collections.abc.Awaitable][]-returning functions or
with "regular" functions,
applied to each element in the sequence:

???+ example

    ```pycon
    >>> import asyncio
    >>> from collections.abc import Sequence
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
    ...     return await (
    ...         SequenceWrapper
    ...         .construct_from_sequence(input_paths)
    ...         .map_to_awaitable(read_from_disk)
    ...         .map(transform)
    ...         .core
    ...     )
    ...
    >>> asyncio.run(read_and_transform(["a.txt", "b.txt"]))
    ['Length: 5', 'Length: 5']

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> from trcks.oop import AwaitableSequenceWrapper
    >>> # 1. Wrap the input sequence:
    >>> wrapped: SequenceWrapper[str] = SequenceWrapper.construct_from_sequence(
    ...     ["a.txt", "b.txt"]
    ... )
    >>> wrapped
    SequenceWrapper(core=['a.txt', 'b.txt'])
    >>> # 2. Apply the Awaitable function read_from_disk to each element:
    >>> mapped_once: AwaitableSequenceWrapper[str] = wrapped.map_to_awaitable(
    ...     read_from_disk
    ... )
    >>> mapped_once
    AwaitableSequenceWrapper(core=<coroutine object ...>)
    >>> # 3. Apply the function transform to each element:
    >>> mapped_twice: AwaitableSequenceWrapper[str] = mapped_once.map(transform)
    >>> mapped_twice
    AwaitableSequenceWrapper(core=<coroutine object ...>)
    >>> # 4. Unwrap and run the output coroutine:
    >>> asyncio.run(mapped_twice.core_as_coroutine)
    ['Length: 5', 'Length: 5']

    ```

???+ note
    The property `core` of the class [trcks.oop.AwaitableSequenceWrapper][]
    has type [trcks.AwaitableSequence][].
    Since [asyncio.run][] expects a [collections.abc.Coroutine][] object,
    we need to use the property `core_as_coroutine` instead.

The method [trcks.oop.AwaitableSequenceWrapper.tap][]
allows us to execute synchronous side effects for each element.
Similarly, the method [trcks.oop.AwaitableSequenceWrapper.tap_to_awaitable][]
allows us to execute asynchronous side effects for each element.

???+ example

    ```pycon
    >>> async def read_from_disk(path: str) -> str:
    ...     await asyncio.sleep(0.001)
    ...     contents = {"a.txt": "Hello", "b.txt": "World"}
    ...     return contents[path]
    ...
    >>> async def read_and_transform(
    ...     input_paths: list[str],
    ... ) -> Sequence[str]:
    ...     return await (
    ...         SequenceWrapper
    ...         .construct_from_sequence(input_paths)
    ...         .map_to_awaitable(read_from_disk)
    ...         .tap(lambda s: print(f"Read '{s}' from disk."))
    ...         .map(transform)
    ...         .tap(lambda s: print(f"Transformed to '{s}'."))
    ...         .core
    ...     )
    ...
    >>> result = asyncio.run(read_and_transform(["a.txt", "b.txt"]))
    Read 'Hello' from disk.
    Read 'World' from disk.
    Transformed to 'Length: 5'.
    Transformed to 'Length: 5'.
    >>> result
    ['Length: 5', 'Length: 5']

    ```

## Asynchronous double-track code for a sequence with [trcks.AwaitableResultSequence][] and [trcks.oop.AwaitableResultSequenceWrapper][]

Whenever we define a function using
the `async def ... -> Result[F, S]` syntax
and want to apply it to each element in a sequence,
we need the [trcks.oop.AwaitableResultSequenceWrapper][] class.
The package [trcks][] provides the type alias
[trcks.AwaitableResultSequence][][F, S]
for `Awaitable[ResultSequence[F, S]]`.
The success track methods are named `map_successes` and `tap_successes` (plural)
because they operate on each element individually.
Processing short-circuits on the first [trcks.Failure][].

???+ example

    ```pycon
    >>> from trcks import AwaitableResultSequence
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
    ...     return await (
    ...         SequenceWrapper
    ...         .construct_from_sequence(input_paths)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .map_successes(transform)
    ...         .tap_successes_to_awaitable_result(
    ...             lambda s: write_to_disk(s, output_path)
    ...         )
    ...         .core
    ...     )
    ...
    >>> asyncio.run(
    ...     read_and_transform_and_write(["a.txt", "b.txt"], "output.txt")
    ... )
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ['Length: 5', 'Length: 5'])

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

???+ example

    ```pycon
    >>> from trcks.oop import AwaitableResultSequenceWrapper
    >>> # 1. Wrap the input sequence:
    >>> wrapped: SequenceWrapper[str] = SequenceWrapper.construct_from_sequence(
    ...     ["a.txt", "b.txt"]
    ... )
    >>> wrapped
    SequenceWrapper(core=['a.txt', 'b.txt'])
    >>> # 2. Apply the AwaitableResult function read_from_disk to each element:
    >>> mapped_once: AwaitableResultSequenceWrapper[
    ...     ReadErrorLiteral, str
    ... ] = wrapped.map_to_awaitable_result(read_from_disk)
    >>> mapped_once
    AwaitableResultSequenceWrapper(core=<coroutine object ...>)
    >>> # 3. Apply the function transform to each element in the success case:
    >>> mapped_twice: AwaitableResultSequenceWrapper[
    ...     ReadErrorLiteral, str
    ... ] = mapped_once.map_successes(transform)
    >>> mapped_twice
    AwaitableResultSequenceWrapper(core=<coroutine object ...>)
    >>> # 4. Apply the failable async side effect write_to_disk to each element:
    >>> mapped_thrice: AwaitableResultSequenceWrapper[
    ...     ReadErrorLiteral | WriteErrorLiteral, str
    ... ] = mapped_twice.tap_successes_to_awaitable_result(
    ...     lambda s: write_to_disk(s, "output.txt")
    ... )
    >>> mapped_thrice
    AwaitableResultSequenceWrapper(core=<coroutine object ...>)
    >>> # 5. Unwrap and run the output coroutine:
    >>> asyncio.run(mapped_thrice.core_as_coroutine)
    Wrote 'Length: 5' to file output.txt.
    Wrote 'Length: 5' to file output.txt.
    ('success', ['Length: 5', 'Length: 5'])

    ```

The methods [trcks.oop.AwaitableResultSequenceWrapper.tap_failure][] and
[trcks.oop.AwaitableResultSequenceWrapper.tap_successes][]
allow us to execute synchronous side effects
in the failure case or in the success case (for each element), respectively:

???+ example

    ```pycon
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
    ...     return await (
    ...         SequenceWrapper
    ...         .construct_from_sequence(input_paths)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .tap_successes(lambda s: print(f"LOG: Read '{s}' from disk."))
    ...         .map_successes(transform)
    ...         .tap_successes_to_awaitable_result(
    ...             lambda s: write_to_disk(s, output_path)
    ...         )
    ...         .tap_successes(lambda _: print("LOG: Successfully wrote to disk."))
    ...         .tap_failure(lambda err: print(f"LOG: Failed with error: {err}"))
    ...         .core
    ...     )
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
    >>> result_2 = asyncio.run(
    ...     read_and_transform_and_write(["missing.txt"], "output.txt")
    ... )
    LOG: Failed with error: read error
    >>> result_2
    ('failure', 'read error')

    ```

Sometimes, side effects themselves can fail and
need to return an [trcks.AwaitableResult][] type.
The method
[trcks.oop.AwaitableResultSequenceWrapper.tap_successes_to_awaitable_result][]
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
    ...     return await (
    ...         SequenceWrapper
    ...         .construct_from_sequence(input_paths)
    ...         .map_to_awaitable_result(read_from_disk)
    ...         .tap_successes(lambda s: print(f"LOG: Persisting '{s}'."))
    ...         .tap_successes_to_awaitable_result(write_to_disk)
    ...         .core
    ...     )
    ...
    >>> result = asyncio.run(read_and_persist(["a.txt", "b.txt"]))
    LOG: Persisting 'Hi'.
    LOG: Persisting 'Hello, world!'.
    >>> result
    ('failure', 'Out of disk space')

    ```
