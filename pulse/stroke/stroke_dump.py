import json
import os
import datetime
import pulse.config.config_load as config

from .stroke_codes import stroke_errors
from pulse.core.core_dir import STROKE_PATH

def dump(code: int) -> None:
    if not code in stroke_errors:
        return

    data = config.load()
    print("DUMP")
    if data.get("stroke", False) == False: 
        return

    timedate = datetime.datetime.now()
    timedate_file = timedate.strftime("%Y-%m-%dT%H:%M:%S")
    timedate_name = timedate.strftime("%Y%m%dT%H%M%S")
    name = f"stroke_{timedate_name}{code}.json"
    name = name.strip()

    print("DUMP2")
    error_node = {
        "event_timestamp": timedate_file,
        "code": code,
        "message": stroke_errors[code].problem
    }
    fix_node = {
        "description": stroke_errors[code].fix,
        "steps": stroke_errors[code].hints
    }
    node = {
        "error": error_node,
        "fix": fix_node
    }
    print("DUMP3")

    os.makedirs(STROKE_PATH, exist_ok=True)
    with open(os.path.join(STROKE_PATH, name), "w") as dump_file:
        json.dump(node, dump_file, indent=4)
    print("DUMP4")