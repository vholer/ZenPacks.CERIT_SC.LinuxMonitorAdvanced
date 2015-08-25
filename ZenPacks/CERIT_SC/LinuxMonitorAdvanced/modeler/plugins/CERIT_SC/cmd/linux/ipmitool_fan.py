import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class ipmitool_fan(LinuxCommandPlugin):
    maptype = "FanMap"
    modname = "Products.ZenModel.Fan"
    relname = "fans"
    compname = "hw"
    command = '''\
if which ipmitool >/dev/null 2>&1; then
    sudo -n ipmitool sdr dump cache.sdr >/dev/null 2>&1
    sudo -n ipmitool -S cache.sdr sdr type fan 2>/dev/null
fi
    '''

    def process(self, device, results, log):
        log.info('Collecting fans for device %s' % device.id)
        rm = self.relMap()

        if results:
            for line in results.splitlines():
                 (name, idx, status, entity, value) = \
                    [ v.strip() for v in line.split('|', 4) ]

                 match = re.search('^(\d+) RPM$', value)
                 if match:
                    om = self.objectMap()
                    om.id = self.prepId(name)
                    om.name = name
                    om.snmpindex = int(idx.rstrip('h'), 16)
                    om.state = status
                    om.type = entity #TODO?
                    rm.append(om)

        return rm
