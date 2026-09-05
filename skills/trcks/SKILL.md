---
name: trcks
description: >-
  Type-safe railway-oriented programming (ROP) with the Python library `trcks`.
  Use when writing, reviewing, or debugging Python code
  that returns domain errors instead of raising them.
  This includes code using
  the generic types `trcks.Failure`, `trcks.Success`, and `trcks.Result`;
  the OOP-style wrapper classes with `map*` methods from `trcks.oop`; or
  the FP-style pipelines (`pipe`) and monads with `map*` functions from `trcks.fp`.
  Also use when narrowing or pattern-matching `trcks.Result` values,
  when converting exception-raising or `None`-returning code
  into `trcks.Result` values, or
  when unwrapping `trcks.Result` values to raise exceptions again.
---

# Railway-oriented programming with `trcks`

The Python library `trcks` lets functions return domain errors
instead of raising them.
Its generic type `trcks.Result` exposes each domain error in the function signature,
so the failure type is visible and downstream uses can be type-checked.
`trcks` supports two distinct but equivalent styles:
method chaining with the wrapper classes from `trcks.oop`, and
function composition with the pipelines and monads from `trcks.fp`.

The sections below provide a reference for the public API,
how-tos for recurring tasks, and best practices.

## Reference: Generic types provided by `trcks`

The module `trcks` defines the covariant generic types
`Failure`, `Success`, and `Result`:

```pycon
>>> from trcks import Failure, Result, Success
>>> Failure
tuple[typing.Literal['failure'], +_F_co]
>>> Success
tuple[typing.Literal['success'], +_S_co]
>>> Result
tuple[typing.Literal['failure'], +_F_co] | tuple[typing.Literal['success'], +_S_co]

```

Wrap `Success` and `Result` around `collections.abc.Iterable` and `tuple`:

```pycon
>>> from trcks import (
...     ResultIterable,
...     ResultTuple,
...     SuccessIterable,
...     SuccessTuple,
... )
>>> SuccessIterable
tuple[typing.Literal['success'], collections.abc.Iterable[+_S_co]]
>>> ResultTuple
tuple[typing.Literal['failure'], +_F_co] | tuple[typing.Literal['success'], tuple[+_S_co, ...]]

```

Wrap `collections.abc.Awaitable` around the above types:

```pycon
>>> from trcks import (
...     AwaitableFailure,
...     AwaitableIterable,
...     AwaitableResult,
...     AwaitableResultIterable,
...     AwaitableResultTuple,
...     AwaitableSuccess,
...     AwaitableSuccessIterable,
...     AwaitableSuccessTuple,
...     AwaitableTuple,
... )
>>> AwaitableResult
collections.abc.Awaitable[tuple[typing.Literal['failure'], +_F_co] | tuple[typing.Literal['success'], +_S_co]]
>>> AwaitableTuple
collections.abc.Awaitable[tuple[+_T_co, ...]]
>>> AwaitableResultTuple
collections.abc.Awaitable[tuple[typing.Literal['failure'], +_F_co] | tuple[typing.Literal['success'], tuple[+_S_co, ...]]]

```

## Reference: Higher-order functions provided by `trcks.fp`

The subpackage `trcks.fp` defines higher-order functions
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
>>>
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

Read [the `trcks.fp` reference guide](references/trcks.fp.md) for details
about the modules and their functions.

## Reference: Wrapper classes provided by `trcks.oop`

The module `trcks.oop` defines wrapper classes
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

Read [the `trcks.oop` reference guide](references/trcks.oop.md) for details
about the wrapper classes and their methods.

## How to: Narrow `trcks.Result` values to their success or failure types

Since `trcks.Result` is a discriminated union of two types,
you can narrow it to either type using a simple `if` statement:

```pycon
>>> from trcks import Result
>>> def handle_result_using_if_statement(result: Result[str, int]) -> None:
...     if result[0] == "failure":
...         message: str = result[1]
...         print(f"Failure: {message}")
...     else:
...         number: int = result[1]
...         print(f"Success: {number}")

```

Alternatively, you can use pattern matching:

```pycon
>>> import sys
>>> from trcks import Result
>>> if sys.version_info >= (3, 11):
...     from typing import assert_never, reveal_type
... else:
...     from typing_extensions import assert_never, reveal_type
>>> def handle_result_using_pattern_matching(result: Result[str, int]) -> None:
...     match result:
...         case ("failure", message):
...             reveal_type(message)  # Revealed type is 'str'
...             print(f"Error: {message}")
...         case ("success", number):
...             reveal_type(number)  # Revealed type is 'int'
...             print(f"Value: {number}")
...         # Depending on your type checker settings and your project preferences,
...         # you might have to omit or modify the following default case:
...         case _:
...             assert_never(result)

```

## How to: Call code that raises exceptions or returns `None` for domain errors

When calling code that raises exceptions for domain errors
(e.g. the Python standard library or a third-party library),
catch the specific domain-error exceptions that you expect,
convert them into `trcks.Failure` values, and
return them:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>> def divide(a: float, b: float) -> Result[Literal["Division by zero"], float]:
...     try:
...         return "success", a / b
...     except ZeroDivisionError:
...         return "failure", "Division by zero"
>>>
>>> divide(5.0, 2.0)
('success', 2.5)
>>> divide(3.5, 0.0)
('failure', 'Division by zero')

```

When calling code that returns `None` for domain errors,
check for `None`, convert it into a `trcks.Failure` value, and return it:

```pycon
>>> import re
>>> from typing import Literal
>>> from trcks import Result
>>> def extract_ticket_number(
...     ticket_id: str,
... ) -> Result[Literal["Invalid ticket ID"], str]:
...     match = re.fullmatch(r"TICKET-(\d+)", ticket_id)
...     if match is None:
...         return "failure", "Invalid ticket ID"
...     return "success", match.group(1)
>>>
>>> extract_ticket_number("TICKET-12345")
('success', '12345')
>>> extract_ticket_number("12345")
('failure', 'Invalid ticket ID')
>>> extract_ticket_number("TICKET-12345-URGENT")
('failure', 'Invalid ticket ID')

```

## How to: Raise exceptions for domain errors

If a framework boundary expects exceptions (e.g. a web framework's `HTTPException`),
narrow your `trcks.Result` value,
translate failures into the expected exceptions, and
raise them:

```pycon
>>> import sys
>>> from typing import Literal
>>> from trcks import Result
>>> if sys.version_info >= (3, 11):
...     from typing import assert_never
... else:
...     from typing_extensions import assert_never
>>> class DivisionByZeroError(Exception):
...     """Raised when division by zero is attempted."""
>>>
>>> def unwrap_divide_result(
...     result: Result[Literal["Division by zero"], float],
... ) -> float:
...     match result:
...         case ("failure", message):
...             raise DivisionByZeroError(message)
...         case ("success", value):
...             return value
...         case _:
...             assert_never(result)
>>>
>>> unwrap_divide_result(("success", 2.5))
2.5
>>> unwrap_divide_result(("failure", "Division by zero"))
Traceback (most recent call last):
    ...
DivisionByZeroError: Division by zero

```

## Best practices: Distinguishing domain errors, panics, and infrastructure errors

Domain errors are expected problems that are part of the business process
(e.g. "order rejected by billing" or "invalid product code").
Do *not* raise exceptions for domain errors.
Use `trcks.Result` to return them instead.

Panics are unexpected problems that the caller cannot meaningfully recover from,
potentially leaving the program in an unknown state
(e.g. a bug, an assertion error, or an out-of-memory condition).
Do *not* wrap panics in `trcks.Result`.
Let them propagate as exceptions instead.

Infrastructure errors are caused by the environment rather than the business process
(e.g. a network timeout or an identity-provider outage).
Treat an infrastructure error as a domain error (use `trcks.Result`)
only if the caller can meaningfully recover from it.
Otherwise, treat it as a panic (raise an exception).
Model only the infrastructure failures that matter to the domain,
and let the rest propagate as exceptions.
If in doubt, ask the user or a domain expert.

## Best practices: Using narrow failure types

Do *not* use broad types like `str` or `object` for failures.
Use narrow types instead.

You can use `Literal`s and unions of `Literal`s like in the examples above.

Or you can use enums:

```pycon
>>> import enum
>>> from typing import Literal
>>> from trcks import Result
>>>
>>> class FailureDescription(enum.Enum):
...     USER_DOES_NOT_EXIST = "User does not exist"
...     USER_DOES_NOT_HAVE_A_SUBSCRIPTION = "User does not have a subscription"
>>>
>>> def get_user_id(
...     user_email: str,
... ) -> Result[Literal[FailureDescription.USER_DOES_NOT_EXIST], int]:
...     if user_email == "erika.mustermann@domain.org":
...         return "success", 1
...     if user_email == "john_doe@provider.com":
...         return "success", 2
...     return "failure", FailureDescription.USER_DOES_NOT_EXIST
>>>
>>> def get_subscription_id(
...     user_id: int,
... ) -> Result[Literal[FailureDescription.USER_DOES_NOT_HAVE_A_SUBSCRIPTION], int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", FailureDescription.USER_DOES_NOT_HAVE_A_SUBSCRIPTION
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fee_by_email(
...     user_email: str,
... ) -> Result[FailureDescription, float]: ...

```

Or you can use data classes to include additional information in the failure value:

```pycon
>>> from dataclasses import dataclass
>>> from typing import final
>>> from trcks import Result
>>>
>>> @final
... @dataclass(frozen=True, slots=True)
... class UserDoesNotExistError:
...     email: str
>>>
>>> @final
... @dataclass(frozen=True, slots=True)
... class UserDoesNotHaveASubscriptionError:
...     id: int
>>>
>>> def get_user_id(user_email: str) -> Result[UserDoesNotExistError, int]:
...     if user_email == "erika.mustermann@domain.org":
...         return "success", 1
...     if user_email == "john_doe@provider.com":
...         return "success", 2
...     return "failure", UserDoesNotExistError(email=user_email)
>>>
>>> def get_subscription_id(user_id: int) -> Result[UserDoesNotHaveASubscriptionError, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", UserDoesNotHaveASubscriptionError(id=user_id)
>>>
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
>>>
>>> def get_subscription_fee_by_email(
...     user_email: str,
... ) -> Result[UserDoesNotExistError | UserDoesNotHaveASubscriptionError, float]: ...

```

## Best practices: Choosing a style and using a type checker

1. Choose either `trcks.fp` or `trcks.oop` for your project, and use it consistently.
2. Use a static type checker (e.g., `mypy`, `pyright`, or `pyrefly`)
   to verify that your code is type-safe.

## Further reading

1. [`trcks.fp` reference guide](references/trcks.fp.md)
2. [`trcks.oop` reference guide](references/trcks.oop.md)
