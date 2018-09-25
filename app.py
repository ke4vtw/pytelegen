import fileinput
import json

import jsonpickle

import scriptEngine

script = ''

for line in fileinput.input():
    script = script + line + '\n'

engine = scriptEngine.ScriptEngine()
output = engine.execute(script)
print json.dumps(json.loads(jsonpickle.encode(output)), indent=4)
