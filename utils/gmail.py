import base64
import html2text
import re
from datetime import datetime


def _decode_part(part_body, mime_type, content):
    try:
        decoded_data = base64.urlsafe_b64decode(part_body["data"]).decode("utf-8")

        if mime_type == "text/html":
            content.append(html2text.html2text(decoded_data))
        else:
            content.append(decoded_data)
    except Exception as e:
        print(f"Error decoding body: {e}")
    return content


def _process_parts(parts, content):
    for part in parts:
        if "parts" in part:
            _process_parts(part["parts"], content)
            continue
        if "body" in part and "data" in part["body"]:
            mime_type = part.get("mimeType", "")
            _decode_part(part["body"], mime_type, content)
    return content


def _process_content(content):
    combined_text = " ".join(content)
    combined_text = (
        combined_text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    )
    combined_text = re.sub(r"\s+", " ", combined_text)
    return combined_text.strip()


def get_email_body(payload):
    content = []
    if "parts" in payload:
        _process_parts(payload["parts"], content)
    elif "body" in payload and "data" in payload["body"]:
        mime_type = payload.get("mimeType", "")
        _decode_part(payload["body"], mime_type, content)

    if not content:
        return None

    return _process_content(content)


def _extract_email(address_field):
    email_pattern = r"[\w\.-]+@[\w\.-]+"
    match = re.search(email_pattern, address_field)
    if match:
        return match.group(0)
    return address_field


def get_required_data(message):
    payload = message["payload"]
    headers = {header["name"]: header["value"] for header in payload["headers"]}
    return {
        "message_id": message["id"],
        "received_at": datetime.fromtimestamp(
            eval(message["internalDate"]) // 1000
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "from_address": _extract_email(headers["From"]),
        "subject": headers["Subject"],
        "to_address": _extract_email(headers["To"]),
        "labels": message.get("labelIds", []),
        "body": get_email_body(payload),
        "thread_id": message["threadId"],
    }


__all__ = ["get_email_body", "get_required_data"]
