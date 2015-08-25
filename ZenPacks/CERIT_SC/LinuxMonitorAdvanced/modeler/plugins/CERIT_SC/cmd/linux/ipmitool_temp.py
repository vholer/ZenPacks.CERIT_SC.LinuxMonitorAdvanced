import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class ipmitool_temp(LinuxCommandPlugin):
    maptype = "TemperatureSensorMap"
    modname = "Products.ZenModel.TemperatureSensor"
    relname = "temperaturesensors"
    compname = "hw"
    command = '''\
if which ipmitool >/dev/null 2>&1; then
    sudo -n ipmitool sdr dump cache.sdr >/dev/null 2>&1
    sudo -n ipmitool -S cache.sdr sdr type temperature 2>/dev/null
fi
    '''

    def process(self, device, results, log):
        log.info('Collecting temperature sensors for device %s' % device.id)
        rm = self.relMap()

        if results:
            for line in results.splitlines():
                 (name, xxx, status, yyy, value) = \
                    [ v.strip() for v in line.split('|', 4) ]

                 match = re.search('^(\d+) degrees C$', value)
                 if match:
                    om = self.objectMap()
                    om.id = self.prepId(name)
                    om.name = name
                    om.state = status
                    rm.append(om)

#                (name, value, units, status, lnr, lc, lnc, unc, uc, unr ) = \
#                    [ v.strip() for v in line.split('|', 9) ]
#
#                if (units == 'degrees C') and (value != 'na'):
#                    om = self.objectMap()
#                    om.id = self.prepId(name)
#                    om.state = status
#                    rm.append(om)

        return rm
