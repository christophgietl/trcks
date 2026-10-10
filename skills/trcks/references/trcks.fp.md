# Higher-order functions provided by `trcks.fp`

## Combining `trcks.Result`-returning functions

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
