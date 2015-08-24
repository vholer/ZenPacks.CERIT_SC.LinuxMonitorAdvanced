from Products.ZenRRD.CommandParser import CommandParser

class who(CommandParser):
    def processResults(self, cmd, result):
        if cmd.result.output:
            valueMap = { 'total': 0 }

            # process command output
            for line in cmd.result.output.splitlines():
                (login, r) = line.split(' ', 1)
                if login:
                    valueMap['total'] += 1
                    key = 'user_%s' % (login,)
                    if valueMap.has_key(key):
                        valueMap[key] += 1
                    else:
                        valueMap[key] = 1

            # process values
            datapointMap = dict([(dp.id, dp) for dp in cmd.points])
            for id in valueMap:
                if datapointMap.has_key(id):
                    result.values.append((datapointMap[id], long(valueMap[id])))

        return result
