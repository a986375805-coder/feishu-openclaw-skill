#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu API CLI — direct Feishu Open API client for the opencode skill.

Zero third-party dependencies (stdlib only). Credentials are read from
environment variables FEISHU_APP_ID and FEISHU_APP_SECRET, or from a
credentials file (see README). Never hardcode secrets here.

Subcommands:
  token                     get a tenant_access_token
  send-text RECEIVE_ID      send a text message (receive_id_type=chat_id)
  send-post RECEIVE_ID      send a rich-text (post) message
  read-messages CHAT_ID     list recent messages of a chat
  fetch-resource MESSAGE_ID FILE_KEY TYPE [OUT]
                            download an image/file resource from a message
  bitable-list APP_TOKEN TABLE_ID
                            list records of a bitable table
  bitable-search APP_TOKEN TABLE_ID FILTER_JSON
                            search records with a filter expression
  bitable-create APP_TOKEN TABLE_ID FIELDS_JSON
                            create a record
  bitable-update APP_TOKEN TABLE_ID RECORD_ID FIELDS_JSON
                            update a record
  bitable-delete APP_TOKEN TABLE_ID RECORD_ID
                            delete a record
  calendar-list [RANGE]     list events on the primary calendar
                            RANGE=start,end (ISO-8601 or epoch seconds)
  calendar-create SUMMARY START END [DESCRIPTION]
                            create an event on the primary calendar
  task-create SUMMARY [DUE] create a task
  task-list [pending|done]  list tasks (default pending)
  task-update TASK_GUID FIELDS_JSON
                            update a task (summary/completed/due...)
  doc-create TITLE          create an empty docx document
  doc-get DOC_ID            fetch a document's raw text content
  doc-append DOC_ID         append stdin lines as text blocks to a document

Notes:
  - Datetime values accept 'YYYY-MM-DDTHH:MM[:SS][+HH:MM]' or 'YYYY-MM-DD HH:MM'
    (naive values are treated as Asia/Shanghai) or raw epoch seconds.
  - Message *search* across chats needs a user_access_token (OAuth) and is not
    covered here; use the original openclaw skill (feishu-im-read) for that.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "https://open.feishu.cn"


class FeishuError(Exception):
    pass


def read_env(name):
    val = os.environ.get(name)
    if not val:
        raise FeishuError(
            f"missing environment variable {name}; set FEISHU_APP_ID / FEISHU_APP_SECRET"
        )
    return val


def get_credentials():
    cred_file = os.environ.get("FEISHU_CREDENTIALS_FILE")
    if cred_file:
        if not os.path.exists(cred_file):
            raise FeishuError(f"credentials file not found: {cred_file}")
        with open(cred_file, encoding="utf-8-sig") as f:
            cfg = json.load(f)
        app_id = cfg.get("FEISHU_APP_ID") or cfg.get("app_id")
        app_secret = cfg.get("FEISHU_APP_SECRET") or cfg.get("app_secret")
        if not app_id or not app_secret:
            raise FeishuError("credentials file missing FEISHU_APP_ID / FEISHU_APP_SECRET")
        return app_id, app_secret
    app_id = read_env("FEISHU_APP_ID")
    app_secret = read_env("FEISHU_APP_SECRET")
    return app_id, app_secret


def request(method, path, token=None, body=None, params=None):
    url = BASE_URL + path
    if params:
        from urllib.parse import urlencode

        url += "?" + urlencode(params)
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
    except urllib.error.URLError as e:
        raise FeishuError(f"network error: {e}")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise FeishuError(f"non-JSON response: {raw[:500]}")
    code = payload.get("code")
    if code not in (0, None):
        msg = payload.get("msg") or payload.get("error") or "unknown error"
        raise FeishuError(f"feishu error code={code} msg={msg} url={path}")
    return payload.get("data", payload)


def get_token():
    app_id, app_secret = get_credentials()
    data = request(
        "POST",
        "/open-apis/auth/v3/tenant_access_token/internal",
        body={"app_id": app_id, "app_secret": app_secret},
    )
    token = data.get("tenant_access_token")
    if not token:
        raise FeishuError("no tenant_access_token in response")
    return token


def cmd_token():
    token = get_token()
    print(json.dumps({"ok": True, "tenant_access_token": token[:8] + "..."}))


def build_text_content(text):
    return json.dumps({"text": text}, ensure_ascii=False)


def build_post_content(title, lines):
    """lines: list of str or list of [str, str] (tag, text)."""
    content = []
    for item in lines:
        if isinstance(item, str):
            content.append([{"tag": "text", "text": item}])
        else:
            tag, text = item
            content.append([{"tag": tag, "text": text}])
    return json.dumps(
        {"zh_cn": {"title": title, "content": content}}, ensure_ascii=False
    )


def send_message(token, receive_id, msg_type, content, receive_id_type="chat_id"):
    data = request(
        "POST",
        "/open-apis/im/v1/messages",
        token=token,
        params={"receive_id_type": receive_id_type},
        body={
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content,
        },
    )
    return data


def cmd_send_text(receive_id):
    text = sys.stdin.read().strip()
    if not text:
        raise FeishuError("no text on stdin")
    token = get_token()
    data = send_message(token, receive_id, "text", build_text_content(text))
    print(
        json.dumps(
            {
                "ok": True,
                "message_id": data.get("message_id"),
                "chat_id": data.get("chat_id"),
            },
            ensure_ascii=False,
        )
    )


def cmd_send_post(receive_id, title):
    lines = [ln for ln in (l.rstrip("\n") for l in sys.stdin) if ln.strip()]
    if not lines:
        raise FeishuError("no content on stdin")
    token = get_token()
    data = send_message(token, receive_id, "post", build_post_content(title, lines))
    print(
        json.dumps(
            {
                "ok": True,
                "message_id": data.get("message_id"),
                "chat_id": data.get("chat_id"),
            },
            ensure_ascii=False,
        )
    )


def cmd_read_messages(chat_id):
    token = get_token()
    data = request(
        "GET",
        "/open-apis/im/v1/messages",
        token=token,
        params={"container_id_type": "chat", "container_id": chat_id, "page_size": 20},
    )
    items = []
    for msg in data.get("items", []):
        items.append(
            {
                "message_id": msg.get("message_id"),
                "msg_type": msg.get("msg_type"),
                "create_time": msg.get("create_time"),
                "sender": (msg.get("sender") or {}).get("id") or (
                    msg.get("sender") or {}
                ).get("sender_type"),
                "body": json.loads(msg.get("body") or "{}"),
            }
        )
    print(json.dumps({"ok": True, "items": items}, ensure_ascii=False, indent=2))


def bitable_request(token, app_token, table_id, action, method, body=None):
    path = f"/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{action}"
    path = path.rstrip("/")
    return request(method, path, token=token, body=body)


def cmd_bitable_list(app_token, table_id):
    token = get_token()
    data = bitable_request(token, app_token, table_id, "search", "POST", body={"page_size": 50})
    print(json.dumps({"ok": True, "total": data.get("total"), "items": data.get("items")}, ensure_ascii=False, indent=2))


def cmd_bitable_search(app_token, table_id, filter_json):
    token = get_token()
    flt = json.loads(filter_json)
    body = {"page_size": 50, "filter": flt}
    data = bitable_request(token, app_token, table_id, "search", "POST", body=body)
    print(json.dumps({"ok": True, "total": data.get("total"), "items": data.get("items")}, ensure_ascii=False, indent=2))


def cmd_bitable_create(app_token, table_id, fields_json):
    token = get_token()
    fields = json.loads(fields_json)
    data = bitable_request(token, app_token, table_id, "", "POST", body={"fields": fields})
    print(json.dumps({"ok": True, "record": data.get("record")}, ensure_ascii=False, indent=2))


def cmd_bitable_update(app_token, table_id, record_id, fields_json):
    token = get_token()
    fields = json.loads(fields_json)
    data = bitable_request(token, app_token, table_id, record_id, "PUT", body={"fields": fields})
    print(json.dumps({"ok": True, "record": data.get("record")}, ensure_ascii=False, indent=2))


def cmd_bitable_delete(app_token, table_id, record_id):
    token = get_token()
    bitable_request(token, app_token, table_id, record_id, "DELETE")
    print(json.dumps({"ok": True, "record_id": record_id}))


def parse_dt(value):
    """Parse ISO-8601-ish datetime or epoch seconds into epoch seconds string."""
    value = value.strip().strip('"')
    if value.replace("-", "").isdigit():
        return value
    try:
        from datetime import datetime, timedelta, timezone

        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=8)))
        return str(int(dt.timestamp()))
    except ValueError:
        raise FeishuError(f"cannot parse datetime: {value}")


def cmd_fetch_resource(message_id, file_key, rtype="file", out=None):
    url = (
        f"{BASE_URL}/open-apis/im/v1/messages/{message_id}/resources/{file_key}"
        f"?type={rtype}"
    )
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + get_token()})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            binary = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8")[:500]
        raise FeishuError(f"download failed http={e.code} body={detail}")
    out = out or file_key
    with open(out, "wb") as fh:
        fh.write(binary)
    print(json.dumps({"ok": True, "file": out, "bytes": len(binary)}, ensure_ascii=False))


def cmd_calendar_list(events_range=None):
    params = {"page_size": 50}
    if events_range:
        parts = [p.strip() for p in events_range.split(",")]
        if len(parts) == 2:
            params["start_time"] = parse_dt(parts[0])
            params["end_time"] = parse_dt(parts[1])
    data = request(
        "GET", "/open-apis/calendar/v4/calendars/primary/events", token=get_token(), params=params
    )
    items = []
    for ev in data.get("items", []):
        items.append(
            {
                "event_id": ev.get("event_id"),
                "summary": ev.get("summary"),
                "start": (ev.get("start_time") or {}).get("timestamp"),
                "end": (ev.get("end_time") or {}).get("timestamp"),
                "url": ev.get("url"),
            }
        )
    print(json.dumps({"ok": True, "items": items}, ensure_ascii=False, indent=2))


def cmd_calendar_create(summary, start, end, description=None):
    body = {
        "summary": summary,
        "start_time": {"timestamp": parse_dt(start)},
        "end_time": {"timestamp": parse_dt(end)},
    }
    if description:
        body["description"] = description
    ev = request(
        "POST",
        "/open-apis/calendar/v4/calendars/primary/events",
        token=get_token(),
        body=body,
    ).get("event") or {}
    print(
        json.dumps(
            {
                "ok": True,
                "event_id": ev.get("event_id"),
                "url": ev.get("url"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_task_create(summary, due=None):
    body = {"summary": summary}
    if due:
        body["due"] = {"timestamp": parse_dt(due)}
    task = request("POST", "/open-apis/task/v2/tasks", token=get_token(), body=body).get(
        "task"
    ) or {}
    print(
        json.dumps(
            {
                "ok": True,
                "task_guid": task.get("guid"),
                "summary": task.get("summary"),
                "url": task.get("url"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_task_list(completed=False):
    params = {"page_size": 50, "completed": "true" if completed else "false"}
    data = request("GET", "/open-apis/task/v2/tasks", token=get_token(), params=params)
    items = []
    for task in data.get("items", []):
        items.append(
            {
                "task_guid": task.get("guid"),
                "summary": task.get("summary"),
                "completed": task.get("completed"),
                "due": (task.get("due") or {}).get("timestamp"),
            }
        )
    print(json.dumps({"ok": True, "items": items}, ensure_ascii=False, indent=2))


def cmd_task_update(guid, fields_json):
    fields = json.loads(fields_json)
    if "due" in fields and not isinstance(fields["due"], dict):
        fields["due"] = {"timestamp": parse_dt(fields["due"])}
    fields["update_fields"] = list(fields.keys())
    task = request(
        "PATCH", f"/open-apis/task/v2/tasks/{guid}", token=get_token(), body=fields
    ).get("task") or {}
    print(
        json.dumps(
            {
                "ok": True,
                "task_guid": task.get("guid"),
                "summary": task.get("summary"),
                "completed": task.get("completed"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_doc_create(title):
    doc = request(
        "POST", "/open-apis/docx/v1/documents", token=get_token(), body={"title": title}
    ).get("document") or {}
    print(
        json.dumps(
            {
                "ok": True,
                "document_id": doc.get("document_id"),
                "title": doc.get("title"),
                "url": doc.get("url"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_doc_get(document_id):
    doc = request(
        "GET",
        f"/open-apis/docx/v1/documents/{document_id}/raw_content",
        token=get_token(),
    ).get("document") or {}
    print(json.dumps({"ok": True, "content": doc.get("content", "")}, ensure_ascii=False, indent=2))


def cmd_doc_append(document_id):
    text = sys.stdin.read()
    lines = [ln for ln in (l.rstrip("\n") for l in text.split("\n")) if ln.strip()]
    if not lines:
        raise FeishuError("no non-empty text on stdin")
    children = [
        {"block_type": 2, "text": {"elements": [{"text_run": {"content": ln}}]}}
        for ln in lines
    ]
    data = request(
        "POST",
        f"/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children",
        token=get_token(),
        body={"children": children},
    )
    print(
        json.dumps(
            {"ok": True, "children": data.get("children", [])}, ensure_ascii=False, indent=2
        )
    )


def usage():
    print(__doc__)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        usage()
    cmd = args[0]
    try:
        if cmd == "token":
            cmd_token()
        elif cmd == "send-text" and len(args) >= 2:
            cmd_send_text(args[1])
        elif cmd == "send-post" and len(args) >= 3:
            cmd_send_post(args[1], args[2])
        elif cmd == "read-messages" and len(args) >= 2:
            cmd_read_messages(args[1])
        elif cmd == "fetch-resource" and len(args) >= 4:
            cmd_fetch_resource(args[1], args[2], args[3], args[4] if len(args) >= 5 else None)
        elif cmd == "calendar-list":
            cmd_calendar_list(args[1] if len(args) >= 2 else None)
        elif cmd == "calendar-create" and len(args) >= 4:
            cmd_calendar_create(args[1], args[2], args[3], args[4] if len(args) >= 5 else None)
        elif cmd == "task-create" and len(args) >= 2:
            cmd_task_create(args[1], args[2] if len(args) >= 3 else None)
        elif cmd == "task-list":
            cmd_task_list(args[1] == "done" if len(args) >= 2 else False)
        elif cmd == "task-update" and len(args) >= 3:
            cmd_task_update(args[1], args[2])
        elif cmd == "doc-create" and len(args) >= 2:
            cmd_doc_create(args[1])
        elif cmd == "doc-get" and len(args) >= 2:
            cmd_doc_get(args[1])
        elif cmd == "doc-append" and len(args) >= 2:
            cmd_doc_append(args[1])
        elif cmd == "bitable-list" and len(args) >= 3:
            cmd_bitable_list(args[1], args[2])
        elif cmd == "bitable-search" and len(args) >= 4:
            cmd_bitable_search(args[1], args[2], args[3])
        elif cmd == "bitable-create" and len(args) >= 4:
            cmd_bitable_create(args[1], args[2], args[3])
        elif cmd == "bitable-update" and len(args) >= 5:
            cmd_bitable_update(args[1], args[2], args[3], args[4])
        elif cmd == "bitable-delete" and len(args) >= 4:
            cmd_bitable_delete(args[1], args[2], args[3])
        else:
            usage()
    except FeishuError as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
