import logging
from typing import Generator
import typing
from attrs import define
from yaml import BaseLoader, Event, MappingStartEvent, ScalarEvent
import yaml
logger = logging.getLogger(__name__)


def rewrite_variable(loader: BaseLoader):
    logger.debug("Entering rewrite_variable")
    yield loader.get_event()
    events = {}
    while loader.check_event(ScalarEvent):
        key_event = loader.get_event()
        logger.debug(f"Key event value: {key_event.value}")
        events[key_event.value] = (key_event, loader.get_event())
        logger.debug(f"Events dict updated: {events}")
    
    if 'template' not in events:
        logger.debug("No 'template' key found in variable")
        return
    template_key, template_value = events['template']
    logger.debug(f"Template key: {template_key}, value: {template_value}")
    if 'default' not in events:
        logger.debug("No 'default' key found in variable")
        return
    default_key, default_value = events['default']
    logger.debug(f"Default key: {default_key}, value: {default_value}")
    template_value.anchor = default_value.anchor
    template_value.tag = '!template'
    default_value.anchor = None
    logger.debug(f"Setting template value anchor to: {template_value.anchor}")
    yield from (template_key, template_value, default_key, default_value)
    yield loader.get_event()

def rewrite_variables(loader):
    logger.debug("Entering rewrite_variables")
    if not loader.check_event(MappingStartEvent):
        logger.debug("No MappingStartEvent after 'variables'")
        return
    
    yield loader.get_event()
    logger.debug("Processing variables")
    while loader.check_event(ScalarEvent):
        yield loader.get_event()
        if not loader.check_event(MappingStartEvent):
            logger.debug("No MappingStartEvent after variable key")
            return
        yield from rewrite_variable(loader)



def rewrite_aliases(loader: BaseLoader) -> Generator[Event]:
    logger.debug("Entering rewrite_aliases")
    while True:
        if loader.check_event(ScalarEvent):
            logger.debug("Found ScalarEvent in rewrite_aliases")
            event = loader.get_event()
            logger.debug(f"Got event: {event}")
            yield event
            if event.value != "variables":
                logger.debug(f"Event value is not 'variables': {event.value}")
                continue
            logger.debug("Found 'variables' key, rewriting variables")
            yield from rewrite_variables(loader)
        elif loader.check_event():
            logger.debug("Found other event in rewrite_aliases")
            yield loader.get_event()
        else:
            logger.debug("No more events in rewrite_aliases")
            break

@define
class Template(yaml.YAMLObject):
    template: str
    
    yaml_tag = '!template'