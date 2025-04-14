import logging
from datetime import datetime
import time

class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Format time to match: 2025-04-14 16:01:22 +0000
        ct = self.converter(record.created)
        t = time.strftime("%Y-%m-%d %H:%M:%S +0000", ct)
        return t

formatter = CustomFormatter(
    fmt='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
