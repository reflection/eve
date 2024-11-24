import logging

from auth import get_google_docs_service

feedback_threads_ts = {}

doc_id = "1thssRygmLCb21lgPOZp1V-b1SpQHd5MkXKTNRxsS_9c"


def setup_feedback(thread_ts, day):
    global feedback_threads_ts
    feedback_threads_ts[thread_ts] = day
    try:
        service = get_google_docs_service()
        heading = f"{day} | Sunday Service\n"
        updates = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": heading,
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": 1, "endIndex": len(heading)},
                    "paragraphStyle": {
                        "namedStyleType": "HEADING_2",
                        "alignment": "START",
                    },
                    "fields": "namedStyleType,alignment",
                }
            },
        ]
        res = (
            service.documents()
            .batchUpdate(documentId=doc_id, body={"requests": updates})
            .execute()
        )
        logging.info(f"Updated google doc: {res}")
    except Exception as e:
        logging.error(f"Error updating google doc: {e}")


def handle_feedback_message(body, say):
    global feedback_threads_ts
    thread_ts = body.get("event", {}).get("thread_ts")

    # Write user feedback to Google Doc
    day = feedback_threads_ts[thread_ts]
    text = body.get("event", {}).get("text", None)
    if day and text:
        try:
            service = get_google_docs_service()
            heading = f"{day} | Sunday Service"

            # Find the day heading
            document = service.documents().get(documentId=doc_id).execute()

            content = document.get("body").get("content")
            heading_idx = None
            for element in content:
                if "paragraph" in element:
                    paragraph = element.get("paragraph")
                    if paragraph.get("paragraphStyle", {}).get("namedStyleType") in [
                        "HEADING_2"
                    ]:
                        elements = paragraph.get("elements")
                        for text_element in elements:
                            if (
                                text_element.get("textRun", {})
                                .get("content", "")
                                .strip()
                                == heading
                            ):
                                heading_idx = element.get("endIndex")
                                break
                if heading_idx:
                    break
            if heading_idx:
                updates = [
                    {
                        "insertText": {
                            "location": {"index": heading_idx},
                            "text": text + "\n",
                        }
                    },
                    {
                        "updateParagraphStyle": {
                            "range": {
                                "startIndex": heading_idx,
                                "endIndex": heading_idx + len(text) + 1,
                            },
                            "paragraphStyle": {
                                "namedStyleType": "NORMAL_TEXT",
                                "alignment": "START",
                            },
                            "fields": "namedStyleType,alignment",
                        }
                    },
                ]
                res = (
                    service.documents()
                    .batchUpdate(documentId=doc_id, body={"requests": updates})
                    .execute()
                )
                logging.info(f"Updated google doc: {res}")
                say("Feedback recorded and thanks!", thread_ts=thread_ts)
        except Exception as e:
            logging.error(f"Error updating google doc: {e}")
