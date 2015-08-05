import re
from Products.ZenRRD.CommandParser import CommandParser

class key_value(CommandParser):
    def processResults(self, cmd, result):
        if cmd.result.output:
            datapointMap = dict([(dp.id, dp) for dp in cmd.points])
            for line in cmd.result.output.splitlines():
                key,value = re.split(r'\s*[:=\s]\s*', line.strip())
                if datapointMap.has_key(key):
                    result.values.append((datapointMap[key], long(value)))

        return result
