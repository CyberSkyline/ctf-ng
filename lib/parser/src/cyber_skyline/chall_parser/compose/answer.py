import attr
import attr.validators as v

@attr.s
class AnswerTestCase:
    """Represents a test case for validating an answer.
    
    Each test case can be used to check if the answer is correct.
    """
    answer: str = attr.ib(validator=v.instance_of(str))
    """The expected answer text for this test case."""
    correct: bool = attr.ib(validator=v.instance_of(bool))
    """Indicates if this test case is a correct answer.
    If True, the answer is expected to match this test case.
    If False, the answer should not match this test case.
    """


@attr.s
class Answer:
    body: str = attr.ib(validator=v.instance_of(str))  # The regex pattern
    test_cases: list[AnswerTestCase] | None = attr.ib(default=None, validator=v.optional(v.deep_iterable(v.instance_of(AnswerTestCase), v.instance_of(list))))  # Optional test cases for validating the answer

