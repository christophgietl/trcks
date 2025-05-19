# trcks

`trcks` is a Python library.
It allows
[railway-oriented programming](https://fsharpforfunandprofit.com/rop/)
in two different programming styles:

1. an *object-oriented style* based on method chaining and
2. a *functional style* based on function composition.

## Motivation

The following subsections motivate
railway-oriented programming in general and
the `trcks` library in particular.

### Why should I use railway-oriented programming?

When writing modular Python code,
return type annotations are extremely helpful.
They help humans
(and maybe [LLMs](https://en.wikipedia.org/w/index.php?title=Large_language_model&oldid=1283157830))
to understand the purpose of a function.
And they allow static type checkers (e.g. `mypy` or `pyright`)
to check whether functions fit together:

```pycon
>>> def get_user_id(user_email: str) -> int:
...     if user_email == "erika.mustermann@domain.org":
...         return 1
...     if user_email == "john_doe@provider.com":
...         return 2
...     raise Exception("User does not exist")
...
>>> def get_subscription_id(user_id: int) -> int:
...     if user_id == 1:
...         return 42
...     raise Exception("User does not have a subscription")
...
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
...
>>> def get_subscription_fee_by_email(user_email: str) -> float:
...     return get_subscription_fee(get_subscription_id(get_user_id(user_email)))
...
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
4.2

```

Unfortunately, conventional return type annotations do not always tell the full story:

```pycon
>>> get_subscription_id(user_id=2)
Traceback (most recent call last):
    ...
Exception: User does not have a subscription

```

We can document (domain) exceptions in the docstring of the function:

```pycon
>>> def get_subscription_id(user_id: int) -> int:
...     """Look up the subscription ID for a user.
...
...     Raises:
...         Exception: If the user does not have a subscription.
...     """
...     if user_id == 1:
...         return 42
...     raise Exception("User does not have a subscription")
...

```

While this helps humans (and maybe LLMs),
static type checkers usually ignore docstrings.
Moreover, it is difficult
to document all (domain) exceptions in the docstring and
to keep this documentation up-to-date.
Therefore, we should use railway-oriented programming.


### How can I use railway-oriented programming?

Instead of raising exceptions (and documenting this behavior in the docstring),
we return a `Result` type:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>>
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>>
>>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
...
>>> get_subscription_id(user_id=1)
('success', 42)
>>> get_subscription_id(user_id=2)
('failure', 'User does not have a subscription')

```

This return type

1. describes the success case *and* the failure case and
2. is verified by static type checkers.

### What do I need for railway-oriented programming?

Combining `Result`-returning functions
with other `Result`-returning functions or with "regular" functions
can be cumbersome.
Moreover, it can lead to repetitive code patterns:

```pycon
>>> from typing import Union
>>>
>>> UserDoesNotExist = Literal["User does not exist"]
>>> FailureDescription = Union[UserDoesNotExist, UserDoesNotHaveASubscription]
>>>
>>> def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
...     if user_email == "erika.mustermann@domain.org":
...         return "success", 1
...     if user_email == "john_doe@provider.com":
...         return "success", 2
...     return "failure", "User does not exist"
...
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
...     # Apply get_user_id:
...     user_id_result = get_user_id(user_email)
...     if user_id_result[0] == "failure":
...         return user_id_result
...     user_id = user_id_result[1]
...     # Apply get_subscription_id:
...     subscription_id_result = get_subscription_id(user_id)
...     if subscription_id_result[0] == "failure":
...         return subscription_id_result
...     subscription_id = subscription_id_result[1]
...     # Apply get_subscription_fee:
...     subscription_fee = get_subscription_fee(subscription_id)
...     # Return result:
...     return "success", subscription_fee
...
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

Therefore, we need a library that helps us combine functions.

### How does the module `trcks.oop` help with function combination?

The module `trcks.oop` supports combining functions in an object-oriented style
using method chaining:

```pycon
>>> from trcks.oop import Wrapper
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
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

### How does the package `trcks.fp` help with function combination?

The package `trcks.fp` supports combining functions in a functional style
using function composition:

```pycon
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import result as r
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
...     # If your static type checker cannot infer
...     # the type of the argument passed to `pipe`,
...     # explicit type assignment can help:
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

```

## Usage

The following subsections describe the usage of `trcks`, `trcks.oop` and `trcks.fp`.

### Tuple types provided by `trcks`

The generic type `trcks.Failure[F]` describes all `tuple`s of length 2
with the string `"failure"` as the first element and a second element of type `F`.
Usually, the second element is a string, an exception or an enum value:

```pycon
>>> import enum
>>> from typing import Literal
>>> from trcks import Failure
>>>
>>> UserDoesNotExistLiteral = Literal["User does not exist"]
>>> literal_failure: Failure[UserDoesNotExistLiteral] = ("failure", "User does not exist")
>>>
>>> class UserDoesNotExistException(Exception):
...     pass
...
>>> exception_failure: Failure[UserDoesNotExistException] = ("failure", UserDoesNotExistException())
>>>
>>> class ErrorEnum(enum.Enum):
...     USER_DOES_NOT_EXIST = enum.auto
...
>>> enum_failure: Failure[ErrorEnum] = ("failure", ErrorEnum.USER_DOES_NOT_EXIST)

```

The generic type `trcks.Success[S]` describes all `tuple`s of length 2
with the string `"success"` as the first element and a second element of type `S`.
Here, `S` can be any type.

```pycon
>>> from decimal import Decimal
>>> from pathlib import Path
>>> from trcks import Success
>>>
>>> decimal_success: Success[Decimal] = ("success", Decimal("3.14"))
>>> float_list_success: Success[list[float]] = ("success", [1.0, 2.0, 3.0])
>>> int_success: Success[int] = ("success", 42)
>>> path_success: Success[Path] = ("success", Path("/tmp/my-file.txt"))
>>> str_success: Success[str] = ("success", "foo")

```

The generic type `trcks.Result[F, S]` is the union of `Failure[F]` and `Success[S]`.
It is primarily used as a return type for functions:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>>
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>>
>>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
...
>>> get_subscription_id(user_id=1)
('success', 42)
>>> get_subscription_id(user_id=2)
('failure', 'User does not have a subscription')

```

### Railway-oriented programming with `trcks.oop`

The following subsections describe how to use `trcks.oop` for railway-oriented programming.
Single-track and double-track code are both discussed.
So are synchronous and asynchronous code.

#### Synchronous single-track code with `trcks.oop.Wrapper`

The generic class `trcks.oop.Wrapper[T]` allows us to chain functions like this:

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

```pycon
>>> from trcks.oop import Wrapper
>>>
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
>>> # 4. Unwrap the final result:
>>> unwrapped: str = mapped_again.core
>>> unwrapped
'Length: 13'

```

*Note:* Instead of the default constructor `Wrapper(core="Hello, world!")`,
we can also use the static method `Wrapper.construct("Hello, world!")`.

By following the pattern of wrapping, mapping and unwrapping,
we can write code that resembles a single-track railway
(or maybe a pipeline).

#### Synchronous double-track code with `trcks.Result` and `trcks.oop.ResultWrapper`

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

This can be achieved by using the generic type `trcks.Result[F, S]`
that contains either

1. a failure value of type `F` or
2. a success value of type `S`.

The generic class `trcks.oop.ResultWrapper[F, S]` simplifies
the implementation of the parallel code tracks.

```pycon
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
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
>>> mapped_two_times: ResultWrapper[
...     Union[UserDoesNotExist, UserDoesNotHaveASubscription], int
... ] = mapped_once.map_success_to_result(get_subscription_id)
>>> mapped_two_times
ResultWrapper(core=('success', 42))
>>> # 4. Apply the function get_subscription_fee in the success case:
>>> mapped_three_times: ResultWrapper[
...     Union[UserDoesNotExist, UserDoesNotHaveASubscription], float
... ] = mapped_two_times.map_success(get_subscription_fee)
>>> mapped_three_times
ResultWrapper(core=('success', 4.2))
>>> # 5. Unwrap the final result:
>>> unwrapped: Result[
...     Union[UserDoesNotExist, UserDoesNotHaveASubscription], float
... ] = mapped_three_times.core
>>> unwrapped
('success', 4.2)

```

*Note:* The method `Wrapper.map_to_result` returns a `ResultWrapper` object.
The class `ResultWrapper` has a `map_failure*` and a `map_success*` method
for each `map*` method of the class `Wrapper`.

#### Asynchronous single-track code with `trcks.oop.AwaitableWrapper`

```pycon
>>> import asyncio
>>> from trcks.oop import Wrapper
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
>>> async def read_and_transform_and_write(input_path: str, output_path: str) -> None:
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

```pycon
>>> from collections.abc import Coroutine
>>> from typing import Any
>>> from trcks.oop import AwaitableWrapper
>>> wrapped: Wrapper[str] = Wrapper(core="input.txt")
>>> wrapped
Wrapper(core='input.txt')
>>> mapped_once: AwaitableWrapper[str] = wrapped.map_to_awaitable(read_from_disk)
>>> mapped_once
AwaitableWrapper(core=<coroutine object ...>)
>>> mapped_twice: AwaitableWrapper[str] = mapped_once.map(transform)
>>> mapped_twice
AwaitableWrapper(core=<coroutine object ...>)
>>> mapped_thrice: AwaitableWrapper[None] = mapped_twice.map_to_awaitable(
...     lambda s: write_to_disk(s, "output.txt")
... )
>>> mapped_thrice
AwaitableWrapper(core=<coroutine object ...>)
>>> unwrapped: Coroutine[Any, Any, None] = mapped_thrice.core_as_coroutine
>>> unwrapped
<coroutine object ...>
>>> asyncio.run(unwrapped)
Read 'Hello, world!' from file input.txt.
Wrote 'Length: 13' to file output.txt.

```

#### Asynchronous double-track code with `trcks.oop.AwaitableResultWrapper`

```pycon
>>> import asyncio
>>> from typing import Literal, Union
>>> from trcks import Result
>>> from trcks.oop import Wrapper
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
>>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
...     if path != "output.txt":
...         return "failure", "write error"
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to file {path}.")
...     return "success", None
...
>>> 
>>> async def read_and_transform_and_write(
...     input_path: str, output_path: str
... ) -> Result[Union[ReadErrorLiteral, WriteErrorLiteral], None]:
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

```pycon
>>> from collections.abc import Coroutine
>>> from typing import Any
>>> from trcks.oop import AwaitableResultWrapper
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
>>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
...     if path != "output.txt":
...         return "failure", "write error"
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to file {path}.")
...     return "success", None
...
>>> wrapped: Wrapper[str] = Wrapper(core="input.txt")
>>> wrapped
Wrapper(core='input.txt')
>>> mapped_once: AwaitableResultWrapper[ReadErrorLiteral, str] = (
...     wrapped.map_to_awaitable_result(read_from_disk)
... )
>>> mapped_once
AwaitableResultWrapper(core=<coroutine object ...>)
>>> mapped_twice: AwaitableResultWrapper[ReadErrorLiteral, str] = mapped_once.map_success(
...     transform
... )
>>> mapped_twice
AwaitableResultWrapper(core=<coroutine object ...>)
>>> mapped_thrice: AwaitableResultWrapper[
...     Union[ReadErrorLiteral, WriteErrorLiteral], None
... ] = mapped_twice.map_success_to_awaitable_result(
...     lambda s: write_to_disk(s, "output.txt")
... )
>>> mapped_thrice
AwaitableResultWrapper(core=<coroutine object ...>)
>>> unwrapped: Coroutine[
...     Any, Any, Result[Union[ReadErrorLiteral, WriteErrorLiteral], None]
... ] = mapped_thrice.core_as_coroutine
>>> unwrapped
<coroutine object ...>
>>> asyncio.run(unwrapped)
Read 'Hello, world!' from file input.txt.
Wrote 'Length: 13' to file output.txt.
('success', None)

```

### Railway-oriented programming with `trcks.fp`

The following subsections describe how to use `trcks.fp` for railway-oriented programming.
Single-track and double-track code are both discussed.
So are synchronous and asynchronous code.

#### Synchronous single-track code with `trcks.fp.composition`

The function `trcks.fp.composition.pipe` allows us to chain functions like this:

```pycon
>>> from trcks.fp.composition import pipe
>>> def to_length_string(s: str) -> str:
...     return pipe((s, len, lambda n: f"Length: {n}"))
...
>>> to_length_string("Hello, world!")
'Length: 13'

```

To understand what is going on here,
let us have a look at the individual steps of the chain:

```pycon
>>> pipe(("Hello, world!",))
'Hello, world!'
>>> pipe(("Hello, world!", len))
13
>>> pipe(("Hello, world!", len, lambda n: f"Length: {n}"))
'Length: 13'

```

#### Synchronous double-track code with `trcks.fp.composition` and `trcks.fp.monads.result`

```pycon
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
...     # If your static type checker cannot infer
...     # the type of the argument passed to `pipe`,
...     # explicit type assignment can help:
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

```

To understand what is going on here,
let us have a look at the individual steps of the chain:

```pycon
>>> from trcks.fp.composition import Pipeline0, Pipeline1, Pipeline2, Pipeline3, pipe
>>> p0: Pipeline0[str] = ("erika.mustermann@domain.org",)
>>> pipe(p0)
'erika.mustermann@domain.org'
>>> p1: Pipeline1[str, Result[UserDoesNotExist, int]] = (
...     "erika.mustermann@domain.org",
...     get_user_id,
... )
>>> pipe(p1)
('success', 1)
>>> p2: Pipeline2[str, Result[UserDoesNotExist, int], Result[FailureDescription, int]] = (
...     "erika.mustermann@domain.org",
...     get_user_id,
...     r.map_success_to_result(get_subscription_id),
... )
>>> pipe(p2)
('success', 42)
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

```

#### Asynchronous single-track code with `trcks.fp.composition` and `trcks.fp.monads.awaitable`

```pycon
>>> import asyncio
>>> from collections.abc import Awaitable
>>> from trcks.fp.composition import pipe, Pipeline3
>>> from trcks.fp.monads import awaitable as a
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
>>> async def read_and_transform_and_write(input_path: str, output_path: str) -> None:
...     p: Pipeline3[str, Awaitable[str], Awaitable[str], Awaitable[None]] = (
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

```pycon
>>> from trcks.fp.composition import Pipeline1, Pipeline2, Pipeline3, pipe
>>> p1: Pipeline1[str, Awaitable[str]] = (
...     "input.txt",
...     read_from_disk,
... )
>>> asyncio.run(a.to_coroutine(pipe(p1)))
Read 'Hello, world!' from file input.txt.
'Hello, world!'
>>> p2: Pipeline2[str, Awaitable[str], Awaitable[str]] = (
...     "input.txt",
...     read_from_disk,
...     a.map_(transform),
... )
>>> asyncio.run(a.to_coroutine(pipe(p2)))
Read 'Hello, world!' from file input.txt.
'Length: 13'
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

#### Asynchronous double-track code with `trcks.fp.composition` and `trcks.fp.monads.awaitable_result`

```pycon
>>> import asyncio
>>> from typing import Literal, Union
>>> from trcks import AwaitableResult, Result
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import awaitable_result as ar
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
>>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
...     if path != "output.txt":
...         return "failure", "write error"
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to file {path}.")
...     return "success", None
...
>>> async def read_and_transform_and_write(
...     input_path: str, output_path: str
... ) -> Result[Union[ReadErrorLiteral, WriteErrorLiteral], None]:
...     p: Pipeline3[
...         str,
...         AwaitableResult[ReadErrorLiteral, str],
...         AwaitableResult[ReadErrorLiteral, str],
...         AwaitableResult[Union[ReadErrorLiteral, WriteErrorLiteral], None],
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

```pycon
>>> import asyncio
>>> from typing import Literal, Union
>>> from trcks import AwaitableResult, Result
>>> from trcks.fp.composition import Pipeline1, Pipeline2, Pipeline3, pipe
>>> from trcks.fp.monads import awaitable_result as ar
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
>>> async def write_to_disk(s: str, path: str) -> Result[WriteErrorLiteral, None]:
...     if path != "output.txt":
...         return "failure", "write error"
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to file {path}.")
...     return "success", None
...
>>> p1: Pipeline1[str, AwaitableResult[ReadErrorLiteral, str]] = (
...     "input.txt",
...     read_from_disk,
... )
>>> asyncio.run(ar.to_coroutine_result(pipe(p1)))
Read 'Hello, world!' from file input.txt.
('success', 'Hello, world!')
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
>>> p3: Pipeline3[
...     str,
...     AwaitableResult[ReadErrorLiteral, str],
...     AwaitableResult[ReadErrorLiteral, str],
...     AwaitableResult[Union[ReadErrorLiteral, WriteErrorLiteral], None],
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
