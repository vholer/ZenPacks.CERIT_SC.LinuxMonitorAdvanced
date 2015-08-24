import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class ethtool(LinuxCommandPlugin):
    modname = "Products.ZenModel.IpInterface"
    relname = "interfaces"
    compname = "os"
    command = "egrep '^\s*\S+:' /proc/net/dev | cut -d: -f1 | xargs -n1 sudo -n /sbin/ethtool 2>/dev/null"
    deviceProperties = LinuxCommandPlugin.deviceProperties + \
        ( 'zInterfaceMapIgnoreNames', 'zInterfaceMapIgnoreTypes')

    re_iface = re.compile(r"^Settings for (?P<name>\S+):")
    re_speed = re.compile(r"Speed: (?P<speed>\d+)Mb/s")
    re_duplex = re.compile(r"Duplex: (?P<duplex>\S+)")

    def process(self, device, results, log):
        # we don't detect interface type via ethtool so if this zProperty is set,
        # we rather skip modeling since this modeler sets only link duplex/speed
        skipTypes = getattr(device, 'zInterfaceMapIgnoreTypes', None)
        if skipTypes:
            log.info("Skipping modeling via ethtool for device %s due "
                     "to no support for zInterfaceMapIgnoreTypes" % device.id)
            return

        log.info('Collecting IP interface speeds for device %s' % device.id)
        skipNames = getattr(device, 'zInterfaceMapIgnoreNames', None)
        rm = self.relMap()

        om = None
        for line in results.splitlines():
            match = self.re_iface.search(line)
            if match:
                if om:
                    rm.append(om)

                if skipNames and re.search(skipNames, match.group('name')):
                    log.info("Skipping '%s' as it matches zInterfaceMapIgnoreNames.", \
                        match.group('name'))
                    om = None
                    continue

                om = self.objectMap()
                om.id = self.prepId(match.group('name'))
                om.interfaceName = match.group('name')
                om.speed = 0
                om.duplex = 0

            if not om:
                continue

            match = self.re_speed.search(line)
            if match:
                om.speed = int(match.group('speed')) * 1e6

            match = self.re_duplex.search(line)
            if match:
                if match.group('duplex') == 'Full':
                    om.duplex = 3
                elif match.group('duplex') == 'Half':
                    om.duplex = 2

        if om:
            rm.append(om)
        return rm
