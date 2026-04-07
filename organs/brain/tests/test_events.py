"""
Tests for Brain event handling.
"""

import pytest
from core.bus import Event


class TestBrainEvents:
    def test_handle_knowledge_extracted(self):
        from organs.brain.events import handle_event
        event = Event(type="knowledge.extracted", source_organ="digestive_system", payload={"summary": "test"})
        # Should not raise
        handle_event(event)

    def test_handle_unknown_event(self):
        from organs.brain.events import handle_event
        event = Event(type="unknown.event", source_organ="test", payload={})
        # Should log warning but not raise
        handle_event(event)
