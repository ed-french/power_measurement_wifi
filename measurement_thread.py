# -*- coding: UTF-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)

from threading import Thread
from collections import deque
from make_measurements import Measurer
import time
import json



class ReadingCollector(Thread):
    """
            A ReadingCollector is initiated and then runs it's own thread collecting data into a deque
            These readings 
    
    """
    def __init__(self,serial_port:str="COM4",max_size=1500):
        super().__init__()
        self.dataset=deque(maxlen=max_size) # approx 1000 seconds of data- quite a lot of memory!
        self.measurer=Measurer(serial_port=serial_port)
        self.running=True
        self.now_stopped=False

    def run(self):
        while self.running:
            r=self.measurer.get_reading_set()
            self.dataset.append(r)
            logging.debug(r)
            time.sleep(0.3)

        logging.info("in process of stopping")
        self.measurer.close()
        self.now_stopped=True

    def stop(self):
        self.running=False
        logging.info("Stop recieved, waiting for stop to happen")
        while not self.now_stopped:
            time.sleep(0.1)

    def get_dollop_json(self):
        """
            Return a string that is a
            json list of readings
            taken from the buffer
            should be threadsafe ;-)
        """
        bits:list[str]=["["]
        while len(self.dataset)>0:
            bits.append(self.dataset.popleft().to_json()+",")
        bits.append("]")
        return "".join(bits)

    def get_latest(self):
        """
            return a string (JSON) of the most recent reading
            as a single object
        """
        latest:str=self.dataset[-1].to_json()
        return latest




if __name__=="__main__":
    rc=ReadingCollector("COM4")
    time.sleep(1)
    rc.start()
    time.sleep(2)
    js=rc.get_dollop_json()
    print(js)
    with open("temp.js","w") as outfile:
        outfile.write(js)
    time.sleep(1)
    rc.stop()









