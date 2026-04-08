# src/adapters/supplier_c_adapter.py
import json
import pandas as pd
import pdfplumber
from datetime import datetime
from typing import List, Dict, Any
from src.adapters.base_adapter import BaseAdapter
from src.schema.canonical_schema import Interaction, InteractionStatus
import logging

logger = logging.getLogger(__name__)

class SupplierCAdapter(BaseAdapter):
    """Adapter for Supplier C (PDF summary + JSON samples)"""
    
    def __init__(self):
        super().__init__(supplier_id="supplier_c", supplier_name="Supplier C")
        logger.info(f"Initialized {self.supplier_name} adapter")
    
    def load_data(self, data_source: str) -> pd.DataFrame:
        """Load data from Supplier C (JSON samples)"""
        logger.info(f"Loading data from {data_source}")
        
        json_path = data_source + "/sampled_interactions.json"
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data['interactions'])
            logger.info(f"Successfully loaded {len(df)} interactions from Supplier C")
            return df
            
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {json_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading Supplier C data: {e}")
            raise
    
    def transform_to_canonical(self, raw_data: pd.DataFrame) -> List[Interaction]:
        """Transform to canonical schema with limited data"""
        logger.info(f"Transforming {len(raw_data)} rows to canonical schema")
        
        interactions = []
        missing_fields = ['model_metadata', 'response_time_ms', 'safety_flags']
        logger.debug(f"Expected missing fields for Supplier C: {missing_fields}")
        
        for idx, row in raw_data.iterrows():
            try:
                interaction = Interaction(
                    interaction_id=row['interaction_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    prompt=row['prompt'],
                    response=row['response'],
                    supplier_id=self.supplier_id,
                    confidence_score=None,
                    response_time_ms=None,
                    model_metadata=None,
                    data_quality=InteractionStatus.PARTIAL,
                    missing_fields=missing_fields
                )
                
                interactions.append(interaction)
                
            except KeyError as e:
                logger.warning(f"Missing required field in row {idx}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error transforming row {idx}: {e}")
                continue
        
        self.interactions = interactions
        logger.info(f"Transformed {len(interactions)} interactions successfully")
        
        if len(interactions) > 0:
            logger.warning(f"Supplier C data is partial - missing fields: {missing_fields}")
        
        return interactions