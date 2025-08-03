# Railway-oriented programming

The following questions motivate railway-oriented programming in general.

## Why should I use railway-oriented programming?

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

We can document domain exceptions in the docstring of the function:

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
to document all domain exceptions in the docstring and
to keep this documentation up-to-date.
Therefore, we should use railway-oriented programming.

## How can I use railway-oriented programming?

Instead of raising exceptions (and documenting this behavior in the docstring),
we return a result type:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>>
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>>
>>> def get_subscription_id(
...     user_id: int
... ) -> Result[UserDoesNotHaveASubscription, int]:
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
