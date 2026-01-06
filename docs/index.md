# Overview

`trcks` is a Python library that allows
[railway-oriented programming (ROP)](https://fsharpforfunandprofit.com/rop/)
in two different type-safe programming styles.

## Object-oriented style

The object-oriented style is based on method chaining,
as demonstrated by the `get_subscription_fee_by_email` function
in the following example.

???+ example

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

???+ note

    1. The generic type `trcks.Result` allows domain errors to become
       part of a function's return type (subject to static type checking).
    2. The class `trcks.oop.Wrapper` provides a convenient way to chain
       `trcks.Result`-returning functions and "regular" functions
       (in a type-safe way).

???+ tip

    For more examples regarding the usage of `trcks` and `trcks.oop.Wrapper`,
    please check the following repositories:

    1. [trcks-example-cyclopts](https://github.com/christophgietl/trcks-example-cyclopts)
       (CLI application)
    2. [trcks-example-fastapi](https://github.com/christophgietl/trcks-example-fastapi)
       (REST backend application)

## Functional style

The functional style is based on function composition,
as demonstrated by the `get_subscription_fee_by_email` function
in the following example.

???+ example

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

???+ note

    1. The generic type `trcks.Result` allows domain errors to become
       part of a function's return type (subject to static type checking).
    2. The modules `trcks.fp.composition` and `trcks.fp.monads.result`
       provide a convenient way to chain
       `trcks.Result`-returning functions and "regular" functions
       (in a type-safe way).
