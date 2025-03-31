# trcks

`trcks` is a Python library.
It allows
[railway-oriented programming](https://fsharpforfunandprofit.com/rop/)
in two different programming styles:

1. an *object-oriented style* based on method chaining and
2. a *functional style* based on function composition.

## Motivation

The following subsections motivate railway-oriented programming in general
and the `trcks` library in particular.

### Why should I use railway-oriented programming?

When writing modular Python code, return type annotations are extremely helpful.
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
Moreover, it is difficult to document all (domain) exceptions in the docstring and
to keep this documentation up-to-date.


### How can I use railway-oriented programming?

Instead of raising exceptions (and documenting this behavior in the docstring),
we can return a generic `Result` type.
This return type

1. describes the success case *and* the failure case and
2. is verified by static type checkers.

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

### What do I need for railway-oriented programming?

Combining `Result`-returning functions
with other `Result`-returning functions or with "regular" functions
can be cumbersome and lead to repetitive code patterns:

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
...     return "success", get_subscription_fee(subscription_id)
...
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

Therefore, we need a library that helps us with combining functions.

### How does the module `trcks.oop` help with function combination?

The module `trcks.oop` supports combining functions in an object-oriented style
using method chaining:

```pycon
>>> from trcks.oop import Wrapper
>>>
>>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
...     return (
...         Wrapper(user_email)
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
