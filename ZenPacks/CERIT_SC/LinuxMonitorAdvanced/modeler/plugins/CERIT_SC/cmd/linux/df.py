import re
from Products.DataCollector.plugins.CollectorPlugin import LinuxCommandPlugin

class df(LinuxCommandPlugin):
    maptype = "FilesystemMap"
    modname = "Products.ZenModel.FileSystem"
    relname = "filesystems"
    compname = "os"
    command = '''
        if which timeout >/dev/null 2>&1; then
            timeout 30 /bin/df -PkT 2>/dev/null
        else
            /bin/df -PkT 2>/dev/null
        fi
    '''

    deviceProperties = LinuxCommandPlugin.deviceProperties + \
        ( 'zFileSystemMapIgnoreNames', 'zFileSystemMapIgnoreFormats' )

    def process(self, device, results, log):
        log.info('Collecting filesystems for device %s' % device.id)
        skipNames = getattr(device, 'zFileSystemMapIgnoreNames', None)
        skipFormats = getattr(device, 'zFileSystemMapIgnoreFormats', None)
        rm = self.relMap()

        for line in results.splitlines():
            if line.startswith('Filesystem'):
                continue

            om = self.objectMap()

            try:
                (om.storageDevice, om.type, tblocks, u, a, p, om.mount) = \
                    line.split()

                if tblocks == "-":
                    om.totalBlocks = 0
                else:
                    om.totalBlocks = long(tblocks) # or fail on ValueError
            except ValueError:
                continue

            # skip by mount point name
            if skipNames and re.search(skipNames, om.mount):
                log.info("Skipping %s as it matches zFileSystemMapIgnoreNames.", \
                    om.mount)
                continue            

            # skip by filesystem format (e.g. nfs4)
            if skipFormats and om.type in skipFormats:
                log.info("Skipping %s as it matches zFileSystemMapIgnoreFormats.", \
                    om.mount)
                continue            

            om.blockSize = 1024
            om.id = self.prepId(om.mount)
            om.title = om.mount
            rm.append(om)

        return rm
