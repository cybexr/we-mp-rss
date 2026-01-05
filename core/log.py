from logging.handlers import RotatingFileHandler
import logging
try:
    import colorlog
except ImportError:
    colorlog = None
from core.config import cfg

# Get log configuration
level = cfg.get("log.level", "INFO").upper()
log_file = cfg.get("log.file", "")

# Configure ROOT logger to capture ALL application logs
# This ensures logs from FastAPI, Uvicorn, SQLAlchemy, and all modules go to the file
root_logger = logging.getLogger()

# Set root logger level
if level == "DEBUG":
    root_logger.setLevel(logging.DEBUG)
elif level == "INFO":
    root_logger.setLevel(logging.INFO)
elif level == "ERROR":
    root_logger.setLevel(logging.ERROR)
elif level == "WARNING":
    root_logger.setLevel(logging.WARNING)
elif level == "CRITICAL":
    root_logger.setLevel(logging.CRITICAL)
else:
    root_logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicates
root_logger.handlers.clear()

# Create formatters
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if colorlog:
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg-white',
        }
    )
else:
    console_formatter = file_formatter

# Create file handler if log file is specified
if log_file:
    file_handler = RotatingFileHandler(
        f'{log_file}.log',
        maxBytes=1024*1024,  # 1MB per file
        backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)  # File captures all levels
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

# Create console handler (stdout/stderr - captured by Docker)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Console shows INFO and above
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# Create a module-level logger for backward compatibility
logger = logging.getLogger(__name__)