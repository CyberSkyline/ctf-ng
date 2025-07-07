# Copyright 2025 Cyber Skyline

# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
# IN THE SOFTWARE.
from cyber_skyline.chall_parser.compose.challenge_info import ChallengeInfo, Hint, Question, TextBody, Variable
from cyber_skyline.chall_parser.rewriter import Template

class TestQuestion:
    def test_basic_question(self):
        """Test creating a basic question."""
        question = Question(
            name="flag",
            body="What is the flag?",
            points=100,
            answer="CTF{test}",
            max_attempts=5
        )
        assert question.name == "flag"
        assert question.points == 100
        assert question.max_attempts == 5

class TestHint:
    def test_text_hint(self):
        """Test creating a text hint."""
        text_hint = TextBody(type="text", content="This is a hint")
        hint = Hint(
            body=text_hint,
            preview="Hint preview",
            deduction=10
        )
        assert isinstance(hint.body, TextBody)
        assert hint.body.content == "This is a hint"
        assert hint.deduction == 10

    def test_string_hint(self):
        """Test creating a simple string hint."""
        hint = Hint(
            body="Simple hint text",
            preview="Simple hint",
            deduction=5
        )
        assert isinstance(hint.body, str)
        assert hint.body == "Simple hint text"

class TestVariable:
    def test_variable_with_template(self):
        """Test creating a variable with template."""
        template = Template("fake.word()", "test_var")
        variable = Variable(
            template=template,
            default="default_value"
        )
        assert variable.template == template
        assert variable.default == "default_value"

class TestChallengeInfo:
    def test_minimal_challenge_info(self):
        """Test creating minimal challenge info."""
        challenge = ChallengeInfo(
            name="Test Challenge",
            description="A test challenge",
            questions=[]
        )
        assert challenge.name == "Test Challenge"
        assert challenge.description == "A test challenge"
        assert len(challenge.questions) == 0

    def test_challenge_info_with_all_optional_fields(self):
        """Test ChallengeInfo with all optional fields populated."""
        question = Question(
            name="comprehensive_test",
            body="Test question?",
            points=50,
            answer="test_answer",
            max_attempts=10
        )
        
        hint = Hint(
            body=TextBody(type="text", content="Test hint content"),
            preview="Test preview",
            deduction=5
        )
        
        variable = Variable(
            template=Template("fake.word()", "test_var"),
            default="default_value"
        )
        
        challenge = ChallengeInfo(
            name="Comprehensive Test",
            description="Testing all fields", 
            questions=[question],
            icon="TbTest",
            hints=[hint],
            summary="Test summary",
            templates={"test_template": "fake.name()"},
            variables={"test_var": variable},
            tags=["test", "comprehensive"]
        )
        
        assert challenge.icon == "TbTest"
        assert challenge.summary == "Test summary"
        assert challenge.templates is not None
        assert "test_template" in challenge.templates
        assert challenge.variables is not None
        assert "test_var" in challenge.variables
        assert challenge.tags is not None
        assert "test" in challenge.tags

    def test_challenge_info_edge_cases(self):
        """Test ChallengeInfo with edge cases."""
        # Empty lists
        challenge = ChallengeInfo(
            name="Edge Case Test",
            description="Testing edge cases",
            questions=[],
            hints=[],
            tags=[]
        )
        
        assert len(challenge.questions) == 0
        assert challenge.hints is not None
        assert len(challenge.hints) == 0
        assert challenge.tags is not None
        assert len(challenge.tags) == 0