from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

class net_dev(ComponentCommandParser):
    componentSplit = '\n'
    componentScanValue = 'interfaceName'
    componentScanner = '^\s*(?P<component>[^:]+):'

    ids = ('ifInOctets', 'ifInUcastPackets', 'ifInErrors', 'ifInDropped',
           'ifInFifo', 'ifInFrame', 'ifInCompressed', 'ifInMcastPackets',
           'ifOutOctets', 'ifOutUcastPackets', 'ifOutErrors', 'ifOutDropped',
           'ifOutFifo', 'ifOutCollisions', 'ifOutCarrier', 'ifOutCompressed')

    scanners = [ r':\s*' +
                 r'\s+'.join([r'(?P<%s>\d+)' % (i) for i in ids]) +
                 r'$' ]
