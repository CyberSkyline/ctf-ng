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
from typing import Generator
from yaml import AliasEvent, BaseLoader, Event, FullLoader, Loader, MappingEndEvent, MappingStartEvent, ScalarEvent, UnsafeLoader
import yaml
from faker import Faker
from faker.providers import address, automotive, bank, barcode, \
                            color, company, credit_card, currency, \
                            date_time, doi, emoji, file, geo, internet, \
                            isbn, job, lorem, misc, passport, person, \
                            phone_number, profile, python, sbn, ssn, user_agent
logger = logging.getLogger(__name__)

class Rewriter:
    """Rewriter class for processing YAML events, resolving aliases, and rewriting variables."""
    
    def __init__(self, loader: BaseLoader):
        self.loader = loader
        self.anchors: dict[str, ScalarEvent] = {}
        logger.debug(f"Rewriter initialized with loader: {loader}")
    
    def resolve_alias(self, alias: AliasEvent) -> AliasEvent | ScalarEvent:
        """Resolve an alias event to its corresponding event scalar event if possible."""

        logger.debug(f"Resolving alias: {alias.anchor}")
        if alias.anchor not in self.anchors:
           return alias

        resolved_event = self.anchors[alias.anchor]
        if not isinstance(resolved_event, ScalarEvent):
            raise ValueError(f"Alias '{alias.anchor}' does not point to a valid scalar event")
        
        return resolved_event


    def rewrite_variable(self, variable_name: str) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_variable")
        yield self.loader.get_event()
        events: dict[str, tuple[ScalarEvent, ScalarEvent | AliasEvent]] = {}
        while self.loader.check_event(ScalarEvent):
            key_event = self.loader.get_event()
            logger.debug(f"Key event value: {key_event.value}")
            events[key_event.value] = (key_event, self.loader.get_event())
            logger.debug(f"Events dict updated: {events}")
        
        if 'template' not in events:
            logger.debug("No 'template' key found in variable")
            raise ValueError(f"Variable '{variable_name}' must have a 'template' key")
        
        template_key, template_value = events.pop('template')
        logger.debug(f"Template key: {template_key}, value: {template_value}")

        if 'default' not in events:
            logger.debug("No 'default' key found in variable")
            raise ValueError(f"Variable '{variable_name}' must have a 'default' key")
        
        default_key, default_value = events.pop('default')
        logger.debug(f"Default key: {default_key}, value: {default_value}")

        if default_value.anchor is None:
            raise ValueError("Default value must have an anchor for variable rewriting")

        yield template_key
        if isinstance(template_value, AliasEvent) and isinstance((resolved := self.resolve_alias(template_value)), ScalarEvent):
            template_value = resolved

        if not isinstance(template_value, ScalarEvent):
            raise ValueError("Template value must be a scalar event after alias resolution if it occurs")
        
        # Create a template mapping that contains the variable name and template to evaluate
        logger.debug(f"Creating template mapping for variable '{variable_name}' with value: {template_value.value}")
        yield MappingStartEvent(anchor=default_value.anchor, tag='!template', implicit=False)
        yield ScalarEvent(value="variable", anchor=None, tag=None, implicit=(True, False))
        yield ScalarEvent(value=variable_name, anchor=None, tag=None, implicit=(True, False))
        yield ScalarEvent(value="eval", anchor=None, tag=None, implicit=(True, False))
        yield ScalarEvent(value=template_value.value, anchor=None, tag=None, implicit=(True, False))
        yield MappingEndEvent()

        default_value.anchor = None
        yield from (default_key, default_value)

        for _, (key_event, value_event) in events.items():
            yield key_event
            if isinstance(value_event, AliasEvent):
                yield self.resolve_alias(value_event)
            else:
                yield value_event

        yield self.loader.get_event()

    def rewrite_variables(self) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_variables")
        if not self.loader.check_event(MappingStartEvent):
            logger.debug("No MappingStartEvent after 'variables'")
            return
        
        yield self.loader.get_event()
        logger.debug("Processing variables")
        while self.loader.check_event(ScalarEvent):
            variable_key: ScalarEvent = self.loader.get_event()
            yield variable_key
            if not self.loader.check_event(MappingStartEvent):
                logger.debug("No MappingStartEvent after variable key")
                return
            yield from self.rewrite_variable(variable_key.value)

    # TODO: Refactor this to utilize a pipeline type architecture instead
    def rewrite(self) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_aliases")
        while True:
            if self.loader.check_event(ScalarEvent):
                logger.debug("Found ScalarEvent in rewrite_aliases")
                event: ScalarEvent = self.loader.get_event()
                logger.debug(f"Got event: {event}")
                if event.anchor is not None:
                    # Store the event in anchors if it has an anchor
                    logger.debug(f"Storing event in anchors with anchor: {event.anchor}")
                    self.anchors[event.anchor] = event
                yield event
                if event.value != "variables":
                    logger.debug(f"Event value is not 'variables': {event.value}")
                    continue
                logger.debug("Found 'variables' key, rewriting variables")
                yield from self.rewrite_variables()
            elif self.loader.check_event(AliasEvent):
                logger.debug("Attempting to resolve AliasEvent during rewrite_aliases")
                yield self.resolve_alias(self.loader.get_event())
            elif self.loader.check_event():
                logger.debug("Not a ScalarEvent or AliasEvent, yielding next event")
                yield self.loader.get_event()
            else:
                logger.debug("No more events in rewrite_aliases")
                break


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
    
    def eval(self):
        """Evaluate the template using Faker."""
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
    def from_yaml(cls, loader: Loader | FullLoader | UnsafeLoader | None, node: yaml.nodes.Node) -> 'Template':
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