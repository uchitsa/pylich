import json5
from jsonschema import validate, ValidationError, SchemaError


class Config:
    def __init__(self, include, exclude=None, license=None):
        self.include = include
        self.exclude = exclude or []
        self.license = license


def parse_config(text: str) -> Config:
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["include"],
            "properties": {
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "exclude": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "license": {
                    "type": "string"
                }
            }
        }
    }

    try:
        data = json5.loads(text)
    except json5.JSON5DecodeError:
        raise ValueError("Parsing configuration has failed")

    try:
        validate(instance=data, schema=schema)
    except (ValidationError, SchemaError) as e:
        raise ValueError(f"Configuration validation has failed: {str(e)}")

    # Assuming the first item in the data list is the configuration we want
    config_data = data[0]
    return Config(**config_data)

# Example usage:
# config_text = '[{"include": ["**/*.js", "**/*.ts"], "exclude": ["**/node_modules/**", "**/dist/**"], "license": "MIT"}]'
# config = parse_config(config_text)
# print(config.include)
# print(config.exclude)
# print(config.license)
