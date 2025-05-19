"""Memory service implementation."""
from google.adk.services.memory_service import MemoryService
from google.adk.services.impl.memory_text_store import MemoryTextStore

_memory_service_instance = None

def get_memory_service():
    global _memory_service_instance
    if _memory_service_instance is None:
        # Using a simple in-memory text store. Replace with persistent store for production.
        _memory_service_instance = MemoryService(store=MemoryTextStore())
        print("Initialized In-Memory MemoryService (TextStore)")
    return _memory_service_instance
