from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from ZenPacks.CERIT_SC.LinuxMonitorAdvanced.lib.IPMISensorsCommandPlugin import IPMISensorsCommandPlugin

class ipmitool_temp(IPMISensorsCommandPlugin):
    maptype = "TemperatureSensorMap"
    #modname = "Products.ZenModel.TemperatureSensor"
    modname = "ZenPacks.CERIT_SC.LinuxMonitorAdvanced.IPMITemperatureSensor"
    relname = "temperaturesensors"
    compname = "hw"
    command = '''\
if which ipmitool >/dev/null 2>&1 && ( test -c /dev/ipmi0 || test -c /dev/ipmi/0 || test -c /dev/ipmidev/0 ); then
    test -f cache.sdr || sudo -n ipmitool -v sdr dump cache.sdr >/dev/null 2>&1
    SDR=$(sudo -n ipmitool -S cache.sdr -v sdr type temperature 2>/dev/null)
    echo "${SDR}" | egrep -qi '(Upper|Lower) (non-)?(critical|recoverable)' &&
        echo "${SDR}" ||
        sudo -n ipmitool -v sensor list 2>/dev/null
fi
    '''

    def process(self, device, results, log):
        log.info('Collecting temperature sensors for device %s' % device.id)
        rm = self.relMap()

        for sensor in results.values():
            if (sensor.get('type') == 'Temperature') and \
                    (sensor.get('units') == 'degrees C') and \
                    (sensor.get('dataType') == 'analog') and \
                    (sensor.get('name')):
                om = self.objectMap()
                om.id = self.prepId(sensor['name'])
                om.name = sensor['name']
                #om.snmpindex = int(sensor['id'], 16)
                om.snmpindex = sensor['id'].upper()
                om.entity = sensor.get('entity', sensor.get('entityId', 'unknown'))
                om.state = sensor.get('state', 'Unknown')

                # thresholds
                for t in ('lowerNC', 'lowerC', 'lowerNR',
                          'upperNC', 'upperC', 'upperNR'):
                    try:
                        setattr(om, t, float(sensor.get(t)))
                    except:
                        setattr(om, t, None)

                rm.append(om)

        return rm
