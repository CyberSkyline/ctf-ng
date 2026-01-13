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
from yaml import AliasEvent, Event, MappingEndEvent, MappingStartEvent, SafeLoader, ScalarEvent
logger = logging.getLogger(__name__)

class Rewriter:
    """Rewriter class for processing YAML events, resolving aliases, and rewriting variables."""
    
    def __init__(self, loader: SafeLoader):
        self._loader = loader
        self._anchors: dict[str, ScalarEvent] = {}
        logger.debug(f"Rewriter initialized with loader: {loader}")
    
    def _resolve_alias(self, alias: AliasEvent) -> AliasEvent | ScalarEvent:
        """Resolve an alias event to its corresponding event scalar event if possible."""

        logger.debug(f"Resolving alias: {alias.anchor}")
        if alias.anchor not in self._anchors:
           return alias

        resolved_event = self._anchors.get(alias.anchor)
        if not isinstance(resolved_event, ScalarEvent):
            raise ValueError(f"Alias '{alias.anchor}' does not point to a valid scalar event")
        
        return resolved_event


    def _rewrite_variable(self, variable_name: str, events: Generator[Event, None, None]) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_variable")
        events_mapping: dict[str, tuple[ScalarEvent, list[Event]]] = {}
        final_event: Event | None = None
        try:
            while (key_event := next(events)) and isinstance(key_event, ScalarEvent):
                logger.debug(f"Key event value: {key_event.value}")
                value_event = next(events)
                value_events = [value_event]
                unmatched_starts = 1 if isinstance(value_event, MappingStartEvent) else 0
                while unmatched_starts > 0:
                    next_event = next(events)
                    if isinstance(next_event, MappingStartEvent):
                        unmatched_starts += 1
                    elif isinstance(next_event, MappingEndEvent):
                        unmatched_starts -= 1

                    value_events.append(next_event)
                events_mapping[key_event.value] = (key_event, value_events)
            else:
                logger.debug(f"No more key events, storing final event: {key_event}")
                final_event = key_event
        except StopIteration:
            pass
        
        if 'template' not in events_mapping:
            logger.debug("No 'template' key found in variable")
            raise ValueError(f"Variable '{variable_name}' must have a 'template' key")
        
        template_key, template_value = events_mapping.pop('template')
        if len(template_value) > 1 or not isinstance(template_value[0], ScalarEvent | AliasEvent):
            raise ValueError(f"Variable '{variable_name}' template value must be a single scalar or alias event")
        template_value = template_value[0]
        logger.debug(f"Template key: {template_key}, value: {template_value}")

        if 'default' not in events_mapping:
            logger.debug("No 'default' key found in variable")
            raise ValueError(f"Variable '{variable_name}' must have a 'default' key")
        
        default_key, default_value = events_mapping.pop('default')
        if len(default_value) > 1 or not isinstance(default_value[0], ScalarEvent | AliasEvent):
            raise ValueError(f"Variable '{variable_name}' default value must be a single scalar or alias event")
        default_value = default_value[0]
        logger.debug(f"Default key: {default_key}, value: {default_value}")

        if default_value.anchor is None:
            raise ValueError("Default value must have an anchor for variable rewriting")

        yield template_key
        if isinstance(template_value, AliasEvent) and isinstance((resolved := self._resolve_alias(template_value)), ScalarEvent):
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
        logger.debug("Finished template mapping")

        logger.debug("Yielding default key and value with cleared anchor")
        default_value.anchor = None
        yield from (default_key, default_value)


        for (key_event, value_event) in events_mapping.values():
            yield key_event
            if isinstance(value_event, AliasEvent):
                yield self._resolve_alias(value_event)
            else:
                yield from value_event

        if final_event is not None:
            logger.debug("Yielding final event after variable mapping")
            yield final_event
        else:
            logger.debug("No final event to yield after variable mapping")

    def _rewrite_variables(self, events: Generator[Event, None, None]) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_variables")
        
        for event in events:
            if isinstance(event, ScalarEvent) and event.value == "variables":
                logger.debug("Found 'variables' key, extracting variable events")
                yield event
                break
            
            yield event
        else:
            logger.debug("No 'variables' section found in events")
            return
        
        event = next(events)
        yield event
        if not isinstance(event, MappingStartEvent):
            logger.debug("yaml events following `variables` do not start with MappingStartEvent")
            yield from events
            return
        
        try:
            while (event := next(events)):
                if isinstance(event, ScalarEvent):
                    logger.debug(f"Processing variable key: {event.value}")
                    yield event
                    mapping_event = next(events)
                    if not isinstance(mapping_event, MappingStartEvent):
                        logger.debug("No MappingStartEvent after variable key")
                        raise ValueError("variable must be followed by a mapping")
                    yield mapping_event
                    yield from self._rewrite_variable(event.value, events)
                elif isinstance(event, MappingEndEvent):
                    logger.debug("Reached end of variables mapping")
                    yield event
                    yield from events
                    return
                else:
                    raise ValueError("Unexpected event type in variables mapping")

        except StopIteration:
            return

    def _log_events(self, events: Generator[Event, None, None], context: str) -> Generator[Event, None, None]:
        """Generator to log events from the loader for debugging purposes."""
        for event in events:
            logger.debug(f"{context} event: {event}")
            yield event

    def _loader_events(self) -> Generator[Event, None, None]:
        logger.debug("Entering loader_events")
        while True:
            if self._loader.check_event():
                event = self._loader.get_event()
                yield event
            else:
                return

    def _persist_anchored_scalar(self, event: Event) -> Event:
        """Store a scalar event in the anchors dictionary if it has an anchor."""
        if isinstance(event, ScalarEvent) and event.anchor is not None:
            logger.debug(f"Persisting anchored event: {event.anchor}")
            self._anchors[event.anchor] = event
        return event

    def _persist_anchored_scalars(self, events: Generator[Event, None, None]) -> Generator[Event, None, None]:
        """Store an scalars events in the anchors dictionary if it has an anchor."""
        yield from (self._persist_anchored_scalar(event) for event in events)

    # TODO: Refactor this to utilize a pipeline type architecture instead
    def rewrite(self) -> Generator[Event, None, None]:
        logger.debug("Entering rewrite_aliases")
        pipeline = self._loader_events()
        pipeline = self._log_events(pipeline, "loader")
        pipeline = self._persist_anchored_scalars(pipeline)
        pipeline = self._rewrite_variables(pipeline)
        pipeline = self._log_events(pipeline, "final")
        yield from pipeline

