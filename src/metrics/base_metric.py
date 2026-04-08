# src/metrics/base_metric.py
from abc import ABC, abstractmethod
from typing import List, Optional
from src.schema.canonical_schema import Interaction, EvaluationResult
import logging

logger = logging.getLogger(__name__)

class BaseMetric(ABC):
    """Base class for all evaluation metrics"""
    
    def __init__(self, name: str, category: str):
        """
        Initialize metric
        
        Args:
            name: Name of the metric
            category: Category of metric (security, fairness, transparency)
        """
        self.name = name
        self.category = category
        logger.debug(f"Initialized base metric: {name} (category: {category})")
    
    @abstractmethod
    def compute_score(self, interactions: List[Interaction]) -> EvaluationResult:
        """
        Compute metric score for a list of interactions
        
        Args:
            interactions: List of interactions in canonical schema
            
        Returns:
            EvaluationResult containing score and metadata
        """
        pass
    
    def _create_empty_result(self, supplier_id: str = "unknown") -> EvaluationResult:
        """
        Create an empty result when no interactions available
        
        Args:
            supplier_id: ID of the supplier
            
        Returns:
            EvaluationResult with default values
        """
        from src.schema.canonical_schema import EvaluationResult
        from datetime import datetime
        
        logger.warning(f"Creating empty result for metric {self.name} - no interactions available")
        
        return EvaluationResult(
            metric_name=self.name,
            metric_category=self.category,
            supplier_id=supplier_id,
            score=0.0,
            confidence=0.0,
            coverage=0.0,
            threshold_status="fail",
            details={"message": "No interactions available for evaluation"},
            timestamp=datetime.now()
        )
    
    def validate_interactions(self, interactions: List[Interaction]) -> bool:
        """
        Validate that interactions are in correct format
        
        Args:
            interactions: List of interactions to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not interactions:
            logger.warning(f"Validation failed for {self.name}: No interactions provided")
            return False
        
        logger.debug(f"Validating {len(interactions)} interactions for metric {self.name}")
        
        invalid_count = 0
        for idx, interaction in enumerate(interactions):
            if not interaction.prompt or not interaction.response:
                logger.debug(f"Interaction {idx} missing prompt or response")
                invalid_count += 1
            elif not interaction.interaction_id:
                logger.debug(f"Interaction {idx} missing interaction_id")
                invalid_count += 1
            elif not interaction.timestamp:
                logger.debug(f"Interaction {idx} missing timestamp")
                invalid_count += 1
        
        if invalid_count > 0:
            logger.warning(f"Validation for {self.name}: {invalid_count} invalid interactions")
            return False
        
        logger.debug(f"Validation passed for {self.name}: {len(interactions)} valid interactions")
        return True
    
    def get_coverage(self, interactions: List[Interaction], required_fields: List[str]) -> float:
        """
        Calculate data coverage for required fields
        
        Args:
            interactions: List of interactions
            required_fields: List of field names that are required for this metric
            
        Returns:
            Coverage score (0-1)
        """
        if not interactions:
            logger.warning(f"Coverage calculation for {self.name}: No interactions")
            return 0.0
        
        logger.debug(f"Calculating coverage for {self.name} with fields: {required_fields}")
        
        total = len(interactions)
        complete = 0
        
        for interaction in interactions:
            has_all = True
            for field in required_fields:
                if getattr(interaction, field, None) is None:
                    has_all = False
                    break
            
            if has_all:
                complete += 1
        
        coverage = complete / total if total > 0 else 0.0
        logger.debug(f"Coverage for {self.name}: {coverage:.1%} ({complete}/{total})")
        
        return coverage