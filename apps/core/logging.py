from pathlib import Path
import logging
import sys

def setup_logging(app_name: str, log_level=logging.DEBUG):
    """
    Setup logging for the application.
    Logs will be written to a file named `{app_name}.log` in the current working directory.
    """
    logger = logging.getLogger("creative")
    logger.setLevel(log_level)
    
    # Check if handlers already exist to avoid duplication
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        
        # File Handler
        file_handler = logging.FileHandler(f"{app_name}.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
