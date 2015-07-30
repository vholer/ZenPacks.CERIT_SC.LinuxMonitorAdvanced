from Products.ZenRRD.CommandParser import CommandParser

class stat(CommandParser):
    def processResults(self, cmd, result):
        if cmd.result.output:
            valueMap = dict()

            for l in cmd.result.output.splitlines():
                e = l.split()
                if len(e) > 1:
                    if e[0] == 'cpu':
                        ids = ('ssCpuUser', 'ssCpuNice', 'ssCpuSystem',
                               'ssCpuIdle', 'ssCpuWait', 'ssCpuInterrupt',
                               'ssCpuSoftInterrupt', 'ssCpuSteal',
                               'ssCpuGuest', 'ssCpuGuestNice')
                        valueMap.update(dict(zip(ids, e[1:])))
                    elif e[0] == 'ctxt':
                        valueMap['ssCtxt'] = e[1]
                    elif e[0] == 'processes':
                        valueMap['ssProcsNew'] = e[1]
                    elif e[0] == 'procs_running':
                        valueMap['ssProcsRunning'] = e[1]
                    elif e[0] == 'procs_blocked':
                        valueMap['ssProcsBlocked'] = e[1]

            # process values
            datapointMap = dict([(dp.id, dp) for dp in cmd.points])
            for id in valueMap:
                if datapointMap.has_key(id):
                    result.values.append((datapointMap[id], long(valueMap[id])))

        return result
