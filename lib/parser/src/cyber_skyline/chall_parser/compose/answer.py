from attrs import define

@define
class AnswerTestCase:
    """Represents a test case for validating an answer.
    
    Each test case can be used to check if the answer is correct.
    """
    answer: str
    """The expected answer text for this test case."""
    correct: bool
    """Indicates if this test case is a correct answer.
    If True, the answer is expected to match this test case.
    If False, the answer should not match this test case.
    """


@define
class Answer:
    body: str  # The regex pattern
    test_cases: list[AnswerTestCase] | None = None  # Optional test cases for validating the answer