import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class ipmitool_temp(LinuxCommandPlugin):
    maptype = "TemperatureSensorMap"
    modname = "Products.ZenModel.TemperatureSensor"
    relname = "temperaturesensors"
    compname = "hw"
    command = '''\
if which ipmitool >/dev/null 2>&1; then
    if [ `stat --format=%Y cache.sdr` -le $(( `date +%s` - 600 )) ]; then 
        if [ -f cache.sdr.lock ]; then
            # remove stale lockfile
            if [ `stat --format=%Y cache.sdr.lock` -le $(( `date +%s` - 600 )) ]; then 
                unlink cache.sdr.lock
            fi
        else
            # lock and proceed with sdr dump
            echo $$ >cache.sdr.lock
            if grep -Fqx $$ cache.sdr.lock; then
                sudo -n ipmitool sdr dump cache.sdr >/dev/null 2>&1
                unlink cache.sdr.lock
            else
                #TODO: wait for sdr dump
                :
            fi
        fi
    fi

    sudo -n ipmitool -S cache.sdr sdr type temperature 2>/dev/null
fi
    '''

    def process(self, device, results, log):
        log.info('Collecting temperature sensors for device %s' % device.id)
        rm = self.relMap()

        if results:
            for line in results.splitlines():
                 (name, idx, status, entity, value) = \
                    [ v.strip() for v in line.split('|', 4) ]

                 match = re.search('^(\d+) degrees C$', value)
                 if match:
                    om = self.objectMap()
                    om.id = self.prepId(name)
                    om.name = name
                    om.snmpindex = int(idx.rstrip('h'), 16)
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
