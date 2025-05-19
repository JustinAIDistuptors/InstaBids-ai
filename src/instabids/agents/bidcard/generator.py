"""
Bid card generation module for InstaBids.

This module handles the generation of bid cards based on project data and
image analysis. It classifies projects into categories and job types,
calculates confidence scores, and creates bid card entries in the database.
"""

import logging
from typing import Dict, Any, List, Tuple
import asyncio
from ...tools.supabase.bid_cards import create_bid_card
from .classifier import classify_project # This import will require classifier.py to be created

logger = logging.getLogger(__name__)

# Categories and job types for classification
CATEGORIES = [
    "repair",
    "renovation",
    "installation",
    "maintenance",
    "construction",
    "landscaping",
    "cleaning",
    "other"
]

JOB_TYPES = {
    "repair": [
        "plumbing",
        "electrical",
        "roofing",
        "appliance",
        "hvac",
        "structural",
        "other"
    ],
    "renovation": [
        "kitchen",
        "bathroom",
        "basement",
        "whole_house",
        "room_addition",
        "flooring",
        "other"
    ],
    "installation": [
        "appliance",
        "flooring",
        "window",
        "door",
        "fixture",
        "system",
        "other"
    ],
    "maintenance": [
        "hvac",
        "plumbing",
        "electrical",
        "general",
        "seasonal",
        "other"
    ],
    "construction": [
        "addition",
        "new_build",
        "garage",
        "deck",
        "shed",
        "other"
    ],
    "landscaping": [
        "lawn",
        "garden",
        "tree",
        "irrigation",
        "hardscape",
        "other"
    ],
    "cleaning": [
        "general",
        "deep",
        "window",
        "carpet",
        "pressure_washing",
        "other"
    ],
    "other": ["other"]
}


async def generate_bid_card(
    project_id: str,
    project_data: Dict[str, Any],
    photo_meta: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate a bid card for a project.
    
    Args:
        project_id: The ID of the project
        project_data: Project information including title, description, etc.
        photo_meta: Metadata and analysis results from uploaded photos
        
    Returns:
        A dictionary containing the created bid card information
    """
    logger.info(f"Generating bid card for project {project_id}")
    
    description = project_data.get("description", "")
    title = project_data.get("title", "")
    budget_range = project_data.get("budget_range", "")
    timeline = project_data.get("timeline", "")
    
    category, job_type, confidence = await classify_project(
        description=description,
        title=title,
        photo_meta=photo_meta or {}
    )
    
    if photo_meta and photo_meta.get("labels"):
        confidence = _adjust_confidence_with_vision(
            confidence,
            category,
            job_type,
            photo_meta
        )
    
    status = "final" if confidence >= 0.7 else "draft"
    
    bid_card = await create_bid_card(
        project_id=project_id,
        category=category,
        job_type=job_type,
        budget_range=budget_range,
        timeline=timeline,
        photo_meta=photo_meta or {},
        ai_confidence=confidence,
        status=status
    )
    
    logger.info(f"Created bid card: {bid_card}")
    return bid_card


def _adjust_confidence_with_vision(
    base_confidence: float,
    category: str,
    job_type: str,
    photo_meta: Dict[str, Any]
) -> float:
    """
    Adjust confidence score based on vision analysis results.
    
    Args:
        base_confidence: The initial confidence score
        category: The classified category
        job_type: The classified job type
        photo_meta: Metadata from vision analysis
        
    Returns:
        Adjusted confidence score
    """
    try:
        labels = photo_meta.get("labels", [])
        
        category_keywords = {
            "repair": ["damage", "broken", "leaking", "cracked", "worn"],
            "renovation": ["remodel", "upgrade", "modernize", "transform", "update"],
            "installation": ["install", "new", "setup", "mount", "fixture"],
            "maintenance": ["clean", "maintain", "service", "tune", "seasonal"],
            "construction": ["build", "construct", "structure", "frame", "foundation"],
            "landscaping": ["garden", "plant", "lawn", "outdoor", "landscape"],
            "cleaning": ["clean", "wash", "sanitize", "debris", "dirt"],
        }
        
        matching_keywords = 0
        # Use .get(category, []) to provide a default empty list if category not in keywords
        keywords_for_category = category_keywords.get(category, [])
        total_keywords = len(keywords_for_category)
        
        if total_keywords > 0:
            for label_obj in labels: # Assuming labels are dicts with 'description'
                label_description = label_obj.get("description", "").lower()
                if any(keyword in label_description for keyword in keywords_for_category):
                    matching_keywords += 1
        
            if matching_keywords > 0:
                vision_confidence = matching_keywords / total_keywords
                adjusted_confidence = (base_confidence * 0.7) + (vision_confidence * 0.3)
                return min(adjusted_confidence, 0.95)  # Cap at 0.95
        
        return base_confidence
        
    except Exception as e:
        logger.error(f"Error adjusting confidence with vision: {e}")
        return base_confidence