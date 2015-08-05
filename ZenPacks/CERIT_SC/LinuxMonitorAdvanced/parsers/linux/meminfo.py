from Products.ZenRRD.CommandParser import CommandParser

class meminfo(CommandParser):
    def processResults(self, cmd, result):
        if cmd.result.output:
            valueMap = dict()

            # process command output
            for line in cmd.result.output.splitlines():
                key,v = line.split(':', 1)
                value = v.split() 

                if len(value) == 1:
                  valueMap[key] = int(value[0])
                elif (len(value) == 2) and (value[1] == 'kB'):
                  valueMap[key] = int(value[0]) * 1024

            # ...
            if len(set(('MemTotal','MemFree','Buffers','Cached')).intersection(valueMap)) == 4:
                valueMap['MemAllocated'] = valueMap['MemTotal'] \
                    - valueMap['MemFree'] \
                    - valueMap['Buffers'] \
                    - valueMap['Cached']

            if len(set(('SwapTotal','SwapFree')).intersection(valueMap)) == 2:
                valueMap['SwapAllocated'] = valueMap['SwapTotal'] \
                    - valueMap['SwapFree']

            # process values
            datapointMap = dict([(dp.id, dp) for dp in cmd.points])
            for id in valueMap:
                if datapointMap.has_key(id):
                    result.values.append((datapointMap[id], long(valueMap[id])))

        return result
