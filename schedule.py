import logging
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from slack_sdk.errors import SlackApiError


def sync_schedules(conn, client, scheduler):
    cur = conn.cursor()
    res = cur.execute("SELECT id, channel_id, message, schedule, tool FROM schedule")
    schedule_ids = [s.id for s in scheduler.get_schedules()]
    for schedule_id, channel_id, message, schedule, tool in res.fetchall():
        schedule_id = str(schedule_id)
        try:
            if schedule_id not in schedule_ids:
                scheduler.add_schedule(
                    post,
                    CronTrigger.from_crontab(schedule),
                    args=[client, channel_id, message, tool],
                    id=schedule_id,
                )
        except Exception as e:
            logging.error(f"Error scheduling id ({schedule_id}): {e}")


def post(client, channel_id, message, tool):
    try:
        metadata = {}
        if tool == "feedback":
            metadata = {
                "event_type": tool,
                "event_payload": {"day": datetime.today().isoformat()},
            }
        result = client.chat_postMessage(
            channel=channel_id,
            text=message,
            metadata=metadata,
        )
        logging.info(f"Message posted: {result}")
    except SlackApiError as e:
        logging.error(
            f"Error posting channel id ({channel_id}) message ({message}): {e}"
        )
