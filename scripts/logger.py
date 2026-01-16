import logging
import os
from datetime import datetime
from scripts.config.settings import LOG_DIR


def get_logger(name="mcg"):
    os.makedirs(LOG_DIR, exist_ok=True)

    log_file = os.path.join(
        LOG_DIR,
        f"daily_{datetime.utcnow().strftime('%Y-%m-%d')}.log"
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(sh)

    return logger