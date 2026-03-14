import os
import json

STATE_PATH = os.path.join(os.path.dirname(__file__), 'state.json')


def _load():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def _save(data):
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_state():
    return _load()


def write_state(updates: dict):
    data = _load()
    data.update(updates)
    _save(data)
    return data


def set_field(key, value):
    data = _load()
    data[key] = value
    _save(data)
    return data


def get_field(key, default=None):
    data = _load()
    return data.get(key, default)
