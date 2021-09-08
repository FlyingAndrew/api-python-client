import os
import sys
import threading
import time

import humanize
from datetime import timedelta

from tqdm import tqdm


def saveAsFile(response, filePath: str, fileName: str, overwrite: bool):
    """
    Saves the file downloaded in the response object, in the outPath, with filename
    If overwrite, will overwrite files with the same name
    @returns status: int 0: Success, 1: Error, 2: Skipped: File exists
    """
    fullPath = fileName
    if len(filePath) > 0:
        fullPath = filePath + '/' + fileName
        # Create outPath directory if not exists
        if not os.path.exists(filePath):
            os.makedirs(filePath)

    # Save file in outPath if it doesn't exist yet
    if overwrite or (not os.path.exists(fullPath)):
        try:
            file = open(fullPath, 'wb+')
            file.write(response.content)
            file.close()
            return 0

        except Exception:
            return -1
    else:
        return -2


def _formatSize(size: float):
    """
    Returns a formatted file size string representation
    @param size: {float} Size in bytes
    """
    return humanize.naturalsize(size)


def _formatDuration(secs: float):
    """
    Returns a formatted time duration string representation of a duration in seconds
    @param secs: float
    """
    if secs < 1.0:
        txtDownTime = '{:.3f} seconds'.format(secs)
    else:
        d = timedelta(seconds=secs)
        txtDownTime = humanize.naturaldelta(d)

    return txtDownTime


def _printErrorMessage(response):
    """
    Method to print infromation of an error returned by the API to the console
    Builds the error description from the response object 
    """
    status = response.status_code
    if status == 400:
        print('\nError 400 - Bad Request: {:s}'.format(response.url))
        payload = response.json()
        if len(payload) >= 1:
            for e in payload['errors']:
                code = e['errorCode']
                msg = e['errorMessage']
                parameters = e['parameter']
                print("   Error {:d}: {:s} (parameter: {})".format(code, msg, parameters))

    elif status == 401:
        print('Error 401 - Unauthorized: {:s}'.format(response.url))
        print(
            'Please check that your Web Services API token is valid. Find your token in your registered profile at '
            'https://data.oceannetworks.ca.')

    else:
        msg = '\nError {:d} - {:s}\n'.format(status, response.reason)
        print(msg)


def _messageForError(status: int):
    """
    Return a description string for an HTTP error code
    """
    errors = {
        500: 'Internal server error',
        503: 'Service temporarily unavailable',
        598: 'Network read timeout error'
    }
    return errors[status]


class ShareJobThreads:
    def __init__(self, thread_n=3, fmt=None):
        """ A Class which spreads a iterable job defined by a function f to n threads. It is basically a Wrapper for:
        for i in iterable:
            f(i)

        The above example translates to:
        sjt = ShareJobThreads(4)  # for 4 threads
        sjt.do(f, iterable)
        """
        self.thread_n = thread_n
        self.lock = threading.Lock()
        self.thread_bar = None
        self.active = False
        self.event = threading.Event()

        self.threads = None  # the _worker_ threads
        self.iterable = None  # the iterable
        self.i = None  # the actual index
        self.f = None  # the function

        # formatter for the bar, if not None, the iterable has to be a dict, i.e. {'a':1, 'b':2}, and the fmt: '{a}-{b}'
        self.fmt = fmt  # formatter for the bar

    def do(self, f, iterable, ):
        self.active = True
        self.iterable = iterable
        self.i = 0
        self.f = f

        self.threads = []

        for i in range(self.thread_n):
            thread_i = threading.Thread(target=self._worker_)
            thread_i.start()
            self.threads.append(thread_i)

        self.thread_bar = threading.Thread(target=self._update_bar_)
        self.thread_bar.start()
        self.thread_bar.join()

    def _update_bar_(self, ):
        last_i = 0

        with tqdm(self.iterable,
                  file=sys.stdout,
                  unit='file') as bar:
            while any([i.is_alive() for i in self.threads]) or last_i != self.i:
                with self.lock:
                    # print(self.i, self.active)
                    if last_i != self.i:
                        for i in range(self.i - last_i):
                            str_i = self.iterable[self.i - 1 - i]
                            if self.fmt is not None and isinstance(self.iterable[self.i - 1 - i], dict):
                                str_i = self.fmt.format(**self.iterable[self.i - 1 - i])

                            bar.set_postfix({'i': str_i})
                            bar.update()

                        last_i = self.i
                time.sleep(0.1)  # delay a bit

    def stop(self, ):
        self.active = False

    def _worker_(self, ):
        iterable_i = True
        while self.active and iterable_i:
            iterable_i = self._get_next_()
            if iterable_i is not False:
                self.f(iterable_i)

    def _get_next_(self, ):
        with self.lock:
            if len(self.iterable) > self.i:
                iterable_i = self.iterable[self.i]
                self.i += 1
                return iterable_i
            else:
                return False
