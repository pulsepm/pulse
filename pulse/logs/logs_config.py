import logging
import pulse.config.config_load as config


def setup() -> None:
    info = config.load()
    log_format = "%(levelname)s: %(message)s"
    logging.basicConfig(format=log_format, level=info.get("log", 0), )
    logging.getLogger("git.cmd").setLevel(level=logging.ERROR)