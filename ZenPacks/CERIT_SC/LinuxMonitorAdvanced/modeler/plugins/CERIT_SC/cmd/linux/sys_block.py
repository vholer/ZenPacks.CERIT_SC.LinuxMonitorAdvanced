import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class sys_block(LinuxCommandPlugin):
    maptype = "HardDiskMap"
    modname = "Products.ZenModel.HardDisk"
    relname = "harddisks"
    compname = "hw"
    command = 'grep -s . /sys/block/*/size /sys/block/*/device/vendor /sys/block/*/device/model'
    deviceProperties = \
        LinuxCommandPlugin.deviceProperties + ('zHardDiskMapMatch',)

    pattern = re.compile('^/sys/block/(?P<dev>[^/]+)/(?P<key>[^:]+):(?P<value>.*)$')

    def process(self, device, results, log):
        log.info('Collecting hard disks for device %s' % device.id)

        # process all data in format:
        # /sys/block/vda/size:20971520
        #            ^^^ ^^^^ ^^^^^^^^
        #            dev  key   value
        data={}
        for line in results.splitlines():
            match=self.pattern.match(line)
            if match:
                k,v = match.group('key'), match.group('value')
                if not data.has_key(match.group('dev')):
                    data[match.group('dev')]={}
                data[match.group('dev')][k]=v

        rm = self.relMap()
        diskmatch = re.compile(getattr(device, 'zHardDiskMapMatch', '^$'))
        for dev in data.keys():
            fixDev=dev.replace('!','/')
            fullDev='/dev/'+fixDev
            if not diskmatch.search(fixDev): continue

            om = self.objectMap()
            om.id = self.prepId(fixDev)
            om.description = fullDev #TODO
            om.setProductKey = MultiArgs(
                data[dev].get('device/model','hard disk'),
                data[dev].get('device/vendor','Unknown'))
            rm.append(om)
        return rm
