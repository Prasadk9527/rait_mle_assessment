import logging
import sys
from datetime import datetime
import os

def setup_logger(name, log_file=None, level=logging.INFO):
    """Setup logger with file and console handlers"""

    if log_file:
        os.makedirs(os.path.dirname(log_file),exist_ok=True)
    
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Root logger for the project
root_logger = setup_logger('rait_mle', 'logs/assessment.log')