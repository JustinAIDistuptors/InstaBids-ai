"""
Event definitions for A2A communication in InstaBids.

This module defines all events used for Agent-to-Agent communication
in the InstaBids platform. Each event class should inherit from BaseEvent
and define its own schema and validation logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


class EventType(Enum):
    """Enumeration of all event types in the system."""
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    BID_CARD_CREATED = "bid_card_created"
    BID_CARD_UPDATED = "bid_card_updated"
    CONTRACTOR_INVITED = "contractor_invited"
    CONTRACTOR_RESPONDED = "contractor_responded"
    MATCH_MADE = "match_made"
    MESSAGE_SENT = "message_sent"


@dataclass
class BaseEvent:
    """Base class for all A2A events."""
    event_type: EventType
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    sender: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_type": self.event_type.value,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "sender": self.sender,
        }


@dataclass
class ProjectCreatedEvent(BaseEvent):
    """Event emitted when a new project is created."""
    project_id: str
    owner_id: str
    title: str
    description: str
    zipcode: str
    
    def __post_init__(self):
        self.event_type = EventType.PROJECT_CREATED
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "project_id": self.project_id,
            "owner_id": self.owner_id,
            "title": self.title,
            "description": self.description,
            "zipcode": self.zipcode,
        })
        return base_dict


@dataclass
class BidCardCreatedEvent(BaseEvent):
    """Event emitted when a new bid card is created."""
    bid_card_id: str
    project_id: str
    category: str
    job_type: str
    budget_range: str
    timeline: str
    photo_meta: Dict[str, Any]
    ai_confidence: float
    status: str
    
    def __post_init__(self):
        self.event_type = EventType.BID_CARD_CREATED
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "bid_card_id": self.bid_card_id,
            "project_id": self.project_id,
            "category": self.category,
            "job_type": self.job_type,
            "budget_range": self.budget_range,
            "timeline": self.timeline,
            "photo_meta": self.photo_meta,
            "ai_confidence": self.ai_confidence,
            "status": self.status,
        })
        return base_dict


@dataclass
class ContractorInvitedEvent(BaseEvent):
    """Event emitted when a contractor is invited to bid on a project."""
    project_id: str
    contractor_id: str
    bid_card_id: str
    invitation_method: str  # "email" or "sms"
    
    def __post_init__(self):
        self.event_type = EventType.CONTRACTOR_INVITED
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "project_id": self.project_id,
            "contractor_id": self.contractor_id,
            "bid_card_id": self.bid_card_id,
            "invitation_method": self.invitation_method,
        })
        return base_dict


@dataclass
class MatchMadeEvent(BaseEvent):
    """Event emitted when a match is made between a homeowner and contractor."""
    project_id: str
    contractor_id: str
    match_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def __post_init__(self):
        self.event_type = EventType.MATCH_MADE
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "project_id": self.project_id,
            "contractor_id": self.contractor_id,
            "match_time": self.match_time,
        })
        return base_dict


@dataclass
class MessageSentEvent(BaseEvent):
    """Event emitted when a message is sent in a project conversation."""
    message_id: str
    project_id: str
    sender_role: str  # "homeowner", "contractor", or "agent"
    content: str
    
    def __post_init__(self):
        self.event_type = EventType.MESSAGE_SENT
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "message_id": self.message_id,
            "project_id": self.project_id,
            "sender_role": self.sender_role,
            "content": self.content,
        })
        return base_dict