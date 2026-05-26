import json
import os

from datetime import datetime
from config import PROCESS_LOG_FILE


os.makedirs("output/logs", exist_ok=True)


def log_result(filename, status, reason=""):

    log = {
        "timestamp": str(datetime.now()),
        "filename": filename,
        "status": status,
        "reason": reason
    }

    with open(PROCESS_LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")