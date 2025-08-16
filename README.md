# trcks 🚂🐍

`trcks` is a Python library that allows
[railway-oriented programming (ROP)](https://fsharpforfunandprofit.com/rop/)
in two different type-safe programming styles.

## Railway-oriented programming (ROP) styles

The following subsections demonstrate
both styles of railway-oriented programming (ROP)
supported by `trcks`.

### Object-oriented style

The object-oriented style is based on method chaining,
as demonstrated by the `get_subscription_fee_by_email` function
in the following example.

```pycon
>>> from typing import Literal, Union
>>> from trcks import Result
>>> from trcks.oop import Wrapper
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

#### Notes w.r.t. object-oriented style

1. The generic type `trcks.Result` allows domain errors to become
   part of a function's return type (subject to static type checking).
2. The class `trcks.oop.Wrapper` provides a convenient way to chain
   `trcks.Result`-returning functions and "regular" functions
   (in a type-safe way).

### Functional style

The functional style is based on function composition,
as demonstrated by the `get_subscription_fee_by_email` function
in the following example.

```pycon
>>> from typing import Literal, Union
>>> from trcks import Result
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import result as r
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

```

#### Notes w.r.t. functional style

1. The generic type `trcks.Result` allows domain errors to become
   part of a function's return type (subject to static type checking).
2. The modules `trcks.fp.composition` and `trcks.fp.monads.result`
   provide a convenient way to chain
   `trcks.Result`-returning functions and "regular" functions
   (in a type-safe way).

## Setup

`trcks` is [available on PyPI](https://pypi.org/project/trcks/).
Use your favorite package manager (e.g. `pip`, `poetry` or `uv`) to install it.
