import logging
from pulse.core.core_group import pulse
from pulse.config.config import load

if __name__ == "__main__":

    log_format = "%(levelname)s: %(message)s"
    logging.basicConfig(format=log_format)
    info = load()
    logging.basicConfig(level=info.get("log", 0), )
    logging.getLogger("git.cmd").setLevel(level=logging.ERROR)
    pulse()
