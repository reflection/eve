import json
import logging
import logging.config
import os
import sqlite3

import yaml
from apscheduler import Scheduler
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from feedback import feedback_handle_message, feedback_threads_ts
from schedule import sync_schedules
from schema import ensure_schema

with open("logging.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

app = App(token=SLACK_BOT_TOKEN, ignoring_self_events_enabled=False)
client = WebClient(token=SLACK_BOT_TOKEN)
groq = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
conn = sqlite3.connect(f"{SLACK_BOT_TOKEN}.db", check_same_thread=False)
ensure_schema(conn)


@app.event("message")
def handle_message(say, body):
    metadata = body.get("metadata", {})
    event_type = metadata.get("event_type")
    thread_ts = body.get("thread_ts", None)
    if event_type == "feedback" or thread_ts in feedback_threads_ts:
        feedback_handle_message(body)

    logging.info(json.dumps(body))
    # event = body["event"]
    # thread_ts = event.get("thread_ts", None)
    # if thread_ts:
    #     say("Message received!", thread_ts=thread_ts)


@app.command("/schedule")
def handle_schedule_command(ack, respond, command):
    ack()

    try:
        logging.info(command)
        # schedule_message(client, channel_id, message_text, post_at_timestamp)
        respond("Scheduled")
    except Exception as e:
        logging.error(f"Error handling command: {e}")


# @app.event("app_mention")
# def event_test(say, body):
#     logging.info(json.dumps(body))
#     event = body["event"]
#     thread_ts = event.get("thread_ts", None)
#     say(text="Hello", thread_ts=thread_ts)

with Scheduler() as scheduler:
    sync_schedules(conn, client, groq, scheduler)
    scheduler.start_in_background()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
