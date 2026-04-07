"""
Memory organ — Vector database and long-term knowledge storage for HumanOS.

Stores embeddings, collections, and search telemetry. Retrieves knowledge for recall
flows without coupling callers to a specific vector backend.
"""

default_app_config = "organs.memory.apps.MemoryConfig"
