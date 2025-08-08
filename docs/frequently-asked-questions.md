# Frequently asked questions (FAQs)

This section answers some questions that might come to your mind.

## Where can I learn more about railway-oriented programming?

Scott Wlaschin's blog post
[Railway oriented programming](https://fsharpforfunandprofit.com/posts/recipe-part2/)
comes with lots of examples and illustrations as well as
videos and slides from his talks.

## Should I replace all raised exceptions with [trcks.Result][]?

No, you should not.
Scott Wlaschin's blog post
[Against Railway-Oriented Programming](https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/)
lists eight scenarios
where raising or not catching an exception is the better choice.

## Which static type checkers does `trcks` support?

`trcks` is compatible with current versions of `mypy` and `pyright`.
Other type checkers may work as well.

## Which alternatives to `trcks` are there?

[returns](https://pypi.org/project/returns/) supports
object-oriented style and functional style (like `trcks`).
It provides
a `Result` container (and multiple other containers) for synchronous code and
a `Future` and a `FutureResult` container for asynchronous code.
Whereas the `Result` container is pretty similar to [trcks.Result][],
the `Future` container and the `FutureResult` container deviate
from [collections.abc.Awaitable][] and [trcks.AwaitableResult][].
Other major differences are:

- `returns` provides
  [do notation](https://returns.readthedocs.io/en/0.25.0/pages/do-notation.html)
  and
  [dependency injection](https://returns.readthedocs.io/en/0.25.0/pages/context.html).
- The authors of `returns`
  [recommend using `mypy`](https://returns.readthedocs.io/en/0.25.0/pages/quickstart.html#typechecking-and-other-integrations)
  along with
  [their suggested `mypy` configuration](https://returns.readthedocs.io/en/0.25.0/pages/contrib/mypy_plugins.html#configuration)
  and
  [their custom `mypy` plugin](https://returns.readthedocs.io/en/0.25.0/pages/contrib/mypy_plugins.html#mypy-plugin).

[Expression](https://pypi.org/project/Expression/) supports
object-oriented style ("fluent syntax") and
functional style (like `trcks`).
It provides a `Result` class (and multiple other container classes)
for synchronous code.
The `Result` class is pretty similar to [trcks.Result][] and [trcks.oop.ResultWrapper][].
An `AsyncResult` type based on [collections.abc.AsyncGenerator][]
[will be added in a future version](https://github.com/dbrattli/Expression/pull/247).

## Which libraries inspired `trcks`?

`trcks` is mostly inspired
by the Python libraries mentioned in the previous section and
by the TypeScript library [fp-ts](https://www.npmjs.com/package/fp-ts).
