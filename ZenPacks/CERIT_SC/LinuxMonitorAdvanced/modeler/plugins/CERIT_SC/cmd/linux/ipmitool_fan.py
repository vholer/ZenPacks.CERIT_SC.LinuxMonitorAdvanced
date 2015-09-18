import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from ZenPacks.CERIT_SC.LinuxMonitorAdvanced.lib.IPMISensorsCommandPlugin import IPMISensorsCommandPlugin

class ipmitool_fan(IPMISensorsCommandPlugin):
    maptype = "FanMap"
    modname = "Products.ZenModel.Fan"
    relname = "fans"
    compname = "hw"
    command = '''\
if which ipmitool >/dev/null 2>&1 && ( test -c /dev/ipmi0 || test -c /dev/ipmi/0 || test -c /dev/ipmidev/0 ); then
    test -f cache.sdr || sudo -n ipmitool -v sdr dump cache.sdr >/dev/null 2>&1
    sudo -n ipmitool -S cache.sdr -v sdr type fan 2>/dev/null
fi
    '''

    def process(self, device, results, log):
        log.info('Collecting fans for device %s' % device.id)
        rm = self.relMap()

        for sensor in results.values():
            if (sensor.get('type') == 'Fan') and \
                    (sensor.get('units') in ('RPM', 'unspecified')) and \
                    (sensor.get('dataType') == 'analog') and \
                    (sensor.get('name')):

                # with unspecified units we expect percentage
                if sensor['units'] == 'unspecified':
                    try:
                        value = float(sensor.get('value', ''))
                        if (value <= 0) or (value >= 100):
                            continue
                    except ValueError:
                        continue

                om = self.objectMap()
                om.id = self.prepId(sensor['name'])
                om.name = sensor['name']
                #om.snmpindex = int(sensor['id'], 16)
                om.snmpindex = sensor['id'].upper()
                om.state = sensor.get('state', 'Unknown')
                om.type = sensor.get('entity', sensor.get('entityId', 'Unknown'))
                rm.append(om)

        return rm
