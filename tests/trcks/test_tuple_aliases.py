from trcks import (
    AwaitableResultSequence,
    AwaitableResultTuple,
    AwaitableSequence,
    AwaitableSuccessSequence,
    AwaitableSuccessTuple,
    AwaitableTuple,
    ResultSequence,
    ResultTuple,
    SuccessSequence,
    SuccessTuple,
)
from trcks.fp.monads import awaitable_result_sequence as ars
from trcks.fp.monads import awaitable_sequence as as_
from trcks.fp.monads import result_sequence as rs
from trcks.fp.monads import sequence as s
from trcks.oop import (
    AwaitableResultSequenceWrapper,
    AwaitableResultTupleWrapper,
    AwaitableSequenceWrapper,
    AwaitableTupleWrapper,
    ResultSequenceWrapper,
    ResultTupleWrapper,
    SequenceWrapper,
    TupleWrapper,
)


def test_tuple_type_aliases_are_compatible() -> None:
    assert AwaitableTuple == AwaitableSequence
    assert ResultTuple == ResultSequence
    assert SuccessTuple == SuccessSequence
    assert AwaitableResultTuple == AwaitableResultSequence
    assert AwaitableSuccessTuple == AwaitableSuccessSequence


def test_tuple_function_aliases_are_available() -> None:
    assert as_.construct_from_tuple == as_.construct_from_sequence
    assert as_.map_to_tuple == as_.map_to_sequence
    assert as_.tap_to_tuple == as_.tap_to_sequence
    assert as_.to_coroutine_tuple == as_.to_coroutine_sequence
    assert s.map_to_tuple == s.map_to_sequence
    assert s.tap_to_tuple == s.tap_to_sequence
    assert rs.construct_successes_from_tuple == rs.construct_successes_from_sequence
    assert rs.map_failure_to_tuple == rs.map_failure_to_sequence
    assert rs.map_successes_to_tuple == rs.map_successes_to_sequence
    assert rs.tap_failure_to_tuple == rs.tap_failure_to_sequence
    assert rs.tap_successes_to_tuple == rs.tap_successes_to_sequence
    assert ars.construct_successes_from_tuple == ars.construct_successes_from_sequence
    assert ars.map_failure_to_tuple == ars.map_failure_to_sequence
    assert ars.map_successes_to_tuple == ars.map_successes_to_sequence
    assert ars.tap_failure_to_tuple == ars.tap_failure_to_sequence
    assert ars.tap_successes_to_tuple == ars.tap_successes_to_sequence


def test_tuple_wrapper_aliases_are_available() -> None:
    assert TupleWrapper is SequenceWrapper
    assert AwaitableTupleWrapper is AwaitableSequenceWrapper
    assert ResultTupleWrapper is ResultSequenceWrapper
    assert AwaitableResultTupleWrapper is AwaitableResultSequenceWrapper
