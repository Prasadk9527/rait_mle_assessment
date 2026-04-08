
## 3. Canonical Schema

# src/schema/canonical_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class InteractionStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"

class SupplierMetadata(BaseModel):
    """Metadata about the supplier"""
    supplier_id: str
    supplier_name: str
    data_format: str
    data_completeness: float = Field(ge=0, le=1, description="0-1 completeness score")

class ModelMetadata(BaseModel):
    """Optional model-specific metadata"""
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    token_usage: Optional[Dict[str, int]] = None  # prompt_tokens, completion_tokens, total_tokens

class Interaction(BaseModel):
    """Canonical schema for all interactions"""
    # Required fields - minimal viable data contract
    interaction_id: str
    timestamp: datetime
    prompt: str
    response: str
    supplier_id: str
    
    # Optional fields - enhanced data when available
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Supplier-assigned confidence")
    response_time_ms: Optional[float] = None
    model_metadata: Optional[ModelMetadata] = None
    prompt_metadata: Optional[Dict[str, Any]] = None  # For additional prompt context
    response_metadata: Optional[Dict[str, Any]] = None  # For additional response data
    safety_flags: Optional[List[str]] = None  # Any safety/security flags from supplier
    
    # Quality indicators
    data_quality: InteractionStatus = InteractionStatus.COMPLETE
    missing_fields: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EvaluationResult(BaseModel):
    """Result of metric evaluation"""
    metric_name: str
    metric_category: str
    supplier_id: str
    score: float
    confidence: float = Field(ge=0, le=1, description="Confidence in this score")
    coverage: float = Field(ge=0, le=1, description="Data coverage for this metric")
    threshold_status: str  # "pass", "warning", "fail"
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class CoverageReport(BaseModel):
    """Coverage report for a supplier"""
    supplier_id: str
    total_interactions: int
    scoreable_interactions: int
    fields_available: Dict[str, float]  # field name -> completeness percentage
    metrics_complete: Dict[str, bool]  # metric name -> can be fully computed
    metrics_partial: Dict[str, bool]  # metric name -> can be partially computed
    recommendations: List[str]