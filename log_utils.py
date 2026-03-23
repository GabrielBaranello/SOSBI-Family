import os
import json
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), 'log.json')


def _load():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return { 'messages': [] }
    return { 'messages': [] }


def _save(data):
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_log(message, typ='info'):
    data = _load()
    if isinstance(data, dict) and 'messages' in data and isinstance(data['messages'], list):
        messages = data['messages']
    elif isinstance(data, list):
        messages = data
        data = { 'messages': messages }
    else:
        messages = []
        data = { 'messages': messages }

    entry = {
        'id': int(datetime.utcnow().timestamp()),
        'type': typ,
        'message': message,
        'ts': datetime.utcnow().isoformat() + 'Z'
    }
    messages.append(entry)
    _save(data)
    return entry


def read_logs():
    data = _load()
    return data.get('messages', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])


def append_entry(entry: dict):
    data = _load()
    if isinstance(data, dict) and 'messages' in data:
        data['messages'].append(entry)
    elif isinstance(data, list):
        data.append(entry)
        data = { 'messages': data }
    else:
        data = { 'messages': [entry] }
    _save(data)
    return entry
