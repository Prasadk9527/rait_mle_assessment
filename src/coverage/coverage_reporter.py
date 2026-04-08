# src/coverage/coverage_reporter.py
from typing import List, Dict, Any
import pandas as pd
from src.schema.canonical_schema import Interaction, CoverageReport, EvaluationResult
import logging

logger = logging.getLogger(__name__)

class CoverageReporter:
    """Reports on data coverage and metric scoreability"""
    
    def __init__(self):
        self.coverage_reports: Dict[str, CoverageReport] = {}
        logger.info("Initialized Coverage Reporter")
    
    def generate_report(self, interactions: List[Interaction]) -> CoverageReport:
        """Generate comprehensive coverage report for a set of interactions"""
        
        logger.info(f"Generating coverage report for {len(interactions)} interactions")
        
        if not interactions:
            logger.warning("No interactions provided for coverage report")
            return CoverageReport(
                supplier_id="unknown",
                total_interactions=0,
                scoreable_interactions=0,
                fields_available={},
                metrics_complete={},
                metrics_partial={},
                recommendations=[]
            )
        
        supplier_id = interactions[0].supplier_id
        logger.debug(f"Processing supplier: {supplier_id}")
        
        fields = ['confidence_score', 'response_time_ms', 'model_metadata', 
                  'prompt_metadata', 'response_metadata', 'safety_flags']
        
        fields_available = {}
        for field in fields:
            present = sum(1 for i in interactions if getattr(i, field) is not None)
            fields_available[field] = present / len(interactions)
            logger.debug(f"Field {field}: {fields_available[field]:.1%} completeness")
        
        scoreable = sum(1 for i in interactions 
                       if i.prompt and i.response and i.timestamp)
        
        logger.info(f"Scoreable interactions: {scoreable}/{len(interactions)}")
        
        metrics_complete = {
            "prompt_injection_detection": fields_available.get('safety_flags', 0) > 0.5,
            "response_quality_parity": True,
            "confidence_calibration": fields_available.get('confidence_score', 0) > 0.5
        }
        
        metrics_partial = {
            "prompt_injection_detection": True,
            "response_quality_parity": True,
            "confidence_calibration": fields_available.get('confidence_score', 0) > 0
        }
        
        recommendations = []
        if fields_available.get('confidence_score', 0) < 0.5:
            recommendations.append("Request confidence scores from supplier for better calibration metrics")
            logger.debug("Confidence score availability below threshold")
        
        if fields_available.get('model_metadata', 0) < 0.5:
            recommendations.append("Request model metadata (name, version) for transparency")
            logger.debug("Model metadata availability below threshold")
        
        if fields_available.get('safety_flags', 0) < 0.5:
            recommendations.append("Consider requesting safety flags for better security monitoring")
            logger.debug("Safety flags availability below threshold")
        
        report = CoverageReport(
            supplier_id=supplier_id,
            total_interactions=len(interactions),
            scoreable_interactions=scoreable,
            fields_available=fields_available,
            metrics_complete=metrics_complete,
            metrics_partial=metrics_partial,
            recommendations=recommendations
        )
        
        self.coverage_reports[supplier_id] = report
        logger.info(f"Coverage report generated for {supplier_id}")
        
        return report
    
    def print_report(self, report: CoverageReport):
        """Pretty print coverage report"""
        logger.info(f"Printing coverage report for {report.supplier_id.upper()}")
        
        print(f"\n{'='*60}")
        print(f"Coverage Report: {report.supplier_id.upper()}")
        print(f"{'='*60}")
        print(f"Total Interactions: {report.total_interactions}")
        print(f"Scoreable Interactions: {report.scoreable_interactions}")
        
        print(f"\nField Completeness:")
        for field, completeness in report.fields_available.items():
            bar = "█" * int(completeness * 20) + "░" * (20 - int(completeness * 20))
            print(f"  {field:20} {bar} {completeness:.1%}")
        
        print(f"\nMetric Scoreability:")
        for metric, complete in report.metrics_complete.items():
            status = "✓ Full" if complete else "⚠ Partial"
            print(f"  {metric:30} {status}")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")