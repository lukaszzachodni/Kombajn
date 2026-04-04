import json
from jsonschema import validate, ValidationError
import os
from backend.app.modules.color_book.binding import config

def _load_schema():
    with open(config.PROJECT_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

COLORBOOK_SCHEMA = _load_schema()

def validate_project_data(data):
    try:
        validate(instance=data, schema=COLORBOOK_SCHEMA)
        return True, None
    except ValidationError as e:
        return False, e
