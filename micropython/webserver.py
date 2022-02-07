from time import sleep
import json
from wlan import connect
import uasyncio
from nanoweb import Nanoweb
import sensors
from html_functions import naw_write_http_header, render_template

sta_if = connect()

naw = Nanoweb()

data = dict(
    bmp = dict(temperature=0, pressure=0),
    ccs = dict(tvoc=0, eco2=0),
    hdc = dict(temperature=0, humidity=0),
    )
    
@naw.route("/")
def index(request):
    naw_write_http_header(request)
    html = render_template(
        'index.html',
        temperature_bmp=str(data['bmp']['temperature']),
        pressure=str(data['bmp']['pressure']),
        tVOC=str(data['ccs']['tvoc']),
        eCO2=str(data['ccs']['eco2']),
        temperature_hdc=str(data['hdc']['temperature']),
        humidity=str(data['hdc']['humidity']),
        )
    await request.write(html)


@naw.route("/api/data")
def api_data(request):
    naw_write_http_header(request, content_type='application/json')
    await request.write(json.dumps(data))


loop = uasyncio.get_event_loop()
loop.create_task(sensors.collect_sensors_data(data, True))
loop.create_task(naw.run())

loop.run_forever()
    

