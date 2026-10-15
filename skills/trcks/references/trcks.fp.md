# Higher-order functions provided by `trcks.fp`

## Combining "regular" functions

The subpackage `trcks.fp` defines higher-order functions
for combining "regular" functions with other "regular" functions.
The identity monad does not wrap values.
Therefore, you can pass "regular" functions directly to `pipe`:

```pycon
>>> from trcks.fp.composition import pipe
>>>
>>> def get_length_string(s: str) -> str:
...     return pipe(s, len, lambda n: f"Length: {n}")
>>>
>>> get_length_string("Hello, world!")
'Length: 13'

```

Side effects like logging tend to "consume" their input
and return `None` instead.
The identity monad provides the higher-order function `tap`.
It turns such a side effect into a function that returns its input:

```pycon
>>> from trcks.fp.composition import pipe
>>> from trcks.fp.monads import identity as i
>>>
>>> def get_length_string(s: str) -> str:
...     return pipe(
...         s,
...         i.tap(lambda o: print(f"LOG: Received '{o}'.")),
...         len,
...         lambda n: f"Length: {n}",
...     )
>>>
>>> output = get_length_string("Hello, world!")
LOG: Received 'Hello, world!'.
>>> output
'Length: 13'

```

The `tap` function in the second example returns a function
with the following input and return types:

- `i.tap(...)` returns a function with
  input type `str` and return type `str`.
  It applies the given side effect and returns its input unchanged.

## Combining `trcks.Result`-returning functions

The subpackage `trcks.fp` also defines higher-order functions
for combining `trcks.Result`-returning functions
with other `trcks.Result`-returning functions and
with "regular" functions:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>> from trcks.fp.composition import Pipeline3, pipe
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
...     # Gathering all arguments for `pipe` in a type-annotated variable
...     # might help your static type checker understand
...     # that your `pipe` call is valid:
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
...     return pipe(*pipeline)
>>>
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

The `map*` functions in this example return functions
with the following input and return types:

- `r.map_success_to_result(get_subscription_id)` returns a function with
  input type `Result[UserDoesNotExist, int]` and
  return type `Result[FailureDescription, int]`.
- `r.map_success(get_subscription_fee)` returns a function with
  input type `Result[FailureDescription, int]` and
  return type `Result[FailureDescription, float]`.

## Combining `tuple`-returning functions

The subpackage `trcks.fp` also defines higher-order functions
for combining `tuple`-returning functions
with other `tuple`-returning functions and
with "regular" functions:

```pycon
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import tuple_ as t
>>>
>>> def get_user_ids(domain: str) -> tuple[int, ...]:
...     if domain == "domain.org":
...         return (1, 2)
...     if domain == "provider.com":
...         return (2,)
...     return ()
>>>
>>> def get_subscription_ids(user_id: int) -> tuple[int, ...]:
...     if user_id == 1:
...         return (42, 43)
...     if user_id == 2:
...         return (44,)
...     return ()
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fees_by_domain(domain: str) -> tuple[float, ...]:
...     # Gathering all arguments for `pipe` in a type-annotated variable
...     # might help your static type checker understand
...     # that your `pipe` call is valid:
...     pipeline: Pipeline3[
...         str,
...         tuple[int, ...],
...         tuple[int, ...],
...         tuple[float, ...],
...     ] = (
...         domain,
...         get_user_ids,
...         t.map_to_iterable(get_subscription_ids),
...         t.map_(get_subscription_fee),
...     )
...     return pipe(*pipeline)
>>>
>>> get_subscription_fees_by_domain("domain.org")
(4.2, 4.3, 4.4)
>>> get_subscription_fees_by_domain("provider.com")
(4.4,)
>>> get_subscription_fees_by_domain("example.net")
()

```

The `map*` functions in this example return functions
with the following input and return types:

- `t.map_to_iterable(get_subscription_ids)` returns a function with
  input type `tuple[int, ...]` and return type `tuple[int, ...]`.
- `t.map_(get_subscription_fee)` returns a function with
  input type `tuple[int, ...]` and return type `tuple[float, ...]`.

## Combining `collections.abc.Awaitable`-returning functions

The subpackage `trcks.fp` also defines higher-order functions
for combining `collections.abc.Awaitable`-returning functions
with other `collections.abc.Awaitable`-returning functions and
with "regular" functions:

```pycon
>>> import asyncio
>>> from collections.abc import Awaitable
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import awaitable as a
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
...     # Gathering all arguments for `pipe` in a type-annotated variable
...     # might help your static type checker understand
...     # that your `pipe` call is valid:
...     pipeline: Pipeline3[
...         str,
...         Awaitable[int],
...         Awaitable[int],
...         Awaitable[float],
...     ] = (
...         user_email,
...         get_user_id,
...         a.map_to_awaitable(get_subscription_id),
...         a.map_(get_subscription_fee),
...     )
...     return await pipe(*pipeline)
>>>
>>> asyncio.run(get_subscription_fee_by_email("erika.mustermann@domain.org"))
4.2
>>> asyncio.run(get_subscription_fee_by_email("john_doe@provider.com"))
4.4
>>> asyncio.run(get_subscription_fee_by_email("jane_doe@provider.com"))
4.5

```

The `map*` functions in this example return functions
with the following input and return types:

- `a.map_to_awaitable(get_subscription_id)` returns a function with
  input type `Awaitable[int]` and return type `Awaitable[int]`.
- `a.map_(get_subscription_fee)` returns a function with
  input type `Awaitable[int]` and return type `Awaitable[float]`.
