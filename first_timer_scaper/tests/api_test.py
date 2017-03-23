import jsonschema
import os
import json
import sys

if len(sys.argv) == 1:
    def choose_schema(schema):
        return True
else:
    valid_schemas = sys.argv[1:]
    def choose_schema(schema):
        return schema in valid_schemas

HERE = os.path.dirname(__file__)
files = os.listdir(HERE)
files.sort()

checker = jsonschema.FormatChecker(("date-time",))

def schema_works(schema, instance):
    jsonschema.validate(instance, schema, format_checker=checker)

def schema_fails(schema, instance):
    try:
        jsonschema.validate(instance, schema, format_checker=checker)
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
    for file in files:
        if file.startswith("schema_" + name + "_works"):
            validate = schema_works
            tested_works = True
        elif file.startswith("schema_" + name + "_fails"):
            validate = schema_fails
            tested_fails = True
        else:
            continue
        instance = load_json_from_file(file)
        new_schema_calls()
        try:
            validate(schema, instance)
        except:
            print("file:", file)
            print("schema:", schema)
            print("instance:", instance)
            print("checkers:", checker.checkers)
            for call in schema_calls:
                print(*call)
            raise
        else:
            print(message, "| ok", file)
    assert tested_fails, "schema " + name + " did not test invalid example"
    assert tested_fails, "schema " + name + " did not test valid example"

#
# Load all `schema_xxx.json` files:
# - add a global variable `SCHEMA_XXX`
# - add a format `xxx`
#

schema_calls = []
def new_schema_calls():
    global schema_calls
    schema_calls = []

def define_schema(name, schema):
    print("Loading schema", name)
    @checker.checks(name, (jsonschema.exceptions.ValidationError, ))
    def check_schema(obj):
        schema_calls.append(("SCHEMA", name, "called with", obj))
        schema_works(schema, obj)
        return True
    globals()["SCHEMA_" + name.upper()] = schema

def execute_tests(name, schema):
    test_schema(name, schema, name + " as schema")
    test_schema(name, {"format" : name}, name + " as format")

SCHEMA_PREFIX = "schema_"
for action in [define_schema, execute_tests]:
    for file in files:
        if file.startswith(SCHEMA_PREFIX) and not "_fails" in file and not "_works" in file:
            name = os.path.splitext(file)[0][len(SCHEMA_PREFIX):]
            schema = load_json_from_file(file)
            if choose_schema(name) or action == define_schema:
                action(name, schema)
            else:
                print("SKIP", name)
        del file




