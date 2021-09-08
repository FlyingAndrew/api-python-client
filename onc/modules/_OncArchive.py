import os
import threading
import time

import humanize
import requests
import pandas

from ._MultiPage import _MultiPage
from ._OncService import _OncService
from ._util import saveAsFile, _printErrorMessage, _formatDuration, ShareJobThreads


class _OncArchive(_OncService):
    """
    Methods that wrap the API archivefiles service
    """

    def __init__(self, parent: object):
        super().__init__(parent)

    def getListByLocation(self, filters: dict = None, allPages: bool = False):
        """
        Get a list of files for a given location code and device category code, and filtered by others optional
        parameters. If locationCode or deviceCategoryCode are missing, we suppose they are in the filters
        """
        try:
            return self._getList(filters, by='location', allPages=allPages)
        except Exception:
            raise

    def getListByDevice(self, filters: dict = None, allPages: bool = False):
        """
        Get a list of files available in Oceans 2.0 Archiving System for a given device code. The list of filenames can
        be filtered by time range. If deviceCode is missing, we suppose it is in the filters
        """
        try:
            return self._getList(filters, by='device', allPages=allPages)
        except Exception:
            raise

    def getFile(self, filename: str = '', overwrite: bool = False, outPath: str = None):
        url = self._serviceUrl('archivefiles')

        filters = {
            'token': self._config('token'),
            'method': 'getFile',
            'filename': filename
        }

        try:
            # Download the archived file with filename (response contents is binary)
            start = time.time()
            response = requests.get(url, filters, timeout=self._config('timeout'))
            status = response.status_code
            elapsed = time.time() - start

            if response.ok:
                # Save file to output path
                if outPath is None:
                    outPath = self._config('outPath')
                saveAsFile(response, outPath, filename, overwrite)
                filePath = '{:s}/{:s}'.format(outPath, filename)
                # self._fixGzFileExtension(filePath) # Supposedly not needed after DMAS fix

            else:
                _printErrorMessage(response)
                if status == 400:
                    raise Exception('   The request failed with HTTP status 400.', response.json())
                else:
                    raise Exception('   The request failed with HTTP status {:d}.'.format(status), response.text)

        except Exception:
            raise

        # Prepare a readable status
        txtStatus = "error"
        if status == 200:
            txtStatus = "completed"

        return {
            'url': response.url,
            'status': txtStatus,
            'size': len(response.content),
            'downloadTime': round(elapsed, 3),
            'file': filename
        }

    def getDirectFiles(self, filters_or_result: dict, overwrite: bool = False, allPages: bool = False,
                       download_threads: int = None):
        """
         Method to download files from the archivefiles service
         see https://wiki.oceannetworks.ca/display/help/archivefiles for usage and available filters for
         'filters_or_result'.
         PARAMETER
         ---------
         filters_or_result: dict,
            can one of:
            - 'filters'-dict following https://wiki.oceannetworks.ca/display/help/archivefiles
            - 'result'-dict which is returned i.e. by 'getListByDevice', 'getListByLocation', or 'getList'. The
            'result'-dict has to be in the shape:
            {'files': [{'filename': file_a}, {'filename': file_b, 'outPath': dir_b}, ...]}. This means, for each file
            a separated 'outPath' can be defined. If not, the default 'outPath' is used.
            - pandas.DataFrame with column 'filename' and optional 'outPath'
        overwrite: bool, optional
            If True, it will overwrite existing files. Default False, which skips exiting files.
        allPages: bool, optional
            See `getListByLocation` or `getListByDevice`
        download_threads: int, optional
            Defines the number of thread for the download. If None (default) it uses the 'download_threads' form the
            ONC initialisation.
         """
        # make sure we only get a simple list of files
        if 'returnOptions' in filters_or_result:
            del filters_or_result['returnOptions']

        # Get a list of files
        # try:
        if 'files' in filters_or_result:
            dataRows = filters_or_result
        elif isinstance(filters_or_result, pandas.DataFrame):
            if 'outPath' in filters_or_result:
                dataRows = {'files': filters_or_result[['filename', 'outPath']].to_dict(orient='records')}
            else:
                dataRows = {'files': filters_or_result[['filename']].to_dict(orient='records')}
        elif 'locationCode' in filters_or_result and 'deviceCategoryCode' in filters_or_result:
            dataRows = self.getListByLocation(filters=filters_or_result, allPages=allPages)
        elif 'deviceCode' in filters_or_result:
            dataRows = self.getListByDevice(filters=filters_or_result, allPages=allPages)
        else:
            raise Exception(
                'getDirectFiles filters_or_result require either a combination of "locationCode" and '
                '"deviceCategoryCode", or a "deviceCode" or "files" '
                '(see _OncArchiveDownloader.download_file) present.')
        # except Exception:
        #     raise

        downloader = _OncArchiveDownloader(parent=self.parent, overwrite=overwrite)
        start, elapsed, download_speed = 0, 0, 0  # to measure download time

        if dataRows['files']:
            # check for exiting files and pop those
            if not overwrite:
                exiting_files = []
                for i, file_i in enumerate(dataRows['files'].copy()):  # copy is important for dataRows['files'].pop
                    if isinstance(file_i, str):
                        filename = file_i
                        outPath = self._config('outPath')
                    else:
                        filename = file_i['filename']
                        if 'outPath' in file_i:
                            outPath = file_i['outPath']
                        else:
                            outPath = self._config('outPath')

                    file_path = os.path.join(outPath, filename)
                    if os.path.exists(file_path):
                        exiting_files.append(dataRows['files'].pop(i-len(exiting_files)))

                if exiting_files:
                    print(f'Skipping {len(exiting_files)} files.')

            # check again if there a files to download, maybe they all exist already and overwrite=False
            if dataRows['files']:
                start = time.time()
                if download_threads is None:
                    download_threads = self._config('download_threads')

                share_job_threads = ShareJobThreads(download_threads, fmt='{filename}')
                share_job_threads.do(downloader.download_file, dataRows['files'])

                elapsed = time.time() - start
                download_speed = downloader.size/elapsed

        print('Downloaded - Directory: {:s}; Files: {:d}; Size: {:s}; Time: {:s}; Speed: {:s}/s'.format(
            self._config('outPath'),
            downloader.successes,
            humanize.naturalsize(downloader.size),
            _formatDuration(elapsed),
            humanize.naturalsize(download_speed),
            )
        )

        return {
            'downloadResults': downloader.downInfos,
            'stats': {
                'totalSize': downloader.size,
                'downloadTime': elapsed,
                'fileCount': downloader.successes
            }
        }

    def _getDownloadUrl(self, filename: str):
        """
        Returns an archivefile absolute download URL for a filename
        """
        url = self._serviceUrl('archivefiles')
        return '{:s}?method=getFile&filename={:s}&token={:s}'.format(url, filename, self._config('token'))

    def _getList(self, filters: dict, by: str = 'location', allPages: bool = False):
        """
        Wraps archivefiles getListByLocation and getListByDevice methods
        """
        url = self._serviceUrl('archivefiles')
        filters['token'] = self._config('token')
        filters['method'] = 'getListByLocation' if by == 'location' else 'getListByDevice'

        # parse and remove the artificial parameter extension
        extension = None
        filters2 = filters.copy()
        if 'extension' in filters2:
            extension = filters2['extension']

        try:
            if allPages:
                mp = _MultiPage(self)
                result = mp.getAllPages('archivefiles', url, filters2)
            else:
                if 'extension' in filters2:
                    del filters2['extension']
                result = self._doRequest(url, filters2)
                result = self._filterByExtension(result, extension)
            return result
        except Exception:
            raise

    @staticmethod
    def _filterByExtension(results: dict, extension: str):
        """
        Filter results to only those where filenames end with the extension
        If extension is None, won't do anything
        Returns the filtered list
        """
        if extension is None:
            return results

        extension = '.' + extension  # match the dot to avoid matching substrings
        n = len(extension)
        filtered = []  # appending is faster than deleting

        # determine the row structure
        rowFormat = 'filename'
        if len(results['files']) > 0:
            if isinstance(results['files'][0], dict):
                rowFormat = 'dict'

        # filter
        for file in results['files']:
            if rowFormat == 'filename':
                if file[-n:] == extension:
                    filtered.append(file)
            else:
                if file['filename'][-n:] == extension:
                    filtered.append(file)
        results['files'] = filtered

        return results


# Download the files obtained
class _OncArchiveDownloader(_OncArchive):
    def __init__(self, parent: object, overwrite: bool = False):
        super().__init__(parent)
        self.overwrite = overwrite
        self.tries = 1
        self.successes = 0
        self.size = 0
        self.time = 0

        self.downInfos = []
        self.info_lock = threading.Lock()

    def download_file(self, download_parameters):
        """
        Downloads a file in a thread safe environment, i.e. to use it with ShareJobThreads.
        PARAMETERS
        ----------
        download_parameters: str, list, tuple, or dict
            download_parameters can be either:
                1. a str, which is interpreted as the 'filename'. For the 'outPath' it takes the default path.
                2. a list or tuple, with len = 2, the first entry is the 'filename' and the second the 'outPath'
                3. a dict, with at least the key 'filename'. 'outPath' is optional, and if not set its the default path.
        """
        if isinstance(download_parameters, str):
            filename = download_parameters
            outPath = self._config('outPath')
        elif isinstance(download_parameters, (list, tuple)):
            filename = download_parameters[0]
            outPath = download_parameters[1]
        elif type(download_parameters) is dict:
            filename = download_parameters['filename']
            if 'outPath' in download_parameters:
                outPath = download_parameters['outPath']
            else:
                outPath = self._config('outPath')
        else:
            raise ValueError(f'download_parameters as to be out of, str, tuple: (str,str), list: [str, str],'
                             f'or dict: {"filename": str, ["outPath": str]}, got: {download_parameters}')

        filePath = os.path.join(outPath, filename)
        fileExists = os.path.exists(filePath)

        if (not fileExists) or (fileExists and self.overwrite):
            try:
                downInfo = self.getFile(filename, overwrite=self.overwrite, outPath=outPath)
                with self.info_lock:
                    self.size += downInfo['size']
                    self.time += downInfo['downloadTime']
                    self.downInfos.append(downInfo)
                    self.successes += 1
            except Exception:
                raise
            self.tries += 1
        else:
            downInfo = {
                'url': self._getDownloadUrl(filename),
                'status': 'skipped',
                'size': 0,
                'downloadTime': 0,
                'file': filename
            }
            with self.info_lock:
                self.downInfos.append(downInfo)
