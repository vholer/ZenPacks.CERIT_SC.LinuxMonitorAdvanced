import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class ip(LinuxCommandPlugin):
    modname = "Products.ZenModel.IpInterface"
    relname = "interfaces"
    compname = "os"
    command = "/sbin/ip address"
    deviceProperties = LinuxCommandPlugin.deviceProperties + \
        ( 'zInterfaceMapIgnoreNames', 'zInterfaceMapIgnoreTypes')

    re_mac = re.compile(r"link/(?P<type>\S+) (?P<mac>[0-9a-fA-F:]+)")
    re_inet = re.compile(r"(?P<type>inet6?) (?P<ip>\S+)/(?P<mask>\S+)")
    re_iface = re.compile(r"^(?P<id>\d+):\s+(?P<name>\S+):\s*"
        "<(?P<flags>[^>]+)> mtu (?P<mtu>\d+) .*state (?P<state>\S+)")    

    def process(self, device, results, log):
        log.info('Collecting IP interfaces for device %s' % device.id)
        skipNames = getattr(device, 'zInterfaceMapIgnoreNames', None)
        skipTypes = getattr(device, 'zInterfaceMapIgnoreTypes', None)
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
                om.ifindex = int(match.group('id'))
                om.mtu = int(match.group('mtu'))
                om.speed = 0
                om.duplex = 0

                if not hasattr(om, 'setIpAddresses'):
                    om.setIpAddresses = []

                flags = match.group('flags').split(',')
                if 'UP' in flags:
                    om.operStatus = 1
                else:
                    om.operStatus = 2

                if 'LOWER_UP' in flags:
                    om.adminStatus = 1
                else:
                    om.adminStatus = 2

            if not om:
                continue

            match = self.re_mac.search(line)
            if match:
                om.macaddress = match.group('mac')

                # based on net-snmp Interface MIB code, but improved
                # http://sourceforge.net/p/net-snmp/code/ci/master/tree/agent/mibgroup/if-mib/data_access/interface_linux.c
                if om.interfaceName.startswith('vmnet'):
                    om.type = 'ethernetCsmacd'
                elif om.interfaceName.startswith('tr'):
                    om.type = 'iso88025TokenRing'
                elif om.interfaceName.startswith('feth'):
                    om.type = 'fastEther' # fix -> ethernetCsmacd
                elif om.interfaceName.startswith('gig'):
                    om.type = 'gigabitEthernet' # fix -> ethernetCsmacd
                elif om.interfaceName.startswith('ib'):
                    om.type = 'infiniband'
                elif om.interfaceName.startswith('ppp'):
                    om.type = 'ppp'
                elif om.interfaceName.startswith('sl'):
                    om.type = 'slip'
                elif om.interfaceName.startswith('sit'):
                    om.type = 'tunnel'
                elif om.interfaceName.startswith('ippp'):
                    om.type = 'basicISDN'
                elif om.interfaceName.startswith('bond'):
                    om.type = 'propVirtual'
                elif om.interfaceName.startswith('vad'):
                    om.type = 'propVirtual'

                # custom
                elif om.interfaceName.startswith('usb'):
                    om.type = 'usb'
                elif re.match('^(vnet|virbr|veth|docker)', om.interfaceName):
                    om.type = 'propVirtual'

                # based on type returned by "ip"
                elif match.group('type').startswith('loopback'):
                    om.type = 'softwareLoopback'
                elif match.group('type').startswith('ether'):
                    om.type = 'ethernetCsmacd'
                else:
                    om.type = 'other' #? match.group('type')

                # skip by type
                if skipTypes and re.search(skipTypes, om.type):
                    log.info("Skipping '%s' as it matches zInterfaceMapIgnoreTypes.", \
                        om.interfaceName)
                    om = None
                    continue

            match = self.re_inet.search(line)
            if match:
                om.setIpAddresses.append("%s/%s" % \
                    (match.group('ip'), match.group ('mask')))

        if om:
            rm.append(om)
        return rm
