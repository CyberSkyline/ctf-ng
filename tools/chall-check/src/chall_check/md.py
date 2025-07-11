from cyber_skyline.chall_parser.compose.compose import ComposeFile
from cyber_skyline.chall_parser.compose.answer import Answer
from cyber_skyline.chall_parser.compose.challenge_info import TextBody
from cyber_skyline.chall_parser.rewriter import Template


# # CHALLENGE_NAME
# Put your challenge description here. This is the story and context, 
# and what players will see.

# ## Questions
# 1. Q1_NAME -- Put the question in here. -- Points
# 2. Q2_NAME -- Put the question in here. -- Points
# 3. Q3_NAME -- Put the question in here. --  Points

# ## Answers
# 1. A1: Put the answer for Q1 in here
# 2. A2: Put the answer for Q2 in here
# 3. A3: Put the answer for Q3 in here

# ## Executive Summary
# This is a very short technical breakdown on what is being tested.

# ## Hint Previews
# Players will see this before they 'buy' the hint.

# ## Hint Content
# 10 -- Your Hint

# ## Notes

# If your solve script isn't verbose enough, or if you want additional information 
# transmitted to the challenge development team, you would put information such as 
# steps to solve in here. 

def h(num: int, text: str) -> str:
    """Helper function to format Markdown headers."""
    return f"{'#' * num} {text}"

def h1(text: str) -> str:
    """Helper function to format Markdown headers."""
    return h(1, text)

def h2(text: str) -> str:
    """Helper function to format Markdown headers."""
    return h(2, text)

def div(*body: str):
    """Helper function to format Markdown divs."""
    return "\n".join(body)

def bold(text: str) -> str:
    """Helper function to format Markdown bold text."""
    return f"**{text}**"

def ol(*body: str) -> str:
    """Helper function to format Markdown ordered lists."""
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(body)) + "\n\n"

def answer(answer: str | Answer | Template):
    """Helper function to format answers."""
    if isinstance(answer, Answer):
        return answer.body
    elif isinstance(answer, Template):
        return answer.eval_str
    elif isinstance(answer, str):
        return answer
    else:
        raise TypeError("Unsupported answer type.")

def hint_body(hint_body: str | TextBody):
    """Helper function to format hint bodies."""
    if isinstance(hint_body, TextBody):
        return hint_body.content
    elif isinstance(hint_body, str):
        return hint_body
    else:
        raise TypeError("Unsupported hint body type.")

# **Author: Your Name**
def compose_to_markdown(compose: ComposeFile) -> str:
    """Convert a ComposeFile object to a Markdown representation."""
    chall = compose.challenge
    return div(
        h1(chall.name),
        div(
            h2("Challenge Description"),
            chall.description or "No description provided."
        ),
        div(
            h2("Questions"),
            ol(*[f"{q.name} -- {q.body} -- {q.points}" for q in chall.questions])
        ),
        div(
            h2("Answers"),
            ol(*[f"A{i + 1}: {answer(q.answer)}" for i, q in enumerate(chall.questions)]) or "No answers provided."
        ),
        div(
            h2("Executive Summary"),
            chall.summary or "No executive summary provided."
        ),
        div(
            h2("Hint Previews"),
            ol(*[f"H{i + 1}: {hint.preview}" for i, hint in enumerate(chall.hints if chall.hints else [])]) or "No hint previews provided."
        ),
        div(
            h2("Hint Content"),
            ol(*[f"H{i + 1}: {hint.deduction} -- {hint_body(hint.body)}" for i, hint in enumerate(chall.hints if chall.hints else [])]) or "No hint content provided."
        ),
        div(
            h2("Notes"),
            "<Provides your own notes here>"
        )
    )
