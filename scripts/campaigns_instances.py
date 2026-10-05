#!/usr/bin/env python3
"""Write the mod's loose INSTANCES.XML (docs/campaigns-page.md): the stock missions hidden from the
CAMPAIGNS page, so every faction tab shows COMING SOON until the mod's own missions are added.

usage: campaigns_instances.py <stock INSTANCES.XML> <out INSTANCES.XML>
"""
import sys
import xml.dom.minidom

SHOWN = b'<ShowOnMissionSelect>true</ShowOnMissionSelect>'
HIDDEN = b'<ShowOnMissionSelect>false</ShowOnMissionSelect>'


def main(src, out):
    data = open(src, 'rb').read()
    count = data.count(SHOWN)
    data = data.replace(SHOWN, HIDDEN)
    open(out, 'wb').write(data)
    xml.dom.minidom.parse(out)
    print('wrote', out, '(%d stock missions hidden)' % count)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(*sys.argv[1:])
