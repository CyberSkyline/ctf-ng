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
import logging
import yaml
from faker import Faker
from faker.providers import address, automotive, bank, barcode, \
                            color, company, credit_card, currency, \
                            date_time, doi, emoji, file, geo, internet, \
                            isbn, job, lorem, misc, passport, person, \
                            phone_number, profile, python, sbn, ssn, user_agent

logger = logging.getLogger(__name__)

fake = Faker()

all_providers = [
    address, automotive, bank, barcode, 
    color, company, credit_card, currency, 
    date_time, doi, emoji, file, geo, internet, 
    isbn, job, lorem, misc, passport, person, 
    phone_number, profile, python, sbn, ssn, user_agent
]

# Register all Faker providers
for provider in all_providers:
    fake.add_provider(provider)

class Template:
    def __init__(self, eval_str: str, parent_variable: str):
        """Initialize a Template object with a template string and optional parent variable."""
        logger.debug(f"Initializing Template with template: {eval_str}, parent_variable: {parent_variable}")
        self.eval_str: str = eval_str
        self.parent_variable: str = parent_variable
    
    def eval(self, seed: str | None = None):
        """Evaluate the template using Faker."""
        if seed is not None:
            fake.seed_instance(seed)

        logger.debug(f"Evaluating template: {self.eval_str}")
        evaluated = None
        if not self.eval_str:
            logger.debug("Template is empty, returning None")
            return None
        try:
            # Use eval to execute the template code
            evaluated = eval(self.eval_str, {'fake': fake})
        except Exception as e:
            logger.error(f"Error evaluating template '{self.eval_str}': {e}")
            raise ValueError(f"Invalid template: {self.eval_str}") from e
        
        return evaluated


    @classmethod
    def from_yaml(cls, loader: yaml.Loader | yaml.FullLoader | yaml.UnsafeLoader | None, node: yaml.nodes.Node) -> 'Template':
        logger.debug(f"Creating Template from YAML node: {node}")
        if not isinstance(node, yaml.nodes.MappingNode):
            raise yaml.YAMLError("Template must be a mapping")
        
        values = {k.value: v for k, v in node.value}
        if 'eval' not in values:
            raise yaml.YAMLError("Template must have a 'eval' key")
        if 'variable' not in values:
            raise yaml.YAMLError("Template must have a 'variable' key")
        
        return cls(eval_str=values['eval'].value, parent_variable=values['variable'].value)
    
    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data: 'Template') -> yaml.nodes.MappingNode:
        logger.debug(f"Converting Template to YAML: {data}")
        return dumper.represent_mapping("!template", [
            ('eval', data.eval_str),
            ('variable', data.parent_variable)
        ])