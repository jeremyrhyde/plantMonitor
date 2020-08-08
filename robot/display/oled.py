#!/usr/bin/env python3
"""oled.py
"""

import Adafruit_SSD1306
import threading
import time
from queue import Queue, Empty
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

__author__ = "Sharan Juangphanich"
__copyright__ = "Copyright 2018, Latchables, Inc."
__credits__ = ["Sharan Juangphanich", "Aaron Sirken"]

#class Oled_Fake:
 #   def set_text(self,a1,a2):
  #      pass
   # def clear(self):
    #    pass
    #def close(self):
     #   pass
class Oled:

    RST = None  # on the SSD1306 this pin isnt used
    font = ImageFont.truetype("robot/display/Timeless.ttf", 14)
    top = -2
    x = 0

    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=self.RST)
        self.disp.begin()
        self.clear()

        self._q = Queue()
        self._stop_event = threading.Event()
        self.oled_thread = threading.Thread(target=self._oled_run)
        self.oled_thread.start()

    def _oled_run(self):
        while not self._stop_event.is_set():
            text1, text2 = self._q.get()
            self._set_text(text1, text2)
            self._q.task_done()

    def _set_text(self, text1, text2):
        image = Image.new("1", (self.disp.width, self.disp.height))
        draw = ImageDraw.Draw(image)

        self.disp.clear()
        draw.text((self.x, self.top), text1 + " ", font=self.font, fill=10)
        draw.text((self.x, self.top + 16), text2 + " ", font=self.font, fill=10)
        self.disp.image(image)
        self.disp.display()

    def set_text(self, text1, text2):
        while not self._q.empty():
            try:
                self._q.get(False)
            except Empty:
                continue
            self._q.task_done()

        self._q.put((text1, text2))

    # Clear display.
    def clear(self):
        self.disp.clear()
        self.disp.display()

    def close(self):
        # Stop thread
        self._stop_event.set()
        self.oled_thread.join()


def main():
    #try:
    #    my_oled = Oled()
    #except OSError:
    #    my_oled = Oled_Fake()
    #my_oled.set_text("LATCH", "TEST")
    my_oled = Oled()
    my_oled.set_text("LATCH", "TEST")

if __name__ == "__main__":
    main()
