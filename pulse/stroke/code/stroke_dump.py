import logging
import json
import os
import datetime
import pulse.config.config as config
import random

from ._stroke_codes import stroke_errors
from typing import Any, Union
from pulse.core.core_dir import STROKE_PATH


def dump(code: int, meta: str = None, __as_command: bool = False) -> None:
    if code not in stroke_errors:
        return

    rand_5: int = random.randint(10000, 99999)

    data: dict[str, Any] = config.load()
    if data.get("stroke", False) is False and __as_command is False:
        return

    logging.debug("Dumping the stroke...")
    timedate: str = datetime.datetime.now()
    timedate_file: str = timedate.strftime("%Y-%m-%dT%H:%M:%S")
    timedate_name: str = timedate.strftime("%Y%m%dT%H%M%S")
    name: str = f"stroke_{timedate_name}{code}_{rand_5}.json"
    name = name.strip()

    error_node: dict[str, Any] = {
        "event_timestamp": timedate_file,
        "code": code,
        "message": stroke_errors[code].problem,
        "meta": meta,
    }
    fix_node: dict[str, Union[str, list[str]]] = {
        "description": stroke_errors[code].fix,
        "steps": stroke_errors[code].hints,
    }
    node: dict[str, dict] = {"error": error_node, "fix": fix_node}

    os.makedirs(STROKE_PATH, exist_ok=True)
    with open(os.path.join(STROKE_PATH, name), "w") as dump_file:
        json.dump(node, dump_file, indent=4)

    logging.info("Stroke has been dumped!")
