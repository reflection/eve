import logging

from auth import get_slack_client

feedback_threads_ts = {}
canvas_id = "F05N5JRB1MF"


def setup_feedback(thread_ts, day):
    global feedback_threads_ts
    feedback_threads_ts[thread_ts] = day
    try:
        client = get_slack_client()
        service_heading = f"# :quicksilver: {day} | Sunday Service"
        notes_heading = f"## :calendar: Sunday Debrief + Planning Meeting Notes"
        feedback_heading = f"## :whoa: Feedback"
        changes = [
            {
                "operation": "insert_at_start",
                "document_content": {
                    "type": "markdown",
                    "markdown": f"{service_heading}\n{notes_heading}\n{feedback_heading}",
                },
            }
        ]
        res = client.canvases_edit(
            canvas_id=canvas_id,
            changes=changes,
        )
        logging.info(f"Updated canvas: {res}")
    except Exception as e:
        logging.error(f"Error updating canvas: {e}")


def handle_feedback_message(body):
    global feedback_threads_ts
    thread_ts = body.get("event", {}).get("thread_ts")

    # Write user feedback to Slack Canvas
    day = feedback_threads_ts[thread_ts]
    text = body.get("event", {}).get("text", None)
    if day and text:
        try:
            client = get_slack_client()
            res = client.canvases_sections_lookup(
                canvas_id=canvas_id,
                criteria={"section_types": ["h2"], "contains_text": "Feedback"},
            )
            section_id = res["sections"][0]["id"]
            logging.info(f"Found section id: {res}")

            res = client.canvases_edit(
                canvas_id=canvas_id,
                changes=[
                    {
                        "operation": "insert_after",
                        "section_id": section_id,
                        "document_content": {
                            "type": "markdown",
                            "markdown": f"* {text}",
                        },
                    }
                ],
            )
            logging.info(f"Updated canvas: {res}")
        except Exception as e:
            logging.error(f"Error updating canvas: {e}")
