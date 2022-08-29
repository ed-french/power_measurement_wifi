



###########################################################################
#                                                                         #
#                                                                         #
#                                                                         #
#                      Streaming electical power monitor                  #
#                                                                         #
#                                                                         #
#                                                                         #
###########################################################################




# Monitor's power consumption at approx 3Hz and the server then collects
# batches of that data in a single collection
# by providing a time-based sample of recent readings 


"""

Requirements
============

To set up on raspi use pip install -r requirements.txt
Also instructions at : https://www.piddlerintheroot.com/pzem-004t/ to set up serial port

Serial port came out as needing /dev/ttyUSB0 as the serial port for it to work
Also, you need to change the port, e.g. to 8080 for it to work on the raspberrypi
In my case: http://192.168.1.193:8080 

"""


import logging

from make_measurements import Measurer
logging.basicConfig(level=logging.DEBUG)

from flask import Flask,Response
from measurement_thread import ReadingCollector



def render_info_page():
    return """
    <h1> Leccy monitor </h1>

    Use /leccy to retreive recent readings as json list<br />

    Use /stop to shut down the measurement thread <br />

    Use /get_latest to get the most recent reading

    <table>
    <tr>
        <th>Timestamp</th><td id="timestamp"></td>
    </tr><tr>
        <th>Voltage</th><td id="voltage"></td>
    </tr><tr>
        <th>Current</th><td id="current"></td>
    </tr><tr>
        <th>Power</th><td id="power"></td>
    </tr><tr>
        <th>P.F.</th><td id="power_factor"></td>
    </tr>
    </table>


    <script>

    function update()
    {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function()
        {
            if (this.readyState == 4 && this.status == 200)
            {
                var resp=xhttp.responseText;
                var results=JSON.parse(resp);
                document.getElementById("timestamp").innerHTML =results.timestamp;
                document.getElementById("voltage").innerHTML =results.voltage;
                document.getElementById("current").innerHTML =results.current;
                document.getElementById("power").innerHTML =results.power;
                document.getElementById("power_factor").innerHTML =results.power_factor;
            }
        };
        xhttp.open("GET", "/get_latest", true);
        xhttp.send();
        window.setTimeout(update,250);
    }
    window.setTimeout(update,1000);
    </script>
    """


def render_json_dataset():
    resp:Response=Response(measure_thread.get_dollop_json(),mimetype="application/json")
    return resp

def stop_measurment():
    measure_thread.stop()

def get_latest():
    return Response(measure_thread.get_latest(),mimetype="application/json")






if __name__=="__main__":

    measure_thread:ReadingCollector=ReadingCollector(serial_port="COM4") # ***** GLOBAL *****
    measure_thread.start()

    flaskapp=Flask(__name__)
    flaskapp.add_url_rule("/","home",render_info_page)
    flaskapp.add_url_rule("/leccy","leccy",render_json_dataset)
    flaskapp.add_url_rule("/stop","stop",stop_measurment)
    flaskapp.add_url_rule("/get_latest","get latest",get_latest)


    flaskapp.run(host="0.0.0.0",port=80)

