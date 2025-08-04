# [trcks][]

The following questions motivate the package [trcks][] in particular.

## What do I need for railway-oriented programming?

Combining result-returning functions
with other result-returning functions or with "regular" functions
can be cumbersome.
Moreover, it can lead to repetitive code patterns:

???+ example

    >>> from typing import Literal, Union
    >>> from trcks import Result
    >>>
    >>> UserDoesNotExist = Literal["User does not exist"]
    >>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
    >>> FailureDescription = Union[UserDoesNotExist, UserDoesNotHaveASubscription]
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

Therefore, we need a library that helps us combine functions.

## How does the module [trcks.oop][] help with function combination?

The module [trcks.oop][] supports combining functions in an object-oriented style
using method chaining:

???+ example

    >>> from trcks.oop import Wrapper
    >>>
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

## How does the package [trcks.fp][] help with function combination?

The package [trcks.fp][] supports combining functions in a functional style
using function composition:

???+ example

    >>> from trcks.fp.composition import Pipeline3, pipe
    >>> from trcks.fp.monads import result as r
    >>>
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
