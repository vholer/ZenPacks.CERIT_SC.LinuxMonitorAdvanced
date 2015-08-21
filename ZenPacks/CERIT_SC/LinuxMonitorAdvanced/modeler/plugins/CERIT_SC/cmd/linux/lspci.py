import re

from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs

class lspci(LinuxCommandPlugin):
    maptype = "ExpansionCardMap"
    modname = "ZenPacks.CERIT_SC.LinuxMonitorAdvanced.LinuxExpansionCard"
    relname = "cards"
    compname = "hw"
    command = 'PATH="$PATH:/sbin:/usr/sbin" lspci -vmmk'
    deviceProperties = LinuxCommandPlugin.deviceProperties + \
        ( 'zLinuxExpansionCardMapMatchIgnoreClasses', )

    def process(self, device, results, log):
        log.info('Collecting expansion cards for device %s' % device.id)
        skipClasses = getattr(device, 'zLinuxExpansionCardMapMatchIgnoreClasses', [])
        rm = self.relMap()

        for section in re.split(r"\n\s*\n", results.strip()):
            om = self.objectMap()
            vendor, model = ('Unknown', 'Unknown')
            modules = []

            for line in section.splitlines():
                try:
                    k,v = line.split(':', 1)
                    v = v.strip()

                    if k == 'Slot':
                        om.slot = v
                    elif k == 'Class':
                        om.cardClass = v
                    elif k == 'Vendor':
                        vendor = v
                    elif k == 'Device':
                        model = v
                    elif k == 'SVendor':
                        om.subVendor = v
                    elif k == 'SDevice':
                        om.subModel = v
                    elif k == 'PhySlot':
                        om.physicalSlot = int(v)
                    elif k == 'Rev':
                        om.revision = v
                    elif k == 'ProgIf':
                        om.progIface = v
                    elif k == 'Driver':
                        om.driver = v
                    elif k == 'Module':
                        modules.append(v)
                except ValueError:
                    continue

            om.id = self.prepId('pci_%s' % (om.slot,))
            om.title = "%s: %s %s" % (om.cardClass, vendor, model)
            om.setProductKey = MultiArgs(model, vendor)
            om.modules = modules
            om.monitor = False # we don't monitor PCI cards

            skip = False
            for regex in skipClasses:
                if re.search(regex, om.cardClass, re.I):
                    log.info("Skipping '%s' as it matches zLinuxExpansionCardMapMatchIgnoreClasses.", \
                        om.title)
                    skip = True
                    break

            if not skip:
                rm.append(om)

        return rm
