import jsonpickle

import agents


class ScriptEngine:

    def execute(self, script):
        ops = jsonpickle.decode(script)
        agent = agents.Agent()
        results = []
        for op in ops:
            results.append(agent.handle(op))
        return results
