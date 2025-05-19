"""Session service implementation."""
from google.adk.services.session_service import SessionService
from google.adk.services.impl.session_memory_store import SessionMemoryStore

_session_service_instance = None

def get_session_service():
    global _session_service_instance
    if _session_service_instance is None:
        # Using a simple in-memory store for now. Replace with persistent store for production.
        _session_service_instance = SessionService(store=SessionMemoryStore())
        print("Initialized In-Memory SessionService")
    return _session_service_instance
