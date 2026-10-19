# Higher-order functions provided by `trcks.fp`

## Combining "regular" functions

The subpackage `trcks.fp` defines higher-order functions
for combining "regular" functions with other "regular" functions.
The identity monad does not wrap values.
Therefore, you can pass "regular" functions directly to `pipe`:

```pycon
>>> from trcks.fp.composition import pipe
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
...     return pipe(user_email, get_user_id, get_subscription_id, get_subscription_fee)
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
The identity monad provides the higher-order function `tap`.
It turns such a side effect into a function that returns its input:

```pycon
>>> from trcks.fp.composition import pipe
>>> from trcks.fp.monads import identity as i
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
...     return pipe(
...         user_email,
...         i.tap(lambda o: print(f"LOG: Received '{o}'.")),
...         get_user_id,
...         get_subscription_id,
...         get_subscription_fee,
...     )
>>>
>>> output = get_subscription_fee_by_email("erika.mustermann@domain.org")
LOG: Received 'erika.mustermann@domain.org'.
>>> output
4.2

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
(4.2,)
>>> get_subscription_fees_by_domain("provider.com")
(4.4, 4.5)
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

## Combining functions that return combination types

The subpackage `trcks.fp` also defines higher-order functions
for combining functions that return combination types.
Combination types combine two or three of
`trcks.Result`, `tuple`, and `collections.abc.Awaitable`.
Each combination type has its own module in `trcks.fp.monads`:

- `awaitable_result` (imported as `ar`) for `trcks.AwaitableResult` values
- `awaitable_result_tuple` (imported as `art`) for
  `trcks.AwaitableResultTuple` values
- `awaitable_tuple` (imported as `at`) for `trcks.AwaitableTuple` values
- `result_tuple` (imported as `rt`) for `trcks.ResultTuple` values

When a step returns a richer type than the pipeline value,
use a `map_to_*` function from the module that matches the pipeline value.
A `map_to_*` function is named after the return type of the given function.
Modules for types that combine `trcks.Result` and `tuple` use
the plural `map_successes*` and `tap_successes*` functions.
They operate on each success element individually
and short-circuit on the first `trcks.Failure`.
The example below starts with a `tuple` of email addresses.
It enters the `trcks.AwaitableTuple` type with `at.construct_from_iterable`
and widens to the `trcks.AwaitableResultTuple` type
because `get_user_id` returns a `trcks.AwaitableResult` value:

```pycon
>>> import asyncio
>>> from typing import Literal
>>> from trcks import AwaitableResultTuple, AwaitableTuple, Result, ResultTuple
>>> from trcks.fp.composition import Pipeline4, pipe
>>> from trcks.fp.monads import awaitable_result_tuple as art
>>> from trcks.fp.monads import awaitable_tuple as at
>>>
>>> UserDoesNotExist = Literal["User does not exist"]
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>> FailureDescription = UserDoesNotExist | UserDoesNotHaveASubscription
>>>
>>> async def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
...     await asyncio.sleep(0.001)  # simulating a database query
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
>>> async def get_subscription_fees_by_email(
...     user_emails: tuple[str, ...],
... ) -> ResultTuple[FailureDescription, float]:
...     # Gathering all arguments for `pipe` in a type-annotated variable
...     # might help your static type checker understand
...     # that your `pipe` call is valid:
...     pipeline: Pipeline4[
...         tuple[str, ...],
...         AwaitableTuple[str],
...         AwaitableResultTuple[UserDoesNotExist, int],
...         AwaitableResultTuple[FailureDescription, int],
...         AwaitableResultTuple[FailureDescription, float],
...     ] = (
...         user_emails,
...         at.construct_from_iterable,
...         at.map_to_awaitable_result(get_user_id),
...         art.map_successes_to_result(get_subscription_id),
...         art.map_successes(get_subscription_fee),
...     )
...     return await pipe(*pipeline)
>>>
>>> asyncio.run(get_subscription_fees_by_email(("erika.mustermann@domain.org",)))
('success', (4.2,))
>>> asyncio.run(
...     get_subscription_fees_by_email(
...         ("john_doe@provider.com", "erika.mustermann@domain.org")
...     )
... )
('failure', 'User does not have a subscription')
>>> asyncio.run(get_subscription_fees_by_email(("jane_doe@provider.com",)))
('failure', 'User does not exist')

```

The `map*` functions in this example return functions
with the following input and return types:

- `at.map_to_awaitable_result(get_user_id)` returns a function with
  input type `AwaitableTuple[str]` and
  return type `AwaitableResultTuple[UserDoesNotExist, int]`.
- `art.map_successes_to_result(get_subscription_id)` returns a function with
  input type `AwaitableResultTuple[UserDoesNotExist, int]` and
  return type `AwaitableResultTuple[FailureDescription, int]`.
- `art.map_successes(get_subscription_fee)` returns a function with
  input type `AwaitableResultTuple[FailureDescription, int]` and
  return type `AwaitableResultTuple[FailureDescription, float]`.
