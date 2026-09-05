# Synchronous code with [trcks.oop][]

???+ tip "See also"
    The [functional sync page](../fp/sync.md)
    covers the same operations using function composition.

## Single-track code with [trcks.oop.Wrapper][]

The generic class [trcks.oop.Wrapper][]`[T]` allows us to chain functions:

???+ example

    ```pycon
    >>> from trcks.oop import Wrapper
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return Wrapper(core=s).map(len).map(lambda n: f"Length: {n}").core
    >>>
    >>> to_length_string("Hello, world!")
    'Length: 13'

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="Hello, world!")
    >>> wrapped
    Wrapper(core='Hello, world!')
    >>> # 2. Apply the builtin function len:
    >>> mapped: Wrapper[int] = wrapped.map(len)
    >>> mapped
    Wrapper(core=13)
    >>> # 3. Apply a lambda function:
    >>> mapped_again: Wrapper[str] = mapped.map(lambda n: f"Length: {n}")
    >>> mapped_again
    Wrapper(core='Length: 13')
    >>> # 4. Unwrap the output string:
    >>> unwrapped: str = mapped_again.core
    >>> unwrapped
    'Length: 13'

    ```

???+ note
    Instead of the default constructor `trcks.oop.Wrapper(core="Hello, world!")`,
    we can also use the static method `trcks.oop.Wrapper.construct("Hello, world!")`.

By following the pattern of wrapping, mapping, and unwrapping,
we can write code that resembles a single-track railway
(or maybe a single-pipe pipeline).

Side effects like logging or writing to a file tend to
"consume" their input and return [None][] instead.
To avoid this, we can use the `tap` method available in
the [trcks.oop.Wrapper][] class.
This method allows executing side effects while preserving the original value:

???+ example

    ```pycon
    >>> def to_length_string(s: str) -> str:
    ...     return (
    ...         Wrapper(core=s)
    ...         .tap(lambda o: print(f"LOG: Received '{o}'."))
    ...         .map(len)
    ...         .map(lambda n: f"Length: {n}")
    ...         .tap(lambda o: print(f"LOG: Returning '{o}'."))
    ...         .core
    ...     )
    >>>
    >>> output = to_length_string("Hello, world!")
    LOG: Received 'Hello, world!'.
    LOG: Returning 'Length: 13'.
    >>> output
    'Length: 13'

    ```

## Double-track code with [trcks.oop.ResultWrapper][]

Whenever a function in a chain returns a [trcks.Result][]`[F, S]` type,
the next operation must handle the [trcks.Result][]`[F, S]` value.
However, methods that directly handle [trcks.Result][]`[F, S]` values tend to violate
the "do one thing and do it well" principle.
Therefore, the class [trcks.oop.ResultWrapper][]`[F, S]` provides
some methods named `map_failure*` and `map_success*`
that call functions with input type `F` and functions with input type `S`
on a wrapped [trcks.Result][]`[F, S]` value.

???+ example

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

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> from trcks.oop import ResultWrapper
    >>>
    >>> # 1. Wrap the input string:
    >>> wrapped: Wrapper[str] = Wrapper(core="erika.mustermann@domain.org")
    >>> wrapped
    Wrapper(core='erika.mustermann@domain.org')
    >>> # 2. Apply the Result function get_user_id:
    >>> mapped_once: ResultWrapper[UserDoesNotExist, int] = wrapped.map_to_result(get_user_id)
    >>> mapped_once
    ResultWrapper(core=('success', 1))
    >>> # 3. Apply the Result function get_subscription_id in the success case:
    >>> mapped_twice: ResultWrapper[FailureDescription, int] = (
    ...     mapped_once.map_success_to_result(get_subscription_id)
    ... )
    >>> mapped_twice
    ResultWrapper(core=('success', 42))
    >>> # 4. Apply the function get_subscription_fee in the success case:
    >>> mapped_thrice: ResultWrapper[FailureDescription, float] = mapped_twice.map_success(
    ...     get_subscription_fee
    ... )
    >>> mapped_thrice
    ResultWrapper(core=('success', 4.2))
    >>> # 5. Unwrap the output result:
    >>> unwrapped: Result[FailureDescription, float] = mapped_thrice.core
    >>> unwrapped
    ('success', 4.2)

    ```

???+ note
    The method [trcks.oop.Wrapper.map_to_result][] returns
    a [trcks.oop.ResultWrapper][] object.
    The corresponding class [trcks.oop.ResultWrapper][]
    has a `map_failure*` and a `map_success*` method
    for each `map*` method of the class [trcks.oop.Wrapper][].

The `tap_success` and `tap_failure` methods allow us to execute side effects
in the success case or in the failure case, respectively:

???+ example

    ```pycon
    >>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
    ...     return (
    ...         Wrapper(core=user_email)
    ...         .map_to_result(get_user_id)
    ...         .tap_success(lambda n: print(f"LOG: User ID: {n}."))
    ...         .map_success_to_result(get_subscription_id)
    ...         .map_success(get_subscription_fee)
    ...         .tap_success(lambda x: print(f"LOG: Subscription fee: {x}."))
    ...         .tap_failure(lambda fd: print(f"LOG: Failure description: {fd}."))
    ...         .core
    ...     )
    >>>
    >>> fee_erika = get_subscription_fee_by_email("erika.mustermann@domain.org")
    LOG: User ID: 1.
    LOG: Subscription fee: 4.2.
    >>> fee_erika
    ('success', 4.2)
    >>>
    >>> fee_john = get_subscription_fee_by_email("john_doe@provider.com")
    LOG: User ID: 2.
    LOG: Failure description: User does not have a subscription.
    >>> fee_john
    ('failure', 'User does not have a subscription')
    >>>
    >>> fee_jane = get_subscription_fee_by_email("jane_doe@provider.com")
    LOG: Failure description: User does not exist.
    >>> fee_jane
    ('failure', 'User does not exist')

    ```

Sometimes, side effects themselves can fail and
need to return a [trcks.Result][] type.
The `tap_success_to_result` method allows us to execute such side effects
in the success case.
If the side effect returns a [trcks.Failure][], that failure is propagated.
If the side effect returns a [trcks.Success][], the original success value is preserved.

???+ example

    ```pycon
    >>> OutOfDiskSpace = Literal["Out of disk space"]
    >>>
    >>> def write_to_disk(n: int) -> Result[OutOfDiskSpace, None]:
    ...     if n > 1:
    ...         return "failure", "Out of disk space"
    ...     return "success", print(f"LOG: Wrote {n} to disk.")
    >>>
    >>> def get_and_persist_user_id(
    ...     user_email: str,
    ... ) -> Result[UserDoesNotExist | OutOfDiskSpace, int]:
    ...     return (
    ...         Wrapper(core=user_email)
    ...         .map_to_result(get_user_id)
    ...         .tap_success_to_result(write_to_disk)
    ...         .core
    ...     )
    >>>
    >>> id_erika = get_and_persist_user_id("erika.mustermann@domain.org")
    LOG: Wrote 1 to disk.
    >>> id_erika
    ('success', 1)
    >>>
    >>> id_john = get_and_persist_user_id("john_doe@provider.com")
    >>> id_john
    ('failure', 'Out of disk space')
    >>>
    >>> id_jane = get_and_persist_user_id("jane_doe@provider.com")
    >>> id_jane
    ('failure', 'User does not exist')

    ```
