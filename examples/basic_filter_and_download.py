from onc.onc import ONC
import os
import datetime
import random

'''This examples shows a basic technics of accessing data from the ONC server.
IMPORTANT fill in your personal ONC token at: https://wiki.oceannetworks.ca/display/O2KB/Get+your+API+token

1. It randomly chooses a location from all locations
2. from the location it select a device, 
3. downloads 2 'Log File' of that device
'''

# Initialize
token = 'YOUR-ONC-TOKEN'
onc = ONC(token=token)

# Get all locations and select one randomly
locations = onc.getLocations()
location_selected = random.choice(locations)
print(location_selected['locationName'])

# Get all devices from the selected location and select one randomly
devices = onc.getDevices(filters={'locationCode': location_selected['locationCode']})
device_selected = random.choice(devices)
print(device_selected['deviceName'])

# Get all data-products from the selected device and select one randomly
data_products = onc.getDataProducts(filters={'deviceCode': device_selected['deviceCode']})
data_product_selected = random.choice(data_products)
print(data_product_selected['dataProductName'])

# getDataProducts list all possible data-product from that moduel, but this doesn't mean the module generated one
# already. For this reason, there can be no file available for that device and data-product on the ONC server.
# Therefore, use 'LF' instead
data_product_selected = {'dataProductCode': 'LF',  # 'LF' is the log file, and that's for sure available
                         'dataProductName': 'Log File',
                         'extension': 'txt',
                         'hasDeviceData': True,
                         'hasPropertyData': False,
                         'helpDocument': 'https://wiki.oceannetworks.ca/display/DP/4'}

print(f'But use the "{data_product_selected["dataProductName"]}" instead')

# Get a possible filenames for the filter parameter.
# The result is a dict with key 'files'; result['files'] is a list; and result['files'][:] are dicts again
result = onc.getListByDevice(filters={'deviceCode': device_selected['deviceCode'],
                                      'dataProductCode': data_product_selected['dataProductCode'],
                                      'returnOptions': 'all',  # includes all parameter per file like 'dateFrom'
                                      },
                             allPages=True)
print(f"Files available {len(result['files'])}")

# Generate 'outPath' per file and store it in the result['files'][:] dicts
# Here the 'outPath' are: onc_data/<YYYY>_<MM>/<deviceCode>
for i, file_i in enumerate(result['files']):
    dev_i = file_i['deviceCode']
    date_from = datetime.datetime.strptime(file_i['dateFrom'], "%Y-%m-%dT%H:%M:%S.000Z")
    result['files'][i]['outPath'] = os.path.join('onc_data', file_i['deviceCode'], date_from.strftime("%Y_%m"))

# Copy the result and cut it to 2 files only
result_download = result.copy()
result_download['files'] = result_download['files'][:2]

# Download the files
download_results = onc.getDirectFiles(filters_or_result=result_download)