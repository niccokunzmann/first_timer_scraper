import jsonschema
import os
import json

HERE = os.path.dirname(__file__)

def schema_works(schema, instance):
    jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())

def schema_fails(schema, instance):
    try:
        jsonschema.validate(instance, schema, format_checker=jsonschema.FormatChecker())
        assert False, "Schema worked"
    except jsonschema.exceptions.ValidationError:
        pass
        
def load_json_from_file(file_name):
    try:
        with open(os.path.join(HERE, file_name)) as f:
            return json.load(f)
    except ValueError:
        print(file_name)
        raise

def test_schema(name, schema, message):
    """Test a schema against all files starting with `name`
    
    - name_works.json files are expected to be valid
    - name_fails.json files are expected to be invalid
    """
    tested_works = False
    tested_fails = False
    for file in os.listdir(HERE):
        if file.startswith("schema_" + name + "_works"):
            validate = schema_works
            tested_works = True
        elif file.startswith(name + "_fails"):
            validate = schema_fails
            tested_fails = True
        else:
            continue
        instance = load_json_from_file(file)
        validate(schema, instance)
        print(message, "| ok", file)
    assert tested_fails, "schema " + name + " did not test invalid example"
    assert tested_fails, "schema " + name + " did not test valid example"

@jsonschema.FormatChecker.cls_checks("name", (AssertionError, ))
def check_name(obj):
    assert isinstance(obj, str)
    assert "/" not in obj
    return True

test_schema("name", {"format":"name"}, "as format")
#
# Load all `schema_xxx.json` files:
# - add a global variable `SCHEMA_XXX`
# - add a format `xxx`
#

def define_schema(name, schema):
    @jsonschema.FormatChecker.cls_checks(name, (jsonschema.exceptions.ValidationError, ))
    def check_schema(obj):
        jsonschema.validate(obj, schema)
        return True
    globals()["SCHEMA_" + name.upper()] = schema

def execute_tests(name, schema):
    test_schema(name, schema, name + " as schema")
    test_schema(name, {"format" : name}, name + " as format")

SCHEMA_PREFIX = "schema_"
for action in [define_schema, execute_tests]:
    for file in os.listdir(HERE):
        if file.startswith(SCHEMA_PREFIX) and not "_fails" in file and not "_works" in file:
            name = os.path.splitext(file)[0][len(SCHEMA_PREFIX):]
            schema = load_json_from_file(file)
            action(name, schema)
        del file




