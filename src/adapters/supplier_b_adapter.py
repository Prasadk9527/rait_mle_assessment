# src/adapters/supplier_b_adapter.py
import pandas as pd
from datetime import datetime
from typing import List
from src.adapters.base_adapter import BaseAdapter
from src.schema.canonical_schema import Interaction, InteractionStatus
import logging

logger = logging.getLogger(__name__)

class SupplierBAdapter(BaseAdapter):
    """Adapter for Supplier B (CSV batch logs)"""
    
    def __init__(self):
        super().__init__(supplier_id="supplier_b", supplier_name="Supplier B")
        logger.info(f"Initialized {self.supplier_name} adapter")
    
    def load_data(self, data_source: str) -> pd.DataFrame:
        """Load CSV data from Supplier B"""
        logger.info(f"Loading CSV data from {data_source}")
        
        try:
            df = pd.read_csv(data_source)
            logger.info(f"Successfully loaded {len(df)} rows from Supplier B")
            return df
        except FileNotFoundError:
            logger.error(f"CSV file not found: {data_source}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {data_source}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading Supplier B data: {e}")
            raise
    
    def transform_to_canonical(self, raw_data: pd.DataFrame) -> List[Interaction]:
        """Transform to canonical schema with limited metadata"""
        logger.info(f"Transforming {len(raw_data)} rows to canonical schema")
        
        interactions = []
        skipped_rows = 0
        missing_fields_count = 0
        
        for idx, row in raw_data.iterrows():
            missing_fields = []
            
            if pd.isna(row.get('user_query')):
                missing_fields.append('prompt')
                logger.debug(f"Row {idx} missing user_query field")
                skipped_rows += 1
                continue
            
            if pd.isna(row.get('system_response')):
                missing_fields.append('response')
                logger.debug(f"Row {idx} missing system_response field")
            
            try:
                interaction = Interaction(
                    interaction_id=str(row['timestamp']) + "_" + str(row.get('index', idx)),
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    prompt=row['user_query'],
                    response=row['system_response'],
                    supplier_id=self.supplier_id,
                    confidence_score=row.get('confidence_score'),
                    response_time_ms=None,
                    model_metadata=None,
                    data_quality=InteractionStatus.PARTIAL if missing_fields else InteractionStatus.COMPLETE,
                    missing_fields=missing_fields
                )
                
                interactions.append(interaction)
                
                if missing_fields:
                    missing_fields_count += 1
                    
            except Exception as e:
                logger.error(f"Error transforming row {idx}: {e}")
                skipped_rows += 1
                continue
        
        self.interactions = interactions
        logger.info(f"Transformed {len(interactions)} interactions successfully")
        
        if skipped_rows > 0:
            logger.warning(f"Skipped {skipped_rows} rows due to errors")
        
        if missing_fields_count > 0:
            logger.warning(f"{missing_fields_count} interactions have missing fields")
        
        return interactions