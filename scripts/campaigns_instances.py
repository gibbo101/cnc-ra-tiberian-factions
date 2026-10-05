#!/usr/bin/env python3
"""Write the mod's loose INSTANCES.XML (docs/campaigns-page.md): the stock missions hidden from the
CAMPAIGNS page, then the mod's own missions appended after every stock base they inherit from.

usage: campaigns_instances.py <stock INSTANCES.XML> <mod missions .xml> <out INSTANCES.XML>
"""
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

SHOWN = b'<ShowOnMissionSelect>true</ShowOnMissionSelect>'
HIDDEN = b'<ShowOnMissionSelect>false</ShowOnMissionSelect>'


def main(src, missions, out):
    data = open(src, 'rb').read()
    hidden = data.count(SHOWN)
    data = data.replace(SHOWN, HIDDEN)
    mod = open(missions, 'rb').read()
    count = len(ET.fromstring(mod).findall('Instance'))
    body = mod[mod.index(b'>', mod.index(b'<Missions')) + 1:mod.rindex(b'</Missions>')].strip(b'\r\n')
    if body:
        close = data.rindex(b'</')
        data = data[:close] + body + b'\r\n' + data[close:]
    open(out, 'wb').write(data)
    xml.dom.minidom.parse(out)
    print('wrote', out, '(%d stock missions hidden, %d mod missions)' % (hidden, count))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
