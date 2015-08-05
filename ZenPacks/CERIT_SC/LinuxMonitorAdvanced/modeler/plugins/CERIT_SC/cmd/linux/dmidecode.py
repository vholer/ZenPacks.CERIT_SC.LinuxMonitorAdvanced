import re
from ZenPacks.CERIT_SC.LinuxMonitorAdvanced.lib.DMICommandPlugin import DMICommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class dmidecode(DMICommandPlugin):
    maptype  = "DeviceMap" 
    compname = ""
    command  = 'sudo -n /usr/sbin/dmidecode --type 1,3'

    def check_sn(self, v):
        return (not v in (None,'','Not Specified') and \
            v.find('O.E.M.')<0 and \
            v.find('123456')<0)

    def process(self, device, results, log):
        """Collect command-line information from this device"""
        log.info("Processing the dmidecode info for device %s" % device.id)

        sys=[results[x]['data'] for x in results if results[x]['type'] == '1']
        chs=[results[x]['data'] for x in results if results[x]['type'] == '3']

        om=self.objectMap()

        if sys:
            # set only valid S/N
            sn=sys[0].get('Serial Number',None)
            if self.check_sn(sn):
                om.setHWSerialNumber=sn
                log.debug("setHWSerialNumber=%s" % (om.setHWSerialNumber))

            # set only valid Tag
            tag=sys[0].get('SKU Number',None)
            if self.check_sn(tag):
                om.setHWTag=tag
                log.debug("setHWTag=%s" % (om.setHWTag))

            # normalize product name (remove part number?)
            product=sys[0].get('Product Name','None')
            if product:
                # IBM: "PRODUCT -[SKU]-"
                result=re.match('^(.+)\s+-\[(.+)\]-$',product)
                if result:
                    product=result.group(1)
                    om.setHWTag=result.group(2)

            om.setHWProductKey=MultiArgs(
                product,
                sys[0].get('Manufacturer',None))

            log.debug("setHWProductKey=%s" % (om.setHWProductKey))

        if chs:
            # chassis rack slot
            height=chs[0].get('Height',None)
            if height:
                result=re.match('^(\d+) U$',height)
                if result: # and not device.rackSlot: #TODO: don't overwrite rackslot
                    om.rackSlot='rh=%s' % (result.group(1))
                    log.debug("rackSlot=%s" % (om.rackSlot))

        return om
