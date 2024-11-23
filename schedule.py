import logging
from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from slack_sdk.errors import SlackApiError

from prompt import global_prompt


def sync_schedules(conn, client, groq, scheduler):
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
                    args=[client, groq, channel_id, message, tool],
                    id=schedule_id,
                )
        except Exception as e:
            logging.error(f"Error scheduling id ({schedule_id}): {e}")


def post(client, groq, channel_id, message, tool):
    try:
        metadata = {}
        if tool == "feedback":
            metadata = {
                "event_type": tool,
                "event_payload": {"day": datetime.today().isoformat()},
            }
        history = [
            {"role": "system", "content": global_prompt},
            {"role": "user", "content": f"Rephrase the following as Eve: {message}"},
        ]
        res = groq.chat.completions.create(
            messages=history,
            model="llama-3.2-90b-vision-preview",
        )
        text = res.choices[0].message.content
        result = client.chat_postMessage(
            channel=channel_id,
            text=text,
            metadata=metadata,
        )
        logging.info(f"Message posted: {result}")
    except SlackApiError as e:
        logging.error(
            f"Error posting channel id ({channel_id}) message ({message}): {e}"
        )
