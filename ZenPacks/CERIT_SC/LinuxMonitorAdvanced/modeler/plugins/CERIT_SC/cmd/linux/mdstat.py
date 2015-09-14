import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from ZenPacks.CERIT_SC.LinuxMonitorAdvanced.lib.parse import parse_mdstat

class mdstat(LinuxCommandPlugin):
    #maptype = "LinuxSWLogicalDiskMap"
    modname = "ZenPacks.CERIT_SC.LinuxMonitorAdvanced.LinuxSWLogicalDisk"
    relname = "linuxSWLogicalDisks"
    #compname = "hw"
    command = 'test -f /proc/mdstat && cat /proc/mdstat'

    def process(self, device, results, log):
        log.info('Collecting logical disks (MD) for device %s' % device.id)
        rm = self.relMap()
        for device in parse_mdstat(results):
            om = self.objectMap()
            om.id = self.prepId('md%s' % device['id'])
            om.description = '/dev/md%s' % device['id']
            om.hostresindex = int(device['id'])
            om.diskType = device['type']
            om.size = device.get('blocks', 0)
            om.stripesize = device.get('stripesize', 0)
            rm.append(om)
        return rm

#        for line in results.splitlines():
#            match = re.search('^md(?P<id>\d+)\s*:', line)
#            if match:
#                om = self.objectMap()
#                om.id = self.prepId('md%s' % match.group('id'))
#                om.description = '/dev/md%s' % match.group('id')
#                om.hostresindex = int(match.group('id'))
#                rm.append(om)
#        return rm
