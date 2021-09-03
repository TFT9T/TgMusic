# Author: https://github.com/AYMENJD (AYMEN Mohammed telegram.me/K6KKK).

from time import gmtime, sleep, strftime, time
import threading
from typing import Optional


class Stopwatch:
    def __init__(self) -> None:
        self.timer = 0
        self._pause = False
        self._stop = False
        self._saved = []
        self.thread = threading.Thread(target=self._counter, daemon=True)

    def start(self) -> bool:
        """start timing"""
        if self.thread.is_alive() == False:
            self.thread.start()
        elif self._stop == True:
            self.thread = threading.Thread(target=self._counter, daemon=True)
            self._stop = False
            self.thread.start()
        else:
            self._pause = False
        return True

    def pause(self) -> bool:
        """pause timing"""
        self._pause = True
        return True

    def save(self) -> bool:
        """save the current timing to list"""
        self._saved.append(self.timer)
        return True

    def saved(self) -> list:
        """returns a list of timings that saved using save() method"""
        return self._saved

    def current(self) -> int:
        """current timing"""
        return self.timer

    def format(self, num: Optional[int] = None, format: Optional[str] = "%M:%S") -> str:
        """time formater

        Args:
            num (`int`): Optional, number of seconds to format.
            format (`str`): Optional, format code.
        """
        num = self.timer if num is None else num
        return strftime(format, gmtime(num))

    def stop(self):
        """stop timer"""
        self._stop = True
        self._pause = True
        if self.thread.is_alive():
            self.thread.join(1)

    def reset(self, restart=True):
        """Reset timer data

        Args:
            restart (`bool`): if True, restart timer.
        """
        if self.thread.is_alive() == True:
            self._stop = True
            self._pause = True
            self.thread.join(1)
        self.timer = 0
        self._pause = False
        self._stop = False
        self._saved = []
        self.thread = threading.Thread(target=self._counter, daemon=True)
        if restart:
            self.thread.start()

    def _counter(self) -> None:
        while self._stop == False:
            while self._pause == False:
                # now = time()
                # sleep(1)
                # self.timer += time() - now
                sleep(1)
                self.timer += 1
