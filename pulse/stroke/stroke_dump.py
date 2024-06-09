import logging
import json
import os
import datetime
import pulse.config.config as config
import random

from .stroke_codes import stroke_errors
from pulse.core.core_dir import STROKE_PATH

def dump(code: int, meta: str = None, __as_command: bool = False) -> None:
    if not code in stroke_errors:
        return

    rand_5 = random.randint(10000, 99999)

    data = config.load()
    if data.get("stroke", False) == False and __as_command is False: 
        return

    logging.debug("Dumping the stroke...")
    timedate = datetime.datetime.now()
    timedate_file = timedate.strftime("%Y-%m-%dT%H:%M:%S")
    timedate_name = timedate.strftime("%Y%m%dT%H%M%S")
    name = f"stroke_{timedate_name}{code}_{rand_5}.json"
    name = name.strip()

    error_node = {
        "event_timestamp": timedate_file,
        "code": code,
        "message": stroke_errors[code].problem,
        "meta": meta
    }
    fix_node = {
        "description": stroke_errors[code].fix,
        "steps": stroke_errors[code].hints
    }
    node = {
        "error": error_node,
        "fix": fix_node
    }

    os.makedirs(STROKE_PATH, exist_ok=True)
    with open(os.path.join(STROKE_PATH, name), "w") as dump_file:
        json.dump(node, dump_file, indent=4)
    
    logging.info("Stroke has been dumped!")