import json
import datetime
import re
from dateutil import parser
from modules._OncDiscovery import _OncDiscovery
from modules._OncDelivery import _OncDelivery
from modules._OncRealTime import _OncRealTime
from modules._OncArchive import _OncArchive
from onc.util.util import add_docs


class ONC:
    """
    Python ONC Api Client Library
    Common library wrapper
    """

    def __init__(self, token, production: bool = True, showInfo: bool = False, outPath: str = 'output',
                 timeout: int = 60, download_threads: int = 2):
        self.token = re.sub('[^a-zA-Z0-9\-]+', '', token)
        self.showInfo = showInfo
        self.timeout = timeout
        self.baseUrl = 'https://data.oceannetworks.ca/'
        self.outPath = ''
        self.download_threads = download_threads

        # sanitize outPath
        if len(outPath) > 0:
            outPath = outPath.replace('\\', '/')
            if outPath[-1] == '/':
                outPath = outPath[:-1]
            self.outPath = outPath

        # switch to qa if needed
        if not production:
            self.baseUrl = 'https://qa.oceannetworks.ca/'

        # Create service objects
        self.discovery = _OncDiscovery(self)
        self.delivery = _OncDelivery(self)
        self.realTime = _OncRealTime(self)
        self.archive = _OncArchive(self)

    @staticmethod
    def print(obj, filename: str = ""):
        """
        Helper for printing a JSON dictionary to the console or to a file
        @filename: if present, creates the file and writes the output in it
        """
        text = json.dumps(obj, indent=4)
        if filename == '':
            print(text)
        else:
            with open(filename, 'w+') as file:
                file.write(text)

    @staticmethod
    def formatUtc(dateString: str = 'now'):
        """
        Helper that returns an ISO8601 string for the provided date string
        Most date formats are supported, as explained in:
        http://labix.org/python-dateutil#head-c0e81a473b647dfa787dc11e8c69557ec2c3ecd2
        A value of "now" returns the current UTC date & time
        Depends on the local system clock
        """
        if dateString == 'now':
            return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + '.000Z'
        else:
            objDate = parser.parse(dateString)
            return objDate.replace(microsecond=0).isoformat() + '.000Z'

    # PUBLIC METHOD WRAPPERS

    # Discovery methods
    @add_docs(_OncDiscovery.getLocations)
    def getLocations(self, filters: dict = None):
        return self.discovery.getLocations(filters)

    @add_docs(_OncDiscovery.getLocationHierarchy)
    def getLocationHierarchy(self, filters: dict = None):
        return self.discovery.getLocationHierarchy(filters)

    @add_docs(_OncDiscovery.getDeployments)
    def getDeployments(self, filters: dict = None):
        return self.discovery.getDeployments(filters)

    @add_docs(_OncDiscovery.getDevices)
    def getDevices(self, filters: dict = None):
        return self.discovery.getDevices(filters)

    @add_docs(_OncDiscovery.getDeviceCategories)
    def getDeviceCategories(self, filters: dict = None):
        return self.discovery.getDeviceCategories(filters)

    @add_docs(_OncDiscovery.getProperties)
    def getProperties(self, filters: dict = None):
        return self.discovery.getProperties(filters)

    @add_docs(_OncDiscovery.getDataProducts)
    def getDataProducts(self, filters: dict = None):
        return self.discovery.getDataProducts(filters)

    # Delivery methods
    @add_docs(_OncDelivery.orderDataProduct)
    def orderDataProduct(self, filters: dict, maxRetries: int = 0, downloadResultsOnly: bool = False,
                         includeMetadataFile: bool = True, overwrite: bool = False):
        return self.delivery.orderDataProduct(filters, maxRetries, downloadResultsOnly, includeMetadataFile, overwrite)

    @add_docs(_OncDelivery.requestDataProduct)
    def requestDataProduct(self, filters: dict):
        return self.delivery.requestDataProduct(filters)

    @add_docs(_OncDelivery.runDataProduct)
    def runDataProduct(self, dpRequestId: int, waitComplete: bool = True):
        return self.delivery.runDataProduct(dpRequestId, waitComplete)

    @add_docs(_OncDelivery.downloadDataProduct)
    def downloadDataProduct(self, runId: int, maxRetries: int = 0, downloadResultsOnly: bool = False,
                            includeMetadataFile: bool = True, overwrite: bool = False):
        return self.delivery.downloadDataProduct(runId, maxRetries, downloadResultsOnly, includeMetadataFile, overwrite)

    # Real-time methods

    @add_docs(_OncRealTime.getDirectByLocation)
    def getDirectScalar(self, filters: dict = None, allPages: bool = False):
        # Alias for getDirectByLocation (to be eventually discontinued)
        return self.getDirectByLocation(filters, allPages)

    @add_docs(_OncRealTime.getDirectByLocation)
    def getDirectByLocation(self, filters: dict = None, allPages: bool = False):
        return self.realTime.getDirectByLocation(filters, allPages)

    @add_docs(_OncRealTime.getDirectByDevice)
    def getDirectByDevice(self, filters: dict = None, allPages: bool = False):
        return self.realTime.getDirectByDevice(filters, allPages)

    @add_docs(_OncRealTime.getDirectRawByLocation)
    def getDirectRawByLocation(self, filters: dict = None, allPages: bool = False):
        return self.realTime.getDirectRawByLocation(filters, allPages)

    @add_docs(_OncRealTime.getDirectRawByDevice)
    def getDirectRawByDevice(self, filters: dict = None, allPages: bool = False):
        return self.realTime.getDirectRawByDevice(filters, allPages)

    # Archive file methods
    @add_docs(_OncArchive.getListByLocation)
    def getListByLocation(self, filters: dict = None, allPages: bool = False):
        return self.archive.getListByLocation(filters, allPages)

    @add_docs(_OncArchive.getListByDevice)
    def getListByDevice(self, filters: dict = None, allPages: bool = False):
        return self.archive.getListByDevice(filters, allPages)

    @add_docs(_OncArchive.getFile)
    def getFile(self, filename: str = '', overwrite: bool = False, outPath: str = None):
        return self.archive.getFile(filename, overwrite, outPath)

    @add_docs(_OncArchive.getDirectFiles)
    def getDirectFiles(self, filters_or_result: dict = None, overwrite: bool = False, allPages: bool = False):
        return self.archive.getDirectFiles(filters_or_result, overwrite, allPages)
