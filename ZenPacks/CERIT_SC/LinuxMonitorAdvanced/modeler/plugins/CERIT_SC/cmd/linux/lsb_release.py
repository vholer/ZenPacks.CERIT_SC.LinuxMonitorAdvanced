from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin

class lsb_release(CommandPlugin):
    maptype = "DeviceMap"
    compname = ""
    command = 'lsb_release -sir'
    oses = ['Linux']

    def condition(self, device, log):
        return device.os.uname == '' or device.os.uname in self.oses

    def process(self, device, results, log):
        log.info("Processing the LSB release info for device %s" % device.id)
        om = self.objectMap()
        om.setOSProductKey = ' '.join(results.strip().split())
        log.debug("setOSProductKey=%s" % (om.setOSProductKey))
        return om
