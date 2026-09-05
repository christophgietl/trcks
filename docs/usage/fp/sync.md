# Synchronous code with [trcks.fp][]

???+ tip "See also"
    The [object-oriented sync page](../oop/sync.md)
    covers the same operations using method chaining.

## Single-track code with [trcks.fp.composition][]

The function [trcks.fp.composition.pipe][] allows us to chain functions:

???+ example

    ```pycon
    >>> from trcks.fp.composition import pipe
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return pipe((s, len, lambda n: f"Length: {n}"))
    >>>
    >>> to_length_string("Hello, world!")
    'Length: 13'

    ```

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> pipe(("Hello, world!",))
    'Hello, world!'
    >>> pipe(("Hello, world!", len))
    13
    >>> pipe(("Hello, world!", len, lambda n: f"Length: {n}"))
    'Length: 13'

    ```

???+ note
    The function [trcks.fp.composition.pipe][] expects a [trcks.fp.composition.Pipeline][],
    i.e. a tuple consisting of a start value followed by up to seven
    compatible functions.

Side effects like logging or writing to a file tend to
"consume" their input and return [None][] instead.
To avoid this, we can use the higher-order function [trcks.fp.monads.identity.tap][].
This higher-order function turns each function into a function
that behaves like the original function but returns the input value.

???+ example

    ```pycon
    >>> from trcks.fp.monads import identity as i
    >>>
    >>> def to_length_string(s: str) -> str:
    ...     return pipe(
    ...         (
    ...             s,
    ...             i.tap(lambda o: print(f"LOG: Received '{o}'.")),
    ...             len,
    ...             lambda n: f"Length: {n}",
    ...             i.tap(lambda o: print(f"LOG: Returning '{o}'.")),
    ...         ),
    ...     )
    >>>
    >>> output = to_length_string("Hello, world!")
    LOG: Received 'Hello, world!'.
    LOG: Returning 'Length: 13'.
    >>> output
    'Length: 13'

    ```

## Double-track code with [trcks.fp.monads.result][]

If one of the functions in a [trcks.fp.composition.Pipeline][]
returns a `trcks.Result[F, S]` type,
the following function must accept this `trcks.Result[F, S]` type as its input.
However, functions with input type `trcks.Result[F, S]` tend to violate
the "do one thing and do it well" principle.
Therefore, the module [trcks.fp.monads.result][] provides
some higher-order functions named `map*`
that turn functions with input type `F` and functions with input type `S`
into functions with input type `trcks.Result[F, S]`.

???+ example

    ```pycon
    >>> from typing import Literal
    >>> from trcks import Result
    >>> from trcks.fp.composition import Pipeline3
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

To understand what is going on here,
let us have a look at the individual steps of the chain:

??? example "Step by step"

    ```pycon
    >>> from trcks.fp.composition import Pipeline0, Pipeline1, Pipeline2
    >>>
    >>> p0: Pipeline0[str] = ("erika.mustermann@domain.org",)
    >>> pipe(p0)
    'erika.mustermann@domain.org'
    >>>
    >>> p1: Pipeline1[str, Result[UserDoesNotExist, int]] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ... )
    >>> pipe(p1)
    ('success', 1)
    >>>
    >>> p2: Pipeline2[str, Result[UserDoesNotExist, int], Result[FailureDescription, int]] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ...     r.map_success_to_result(get_subscription_id),
    ... )
    >>> pipe(p2)
    ('success', 42)
    >>>
    >>> p3: Pipeline3[
    ...     str,
    ...     Result[UserDoesNotExist, int],
    ...     Result[FailureDescription, int],
    ...     Result[FailureDescription, float],
    ... ] = (
    ...     "erika.mustermann@domain.org",
    ...     get_user_id,
    ...     r.map_success_to_result(get_subscription_id),
    ...     r.map_success(get_subscription_fee),
    ... )
    >>> pipe(p3)
    ('success', 4.2)

    ```

While [trcks.fp.monads.result.map_failure][] and [trcks.fp.monads.result.map_success][]
allow us to apply functions in the failure case or in the success case, respectively,
the higher-order functions [trcks.fp.monads.result.tap_failure][] and [trcks.fp.monads.result.tap_success][]
allow us to execute side effects in the failure case or in the success case, respectively.

???+ example

    ```pycon
    >>> from trcks.fp.composition import Pipeline6
    >>>
    >>> def get_subscription_fee_by_email(user_email: str) -> Result[FailureDescription, float]:
    ...     pipeline: Pipeline6[
    ...         str,
    ...         Result[UserDoesNotExist, int],
    ...         Result[UserDoesNotExist, int],
    ...         Result[FailureDescription, int],
    ...         Result[FailureDescription, float],
    ...         Result[FailureDescription, float],
    ...         Result[FailureDescription, float],
    ...     ] = (
    ...         user_email,
    ...         get_user_id,
    ...         r.tap_success(lambda n: print(f"LOG: User ID: {n}.")),
    ...         r.map_success_to_result(get_subscription_id),
    ...         r.map_success(get_subscription_fee),
    ...         r.tap_success(lambda x: print(f"LOG: Subscription fee: {x}.")),
    ...         r.tap_failure(lambda fd: print(f"LOG: Failure description: {fd}.")),
    ...     )
    ...     return pipe(pipeline)
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
The higher-order function [trcks.fp.monads.result.tap_success_to_result][]
allows us to execute such side effects in the success case.
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
    ...     pipeline: Pipeline2[
    ...         str,
    ...         Result[UserDoesNotExist, int],
    ...         Result[UserDoesNotExist | OutOfDiskSpace, int],
    ...     ] = (
    ...         user_email,
    ...         get_user_id,
    ...         r.tap_success_to_result(write_to_disk),
    ...     )
    ...     return pipe(pipeline)
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
