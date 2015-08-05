from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

class diskstats(ComponentCommandParser):
    componentSplit = '\n'
    componentScanValue = 'id'
    componentScanner = '^\s*(\d+\s+){2}(?P<component>[^ ]+) '

    scanners = [
        r' (?P<rTotal>\d+) (?P<rMerged>\d+) (?P<rSectors>\d+) (?P<rTime>\d+)'
        r' (?P<wTotal>\d+) (?P<wMerged>\d+) (?P<wSectors>\d+) (?P<wTime>\d+)'
        r' (?P<ioPending>\d+) (?P<ioTime>\d+) (?P<ioTimeWeight>\d+)$' ]
