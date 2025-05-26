import os
from dotenv import load_dotenv
import sentry_sdk

load_dotenv()

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        send_default_pii=True,
        traces_sample_rate=1.0
    )