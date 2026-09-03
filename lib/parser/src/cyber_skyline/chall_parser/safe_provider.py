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
import string

from faker.providers import BaseProvider

# Letters that look like a 0 or a 1
AMBIGUOUS_LETTERS = 'OoIiLl'

SAFE_LETTERS = ''.join(c for c in string.ascii_letters if c not in AMBIGUOUS_LETTERS)


class SafeProvider(BaseProvider):
    def bothify_safe(self, text: str = '## ??') -> str:
        """Like bothify, but never picks a letter that looks like a 0 or a 1."""
        return self.bothify(text, letters=SAFE_LETTERS)
