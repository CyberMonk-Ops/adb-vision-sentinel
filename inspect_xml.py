import xml.etree.ElementTree as ET
from ppadb.client import Client as AdbClient

# Connect to device
client = AdbClient(host="127.0.0.1", port=5037)
device = client.devices()[0]

print("[*] DUMPING UI XML...")
device.shell("uiautomator dump /sdcard/inspect.xml")
device.pull("/sdcard/inspect.xml", "inspect.xml")

# Parse and Print
tree = ET.parse("inspect.xml")
root = tree.getroot()

print("\n[*] SCANNING FOR INTERACTABLE ELEMENTS:\n" + "="*40)

for node in root.iter('node'):
    # Get all attributes
    text = node.attrib.get('text')
    desc = node.attrib.get('content-desc')
    res_id = node.attrib.get('resource-id')
    bounds = node.attrib.get('bounds')
    
    # Only show things that have a Name or ID
    if text or desc or res_id:
        print(f"Type: {res_id}")
        print(f"Text: {text} | Desc: {desc}")
        print(f"Bounds: {bounds}")
        print("-" * 20)
        # Filter for things that might be buttons (clickable=true)
        if node.attrib.get('clickable') == 'true':
            print("clickables__________________________")
            print(f"Type: {res_id}")
            print(f"Text: {text} | Desc: {desc}")
            print(f"Bounds: {bounds}")
            print("-" * 20)
            
            
            
 