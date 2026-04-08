# src/adapters/supplier_a_adapter.py
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from src.adapters.base_adapter import BaseAdapter
from src.schema.canonical_schema import Interaction, ModelMetadata, InteractionStatus
import logging

logger = logging.getLogger(__name__)

class SupplierAAdapter(BaseAdapter):
    """Adapter for Supplier A (full API access)"""
    
    def __init__(self):
        super().__init__(supplier_id="supplier_a", supplier_name="Supplier A")
        logger.info(f"Initialized {self.supplier_name} adapter")
    
    def load_data(self, data_source: str) -> pd.DataFrame:
        """Load JSON data from Supplier A"""
        logger.info(f"Loading data from {data_source}")
        
        try:
            with open(data_source, 'r') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data['interactions'])
            logger.info(f"Successfully loaded {len(df)} interactions from Supplier A")
            return df
            
        except FileNotFoundError:
            logger.error(f"Data file not found: {data_source}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {data_source}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading Supplier A data: {e}")
            raise
    
    def transform_to_canonical(self, raw_data: pd.DataFrame) -> List[Interaction]:
        """Transform to canonical schema with full metadata"""
        logger.info(f"Transforming {len(raw_data)} rows to canonical schema")
        
        interactions = []
        missing_fields_count = 0
        
        for idx, row in raw_data.iterrows():
            try:
                model_metadata = ModelMetadata(
                    model_name=row.get('model_name'),
                    model_version=row.get('model_version'),
                    temperature=row.get('temperature'),
                    max_tokens=row.get('max_tokens'),
                    token_usage=row.get('token_usage', {})
                )
                
                interaction = Interaction(
                    interaction_id=row['interaction_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    prompt=row['prompt'],
                    response=row['response'],
                    supplier_id=self.supplier_id,
                    confidence_score=row.get('confidence_score'),
                    response_time_ms=row.get('response_time_ms'),
                    model_metadata=model_metadata,
                    prompt_metadata=row.get('prompt_metadata'),
                    response_metadata=row.get('response_metadata'),
                    safety_flags=row.get('safety_flags', []),
                    data_quality=InteractionStatus.COMPLETE,
                    missing_fields=[]
                )
                
                interactions.append(interaction)
                
            except KeyError as e:
                logger.warning(f"Missing required field in row {idx}: {e}")
                missing_fields_count += 1
                continue
            except Exception as e:
                logger.error(f"Error transforming row {idx}: {e}")
                missing_fields_count += 1
                continue
        
        self.interactions = interactions
        logger.info(f"Transformed {len(interactions)} interactions successfully")
        
        if missing_fields_count > 0:
            logger.warning(f"Skipped {missing_fields_count} rows due to missing fields")
        
        return interactions