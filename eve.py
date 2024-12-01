import json
import logging
import logging.config
import os

import yaml
from apscheduler import Scheduler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from feedback import feedback_threads_ts, handle_feedback_message
from schedule import sync_schedules
from schema import ensure_schema

with open("logging.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

ensure_schema()

app = App(token=SLACK_BOT_TOKEN)


@app.event("message")
def handle_message(say, body):
    thread_ts = body.get("event", {}).get("thread_ts")
    if thread_ts in feedback_threads_ts:
        handle_feedback_message(body)

    logging.info(json.dumps(body))


with Scheduler() as scheduler:
    sync_schedules(scheduler)
    scheduler.start_in_background()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
