import logging
from pulse.core.core_group import pulse
from pulse.config.config import load

if __name__ == "__main__":
    log_format = "%(levelname)s: %(message)s"
    
    logging.addLevelName(logging.FATAL, "STROKE")
    
    info = load()
    
    root_logger = logging.getLogger()

    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    logging.basicConfig(format=log_format, level=info.get("log", logging.DEBUG))
    
    logging.getLogger("git.cmd").setLevel(level=logging.ERROR)
    
    pulse()
