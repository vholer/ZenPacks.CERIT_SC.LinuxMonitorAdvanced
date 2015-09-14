import logging

from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser
from ZenPacks.zenoss.LinuxMonitor.lib.parse import parse_mdstat
from pprint import pformat

log = logging.getLogger("zen.ComponentCommandParser")

class mdstat(ComponentCommandParser):
    def processResults(self, cmd, result):
        """
        Process the results of "cat /proc/mdstat".
        """
        ifs = {}
        for dp in cmd.points:
            dp.component = dp.data['componentScanValue']
            points = ifs.setdefault(dp.component, {})
            points[dp.id] = dp

        for device in parse_mdstat(cmd.result.output):
            component = self.prepId('md%s' % device['id'])
            points = ifs.get(component, None)
            if points:
                for name,value in device.items():
                    dp = points.get(name, None)
                    if dp is not None:
                        if value in ('-',''): value = 0
                        result.values.append((dp, float(value)))

        log.debug(pformat(result))
        return result
