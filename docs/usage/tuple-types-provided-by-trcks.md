# Tuple types provided by [trcks][]

The generic type [trcks.Failure][][F] describes all [tuple][]s of length 2
with the string "failure" as the first element and a second element of type F.
Usually, the second element is a string, an exception or an enum value:

```pycon
>>> import enum
>>> from typing import Literal
>>> from trcks import Failure
>>>
>>> UserDoesNotExistLiteral = Literal["User does not exist"]
>>> literal_failure: Failure[UserDoesNotExistLiteral] = (
...     "failure", "User does not exist"
... )
>>>
>>> class UserDoesNotExistException(Exception):
...     pass
...
>>> exception_failure: Failure[UserDoesNotExistException] = ("failure", UserDoesNotExistException())
>>>
>>> class ErrorEnum(enum.Enum):
...     USER_DOES_NOT_EXIST = enum.auto
...
>>> enum_failure: Failure[ErrorEnum] = ("failure", ErrorEnum.USER_DOES_NOT_EXIST)

```

The generic type [trcks.Success][][S] describes all [tuple][]s of length 2
with the string "success" as the first element and a second element of type S.
Here, S can be any type.

```pycon
>>> from decimal import Decimal
>>> from pathlib import Path
>>> from trcks import Success
>>>
>>> decimal_success: Success[Decimal] = ("success", Decimal("3.14"))
>>> float_list_success: Success[list[float]] = ("success", [1.0, 2.0, 3.0])
>>> int_success: Success[int] = ("success", 42)
>>> path_success: Success[Path] = ("success", Path("/tmp/my-file.txt"))
>>> str_success: Success[str] = ("success", "foo")

```

The generic type [trcks.Result][][F, S] is
the union of [trcks.Failure][][F] and [trcks.Success][][S].
It is primarily used as a return type for functions:

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
