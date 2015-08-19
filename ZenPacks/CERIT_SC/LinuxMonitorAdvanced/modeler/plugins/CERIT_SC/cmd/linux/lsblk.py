import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class lsblk(LinuxCommandPlugin):
    maptype = "HardDiskMap"
    modname = "Products.ZenModel.HardDisk"
    relname = "harddisks"
    compname = "hw"
    command = '''
        PARAMS_BASE='NAME,RM,SIZE,RO,TYPE,MODEL'
        PARAMS_MORE='VENDOR,SERIAL,REV,TRAN'

        if which lsblk >/dev/null 2>&1; then
            lsblk -P -b -d -o "${PARAMS_BASE},${PARAMS_MORE}" 2>/dev/null || \
                lsblk -P -b -d -o "${PARAMS_BASE}" 
        fi
    '''

    deviceProperties = LinuxCommandPlugin.deviceProperties + \
        ('zHardDiskMapMatch',)

    pattern = re.compile('^(?P<key>\w+)="(?P<value>.*)"?$')

    def process(self, device, results, log):
        log.info('Collecting hard disks for device %s' % device.id)
        rm = self.relMap()
        diskmatch = re.compile(getattr(device, 'zHardDiskMapMatch', '^$')) #TODO
        for line in results.splitlines():
            om = self.objectMap()
            vendor, model = ('Unknown', 'Unknown')

            for param in line.split('" '): #TODO: LAME!
                match=self.pattern.match(param)
                k,v = match.group('key'), match.group('value')
                if k == 'NAME':
                    om.id = self.prepId(v)
                    om.description = '/dev'+v
                elif k == 'SERIAL':
                    om.serialNumber = v
                elif k == 'MODEL':
                    model = v
                elif k == 'VENDOR':
                    vendor = v

            om.setProductKey = MultiArgs(model, vendor)
            rm.append(om)

        return rm



#
#        # process all data in format:
#        # /sys/block/vda/size:20971520
#        #            ^^^ ^^^^ ^^^^^^^^
#        #            dev  key   value
#        data={}
#        for line in results.splitlines():
#            match=self.pattern.match(line)
#            if match:
#                k,v = match.group('key'), match.group('value')
#                if not data.has_key(match.group('dev')):
#                    data[match.group('dev')]={}
#                data[match.group('dev')][k]=v
#
#        rm = self.relMap()
#        diskmatch = re.compile(getattr(device, 'zHardDiskMapMatch', '^$'))
#        for dev in data.keys():
#            fixDev=dev.replace('!','/')
#            fullDev='/dev/'+fixDev
#            if not diskmatch.search(fixDev): continue
#
#            om = self.objectMap()
#            om.id = self.prepId(fixDev)
#            om.description = fullDev #TODO
#            om.setProductKey = MultiArgs(
#                data[dev].get('device/model','hard disk'),
#                data[dev].get('device/vendor','Unknown'))
#            rm.append(om)
#        return rm
