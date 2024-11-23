feedback_threads_ts = {}


def feedback_handle_message(body):
    global feedback_threads_ts
    thread_ts = body.get("thread_ts", None)

    if not thread_ts:
        feedback_threads_ts = body["ts"]
        return
