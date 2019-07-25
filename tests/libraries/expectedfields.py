# Expected fields information for the responses the client methods return
# Note that:
#   Python's float type has float precision
#   Field types that end with a * can also have the None type

expectedFields = {
	"getLocations": {
		"locationCode":    "str",
	    "locationName":    "str",
	    "description":     "str",
	    "deployments":     "int",
	    "hasDeviceData":   "bool",
	    "hasPropertyData": "bool",
	    "bbox":            "dict*",
	    "lon":             "float*",
	    "lat":             "float*",
	    "depth":           "float*",
	    "dataSearchURL":   "str"
	},
	"getLocationHierarchy": {
		"locationCode":    "str",
	    "locationName":    "str",
	    "description":     "str",
	    "hasDeviceData":   "bool",
	    "hasPropertyData": "bool",
	    "children":        "list"
	},
	"getDevices": {
		"deviceCode":    "str",
	    "deviceId":      "int",
	    "deviceName":    "str",
	    "deviceLink":    "str",
	    "dataRating":    "list",
	    "cvTerm":        "dict",
	    "hasDeviceData": "bool"
	},
	"getDeviceCategories": {
		"deviceCategoryCode": "str",
	    "deviceCategoryName": "str",
	    "description":        "str",
	    "hasDeviceData":      "bool",
	    "longDescription":    "str",
	    "cvTerm":             "dict"
	},
	"getDeployments": {
		"begin":         "str",
	    "depth":         "float",
	    "deviceCode":    "str",
	    "end":           "str*",
	    "hasDeviceData": "bool",
	    "heading":       "float*",
	    "lat":           "float",
	    "locationCode":  "str",
	    "lon":           "float",
	    "pitch":         "float*",
	    "roll":          "float*"
	},
	"getProperties": {
		"propertyCode":    "str",
	    "propertyName":    "str",
	    "description":     "str",
	    "hasDeviceData":   "bool",
	    "hasPropertyData": "bool",
	    "uom":             "str",
	    "cvTerm":          "dict"
	},
	"getDataProducts": {
	    "dataProductCode": "str",
	    "dataProductName": "str",
	    "extension":       "str",
	    "hasDeviceData":   "bool",
	    "hasPropertyData": "bool",
	    "helpDocument":    "str"
	},
	"orderDataProduct": {
	    "index"           : "str",
	    "url"             : "str",
	    "status"          : "str",
	    "downloaded"      : "bool",
	    "file"            : "str",
	    "size"            : "int",
	    "fileDownloadTime": "float"
	}
}