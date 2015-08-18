import re
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class lsb_release(CommandPlugin):
    maptype = "DeviceMap"
    compname = ""
    command = 'lsb_release -id'
    oses = ['Linux']

    def condition(self, device, log):
        return device.os.uname == '' or device.os.uname in self.oses

    def process(self, device, results, log):
        log.info("Processing the LSB release info for device %s" % device.id)
        vendor, model = ('Unknown', 'Unknown') 

        for line in results.splitlines():
            k,v = line.split(':', 1)
            v = v.strip()

            if k == 'Distributor ID':
                if re.search('^Red\s*Hat', v, re.IGNORECASE):
                    vendor = 'RedHat'
                elif re.search('^SUSE', v, re.IGNORECASE):
                    vendor = 'SUSE'
                else:
                    vendor = v
            elif k == 'Description':
                model = v

        om = self.objectMap()
        om.setOSProductKey = MultiArgs(model, vendor)
        log.debug("setOSProductKey=%s" % (om.setOSProductKey))
        return om
