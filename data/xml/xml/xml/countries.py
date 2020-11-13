import sys
import xml.etree.ElementTree as ET
tree = ET.parse(sys.argv[-1])
root = tree.getroot()
ch = root.getchildren()
a = ch[0]
import IPython; IPython.embed()

