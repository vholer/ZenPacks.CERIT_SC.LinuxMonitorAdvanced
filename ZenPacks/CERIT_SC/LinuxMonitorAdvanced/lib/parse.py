import re

__all__ = ['parse_mdstat']

MULTIPLIER = {
    'KB' : 1024,
    'K'  : 1024,
    'MB' : 1024 * 1024,
    'M'  : 1024 * 1024,
    'B'  : 1
}

def parse_mdstat(results):
    linePattern = re.compile(r"\n\s*\n")
    mds = []

    # strip first and last line:
    # > Personalities : 
    # > unused devices: <none>
    for section in linePattern.split('\n'.join(results.splitlines()[1:-1])):
        # md1 : active raid1 sde1[6](F) sdg1[1] sdb1[4] sdd1[3] sdc1[2]
        # md0 : active raid1 vdg[2](S) vdf[1] vde[0]
        # md0 : active raid1 vdg[2] vdf[1](F) vde[0]
        #match=re.match(r"md(?P<id>\d+) : (?P<md_status>\w+)( \((?P<detail>[^)]+)\))? (?P<type>[\w\d]+) (?P<devicesStr>[^\n]+)$",section)
        match=re.match(r"md(?P<id>\d+) : (?P<md_status>\w+( \(.*\))?) (?P<type>[\w\d]+) (?P<devicesStr>[^\n]+)",section)
        if not match:
            print "No match!"
            continue

        md=match.groupdict()

        # read RAID devices
        counts={'active':0,'failed':0,'spare':0,'required':0,'online':0}
        devices=[]
        for dev in match.group('devicesStr').split():
            matchDev=re.match(r"(?P<device>\w+)\[(?P<id>\d+)\](\((?P<status>\w)\))?",dev)
            devices.append(matchDev.groupdict())
            if matchDev.group('status') == 'F':
                counts['failed'] += 1
            elif matchDev.group('status') == 'S':
                counts['spare'] += 1
            else:
                counts['active'] += 1
        md['devices']=devices

        # get total/online disks:
        # 63967104 blocks super 1.2 [2/2] [UU]
        #                            ^^^
        matchReq=re.search(r" \[(?P<required>\d+)/(?P<online>\d+)\] \[",section)
        if matchReq:
            counts['online']   = int(matchReq.group('online'))
            counts['required'] = int(matchReq.group('required'))

        # get RAID size:
        #  15991680 blocks super 1.2 [2/2] [UU]
        # 996119552 blocks super 1.2 512k chunks
        # ^^^^^^^^^
        matchBlcks=re.search(r"(?P<blocks>\d+) blocks",section)
        if matchBlcks:
            md['blocks']=long(matchBlcks.group('blocks'))*1024

        # get chunk size:
        #   bitmap: 1/1 pages [4KB], 65536KB chunk
        # 996119552 blocks super 1.2 512k chunks
        #                            ^^^^^^^^^^^^^
        matchChunk=re.search(r"\s(?P<size>\d+)\s*(?P<unit>\w+) chunk",section)
        if matchChunk:
            multi=MULTIPLIER.get(matchChunk.group('unit').upper(),1)
            md['stripesize'] = int(matchChunk.group('size')) * multi
        else:
            md['stripesize'] = 0

        # search for current task/progress:
        # [==============>......]  recovery = 72.0% (24162368/33553340) finish=3.4min speed=45458K/sec
        #                          ^^^^^^^^   ^^^^^
        # resync=DELAYED
        # resync=PENDING
        # ^^^^^  ^^^^^^^
        matchTask=re.search(r"\s(?P<task>recovery|resync|check)\s*=\s*(?P<progress>[^ ]+)",section)
        if matchTask:
            md=dict(md.items()+matchTask.groupdict().items())

        md['counts']=counts

        # determine RAID status
        status=1

        if re.match('active',md['md_status'],re.I):
            if counts['required']>0:
                if counts['required'] != counts['online']:
                    status=5 #degraded
                elif counts['failed']>0:
                    status=4 #online but some failed disks
                else:
                    status=2 #online
            elif counts['failed']>0:
                status=4 #degraded (probably)
            else:
                status=2 #online

            # task status: (pending, delayed, unknown, currently)
            taskMap = {
                'resync':   (7,8,9,10),
                'check':    (11,12,13,14),
                'recovery': (15,16,17,18)
            }

            if md.get('task'):
                mapIdx = 2
                if 'PENDING' in md['progress']:
                    mapIdx = 0
                elif 'DELAYED' in md['progress']:
                    mapIdx = 1
                elif re.match('\d+(\.\d+)?%',md['progress']):
                    mapIdx = 3

                status=taskMap.get(md['task'],(19,19,19,19))[mapIdx]

        elif re.match('inactive',md['md_status'],re.I):
            status=3
        else:
            status=6 #TODO??? failed??

        md['status']=status
        mds.append(md)

    return mds
