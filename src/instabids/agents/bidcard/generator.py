"""
Bid card generation module for InstaBids.

This module handles the generation of bid cards based on project data and
image analysis. It classifies projects into categories and job types,
calculates confidence scores, and creates bid card entries in the database.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import asyncio
from ..homeowner.classifier import classify_project_with_llm

logger = logging.getLogger(__name__)

# Categories and job types for classification (assuming these remain relevant for classifier)
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


async def generate_bid_card_data(
    project_id: str, 
    project_data: Dict[str, Any],
    photo_meta: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Classifies the project and prepares data necessary for creating a bid card.
    This function does NOT create the bid card in the database directly.
    It returns a dictionary of parameters for the CreateBidCardTool.
    
    Args:
        project_id: The ID of the project.
        project_data: Project information including title, description, etc.
        photo_meta: Metadata and analysis results from uploaded photos.
        
    Returns:
        A dictionary containing data prepared for bid card creation tool.
    """
    logger.info(f"Preparing bid card data for project {project_id}")
    
    description = project_data.get("description", "")
    title = project_data.get("title", "")
    budget_range = project_data.get("budget_range", "")
    timeline = project_data.get("timeline", "")
    
    current_photo_meta_list = photo_meta if photo_meta is not None else []

    (
        primary_category,
        primary_job_type,
        primary_confidence,
        secondary_category,
        secondary_job_type,
        secondary_confidence,
        tertiary_category,
        tertiary_job_type,
        tertiary_confidence,
        classification_details
    ) = await classify_project_with_llm(
        project_description=description,
        image_analysis_results=current_photo_meta_list 
    )
    
    photo_meta_for_confidence_adjustment = current_photo_meta_list[0] if current_photo_meta_list else {}

    if photo_meta_for_confidence_adjustment and photo_meta_for_confidence_adjustment.get("labels"):
        primary_confidence = _adjust_confidence_with_vision(
            primary_confidence,
            primary_category,
            primary_job_type,
            photo_meta_for_confidence_adjustment
        )
    
    status = "final" if primary_confidence >= 0.7 else "draft"
    
    bid_card_tool_params = {
        "project_id": project_id,
        "primary_category": primary_category,
        "primary_job_type": primary_job_type,
        "primary_ai_confidence": primary_confidence,
        "secondary_category": secondary_category,
        "secondary_job_type": secondary_job_type,
        "secondary_ai_confidence": secondary_confidence,
        "tertiary_category": tertiary_category,
        "tertiary_job_type": tertiary_job_type,
        "tertiary_ai_confidence": tertiary_confidence,
        "classification_details": classification_details, 
        "budget_range": budget_range,
        "timeline": timeline,
        "photo_meta": current_photo_meta_list, 
        "status": status
    }
    
    logger.info(f"Prepared bid card data for CreateBidCardTool: {bid_card_tool_params}")
    return bid_card_tool_params


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
        keywords_for_category = category_keywords.get(category, [])
        total_keywords = len(keywords_for_category)
        
        if total_keywords > 0:
            for label_obj in labels: 
                label_description = label_obj.get("description", "").lower()
                if any(keyword in label_description for keyword in keywords_for_category):
                    matching_keywords += 1
        
            if matching_keywords > 0:
                vision_confidence_boost = (matching_keywords / total_keywords) * 0.2 
                adjusted_confidence = base_confidence + vision_confidence_boost 
                return min(adjusted_confidence, 0.99)  
        
        return base_confidence
        
    except Exception as e:
        logger.error(f"Error adjusting confidence with vision: {e}")
        return base_confidence