# src/adapters/base_adapter.py
from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from src.schema.canonical_schema import Interaction, CoverageReport

class BaseAdapter(ABC):
    """Base class for all supplier adapters"""
    
    def __init__(self, supplier_id: str, supplier_name: str):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.interactions: List[Interaction] = []
        
    @abstractmethod
    def load_data(self, data_source: str) -> pd.DataFrame:
        """Load data from supplier-specific format"""
        pass
    
    @abstractmethod
    def transform_to_canonical(self, raw_data: pd.DataFrame) -> List[Interaction]:
        """Transform raw data to canonical schema"""
        pass
    
    def generate_coverage_report(self) -> CoverageReport:
        """Generate coverage report based on loaded interactions"""
        if not self.interactions:
            return CoverageReport(
                supplier_id=self.supplier_id,
                total_interactions=0,
                scoreable_interactions=0,
                fields_available={},
                metrics_complete={},
                metrics_partial={},
                recommendations=[]
            )
        
        # Analyze field completeness
        fields = ['confidence_score', 'response_time_ms', 'model_metadata', 
                  'prompt_metadata', 'response_metadata', 'safety_flags']
        
        fields_available = {}
        for field in fields:
            present = sum(1 for i in self.interactions if getattr(i, field) is not None)
            fields_available[field] = present / len(self.interactions)
        
        # Determine scoreable interactions
        scoreable = sum(1 for i in self.interactions 
                       if i.prompt and i.response and i.timestamp)
        
        # Generate recommendations
        recommendations = []
        if fields_available.get('confidence_score', 0) < 0.5:
            recommendations.append("Low confidence score availability - consider requesting confidence scores from supplier")
        if fields_available.get('model_metadata', 0) < 0.5:
            recommendations.append("Limited model metadata - may affect transparency metrics")
        
        return CoverageReport(
            supplier_id=self.supplier_id,
            total_interactions=len(self.interactions),
            scoreable_interactions=scoreable,
            fields_available=fields_available,
            metrics_complete={},  # To be filled by metric evaluator
            metrics_partial={},   # To be filled by metric evaluator
            recommendations=recommendations
        )