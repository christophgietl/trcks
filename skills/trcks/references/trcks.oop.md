# Wrapper classes provided by `trcks.oop`

## Combining "regular" functions

The module `trcks.oop` defines the wrapper class `Wrapper`
for combining "regular" functions with other "regular" functions.
Wrap a value, chain `map` calls, and unwrap the result
with the `core` attribute:

```pycon
>>> from trcks.oop import Wrapper
>>>
>>> def get_user_id(user_email: str) -> int:
...     if user_email == "erika.mustermann@domain.org":
...         return 1
...     if user_email == "john_doe@provider.com":
...         return 2
...     return 3
>>>
>>> def get_subscription_id(user_id: int) -> int:
...     if user_id == 1:
...         return 42
...     if user_id == 2:
...         return 44
...     return 45
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> float:
...     return (
...         Wrapper(core=user_email)
...         .map(get_user_id)
...         .map(get_subscription_id)
...         .map(get_subscription_fee)
...         .core
...     )
>>>
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
4.2
>>> get_subscription_fee_by_email("john_doe@provider.com")
4.4
>>> get_subscription_fee_by_email("jane_doe@provider.com")
4.5

```

Side effects like logging tend to "consume" their input
and return `None` instead.
The `Wrapper` class provides the `tap` method.
It applies a side effect without changing the wrapped value:

```pycon
>>> from trcks.oop import Wrapper
>>>
>>> def get_user_id(user_email: str) -> int:
...     if user_email == "erika.mustermann@domain.org":
...         return 1
...     if user_email == "john_doe@provider.com":
...         return 2
...     return 3
>>>
>>> def get_subscription_id(user_id: int) -> int:
...     if user_id == 1:
...         return 42
...     if user_id == 2:
...         return 44
...     return 45
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> float:
...     return (
...         Wrapper(core=user_email)
...         .tap(lambda o: print(f"LOG: Received '{o}'."))
...         .map(get_user_id)
...         .map(get_subscription_id)
...         .map(get_subscription_fee)
...         .core
...     )
>>>
>>> output = get_subscription_fee_by_email("erika.mustermann@domain.org")
LOG: Received 'erika.mustermann@domain.org'.
>>> output
4.2

```

Each method in the second example returns a new, immutable wrapper instance:

- `Wrapper.tap(...)` returns a `Wrapper[str]` instance
  that wraps the original string.
- `Wrapper.map(get_user_id)` returns a `Wrapper[int]` instance.
- `Wrapper.map(get_subscription_id)` returns a `Wrapper[int]` instance.
- `Wrapper.map(get_subscription_fee)` returns a `Wrapper[float]` instance.

## Combining `trcks.Result`-returning functions

The module `trcks.oop` also defines wrapper classes
for combining `trcks.Result`-returning functions
with other `trcks.Result`-returning functions and
with "regular" functions:

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
>>>
>>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
...     return (
...         Wrapper(core=user_email)
...         .map_to_result(get_user_id)
...         .map_success_to_result(get_subscription_id)
...         .map_success(get_subscription_fee)
...         .core
...     )
>>>
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

Each `map*` method in this example returns a new, immutable wrapper instance:

- `Wrapper.map_to_result(get_user_id)` returns a
  `ResultWrapper[UserDoesNotExist, int]` instance.
- `ResultWrapper.map_success_to_result(get_subscription_id)` returns a
  `ResultWrapper[FailureDescription, int]` instance.
- `ResultWrapper.map_success(get_subscription_fee)` returns a
  `ResultWrapper[FailureDescription, float]` instance.

## Combining `tuple`-returning functions

The module `trcks.oop` also defines wrapper classes
for combining `tuple`-returning functions
with other `tuple`-returning functions and
with "regular" functions:

```pycon
>>> from trcks.oop import Wrapper
>>>
>>> def get_user_ids(domain: str) -> tuple[int, ...]:
...     if domain == "domain.org":
...         return (1,)
...     if domain == "provider.com":
...         return (2, 3)
...     return ()
>>>
>>> def get_subscription_ids(user_id: int) -> tuple[int, ...]:
...     if user_id == 1:
...         return (42,)
...     if user_id == 2:
...         return (44,)
...     if user_id == 3:
...         return (45,)
...     return ()
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fees_by_domain(domain: str) -> tuple[float, ...]:
...     return (
...         Wrapper(core=domain)
...         .map_to_iterable(get_user_ids)
...         .map_to_iterable(get_subscription_ids)
...         .map(get_subscription_fee)
...         .core
...     )
>>>
>>> get_subscription_fees_by_domain("domain.org")
(4.2,)
>>> get_subscription_fees_by_domain("provider.com")
(4.4, 4.5)
>>> get_subscription_fees_by_domain("example.net")
()

```

Each `map*` method in this example returns a new, immutable wrapper instance:

- `Wrapper.map_to_iterable(get_user_ids)` returns a
  `TupleWrapper[int]` instance.
- `TupleWrapper.map_to_iterable(get_subscription_ids)` returns a
  `TupleWrapper[int]` instance.
- `TupleWrapper.map(get_subscription_fee)` returns a
  `TupleWrapper[float]` instance.

## Combining `collections.abc.Awaitable`-returning functions

The module `trcks.oop` also defines wrapper classes
for combining `collections.abc.Awaitable`-returning functions
with other `collections.abc.Awaitable`-returning functions and
with "regular" functions:

```pycon
>>> import asyncio
>>> from trcks.oop import Wrapper
>>>
>>> async def get_user_id(user_email: str) -> int:
...     await asyncio.sleep(0.001)  # simulating a database query
...     if user_email == "erika.mustermann@domain.org":
...         return 1
...     if user_email == "john_doe@provider.com":
...         return 2
...     return 3
>>>
>>> async def get_subscription_id(user_id: int) -> int:
...     await asyncio.sleep(0.001)  # simulating another database query
...     if user_id == 1:
...         return 42
...     if user_id == 2:
...         return 44
...     return 45
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> async def get_subscription_fee_by_email(user_email: str) -> float:
...     return await (
...         Wrapper(core=user_email)
...         .map_to_awaitable(get_user_id)
...         .map_to_awaitable(get_subscription_id)
...         .map(get_subscription_fee)
...         .core
...     )
>>>
>>> asyncio.run(get_subscription_fee_by_email("erika.mustermann@domain.org"))
4.2
>>> asyncio.run(get_subscription_fee_by_email("john_doe@provider.com"))
4.4
>>> asyncio.run(get_subscription_fee_by_email("jane_doe@provider.com"))
4.5

```

Each `map*` method in this example returns a new, immutable wrapper instance:

- `Wrapper.map_to_awaitable(get_user_id)` returns an
  `AwaitableWrapper[int]` instance.
- `AwaitableWrapper.map_to_awaitable(get_subscription_id)` returns an
  `AwaitableWrapper[int]` instance.
- `AwaitableWrapper.map(get_subscription_fee)` returns an
  `AwaitableWrapper[float]` instance.

## Combining functions that return combination types

The module `trcks.oop` also defines wrapper classes
for combining functions that return combination types.
Combination types combine two or three of
`trcks.Result`, `tuple`, and `collections.abc.Awaitable`.
Each combination type has its own wrapper class:

- `trcks.oop.AwaitableResultTupleWrapper` for
  `trcks.AwaitableResultTuple` values
- `trcks.oop.AwaitableResultWrapper` for `trcks.AwaitableResult` values
- `trcks.oop.AwaitableTupleWrapper` for `trcks.AwaitableTuple` values
- `trcks.oop.ResultTupleWrapper` for `trcks.ResultTuple` values

When the given function returns a richer type than the wrapped value,
call a `map_to_*` method on the wrapper class that matches the wrapped value.
A `map_to_*` method is named after the return type of the given function.
Classes for types that combine `trcks.Result` and `tuple` use
the plural `map_successes*` and `tap_successes*` methods.
They operate on each success element individually
and short-circuit on the first `trcks.Failure`.
The example below starts with a domain string.
The function `get_user_ids` maps it to a `tuple` of user IDs.
The class method `AwaitableTupleWrapper.construct_from_iterable` wraps
the user IDs in an `AwaitableTupleWrapper` instance.
The method `AwaitableTupleWrapper.map_to_result` returns an
`AwaitableResultTupleWrapper` instance
because `get_subscription_id` returns a `trcks.Result` value:

```pycon
>>> import asyncio
>>> from typing import Literal
>>> from trcks import Result, ResultTuple
>>> from trcks.oop import AwaitableTupleWrapper
>>>
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>>
>>> def get_user_ids(domain: str) -> tuple[int, ...]:
...     if domain == "domain.org":
...         return (1,)
...     if domain == "provider.com":
...         return (2, 3)
...     return ()
>>>
>>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> async def get_subscription_fees_by_domain(
...     domain: str,
... ) -> ResultTuple[UserDoesNotHaveASubscription, float]:
...     return await (
...         AwaitableTupleWrapper.construct_from_iterable(get_user_ids(domain))
...         .map_to_result(get_subscription_id)
...         .map_successes(get_subscription_fee)
...         .core
...     )
>>>
>>> asyncio.run(get_subscription_fees_by_domain("domain.org"))
('success', (4.2,))
>>> asyncio.run(get_subscription_fees_by_domain("provider.com"))
('failure', 'User does not have a subscription')
>>> asyncio.run(get_subscription_fees_by_domain("example.net"))
('success', ())

```

Each `map*` method in this example returns a new, immutable wrapper instance:

- `AwaitableTupleWrapper.map_to_result(get_subscription_id)` returns an
  `AwaitableResultTupleWrapper[UserDoesNotHaveASubscription, int]` instance.
- `AwaitableResultTupleWrapper.map_successes(get_subscription_fee)` returns an
  `AwaitableResultTupleWrapper[UserDoesNotHaveASubscription, float]` instance.
