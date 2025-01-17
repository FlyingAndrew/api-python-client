# delivery services' tests
from robot.libraries.BuiltIn import BuiltIn
import sys
import os
import json
from pathlib import Path

sys.path.append(os.path.join(Path(__file__).parents[2], 'onc'))
from onc import ONC

# get token from Robot variable
token = BuiltIn().get_variable_value("${TOKEN}")
onc = ONC(token, True, True, 'output')


def manualRequestProduct(filters: dict):
    # Manually requests data product, doesn't execute or download
    return onc.requestDataProduct(filters)


def manualRunProduct(dpRequestId: int):
    # Manually runs request id
    return onc.runDataProduct(dpRequestId)


def manualDownloadProduct(dpRunId: int, outPath: str = None, resultsOnly: bool = False):
    # Manually downloads runId
    return onc.downloadDataProduct(dpRunId, downloadResultsOnly=resultsOnly, outPath=outPath)


def test_getDataProductUrls(onc, filters):
    print('\n9. TEST getDataProductUrls()')
    res = onc.getDataProductUrls(filters)


def test_downloadFile(onc, url):
    print('\n9. TEST downloadFile()')
    res = onc.downloadFile(url)
