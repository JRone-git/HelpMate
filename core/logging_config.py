import logging
import logging.config
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Get environment variables
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configure logging based on environment
    if environment == "development":
        # Development logging - detailed and colorful
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                },
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': '%(log_color)s[%(asctime)s] %(levelname)s in %(module)s:%(reset)s %(message)s',
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    },
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'formatter': 'colored',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'detailed',
                    'filename': logs_dir / f'app-{datetime.now().strftime("%Y-%m-%d")}.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf8'
                }
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                }
            },
            'root': {
                'level': log_level,
                'handlers': ['console', 'file']
            }
        }
    else:
        # Production logging - simpler and more efficient
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': logs_dir / f'app-{datetime.now().strftime("%Y-%m-%d")}.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 10,
                    'formatter': 'standard',
                    'encoding': 'utf8'
                }
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                }
            }
        }
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Test logging
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized in {environment} mode with level {log_level}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)

# Initialize logging when module is imported
logger = setup_logging()