import logging
from pulse.core.core_group import pulse
from pulse.user import User

if __name__ == "__main__":
    
    usr = User()
    
    log_format = "%(levelname)s: %(message)s"
    logging.addLevelName(logging.FATAL, "STROKE")
    
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    logging.basicConfig(format=log_format, level=usr.log_power)

    logging.getLogger("git.cmd").setLevel(logging.ERROR)

    logging.getLogger('requests').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)

    print(logging.getLogger("git.cmd"))
    print(logging.getLevelName(root_logger))

    pulse()
