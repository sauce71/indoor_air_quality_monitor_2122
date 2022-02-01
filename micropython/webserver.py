import gc
from time          import sleep
from machine import Pin, I2C
from wlan import connect
from micropython import mem_info
import uasyncio
from nanoweb import Nanoweb
from BME280 import BME280
from CCS811 import CCS811
from hdc1080 import HDC1080


i2c = I2C(1, scl=Pin(22), sda=Pin(21))
bmp = BME280(i2c=i2c)
ccs = CCS811(i2c=i2c)
hdc = HDC1080(i2c=i2c)


sta_if = connect()

naw = Nanoweb()

    data = dict(
        bmp = dict(temperature=0, pressure=0),
        ccs = dict(tvoc=0, eco2=0),
        hdc = dict(temperature=0, humidity=0),
        )

gc.collect()



def http_write_header(request, content_type='text/html'):
    """
    HTTP Header
    Content types:
    json: application/json
    """
    await request.write("HTTP/1.1 200 OK\r\n".format(content_type))
    await request.write("Content-Type: {}\r\n\r\n")
    
@naw.route("/")
def index(request):
    http_write_header(request)    
    await request.write("Hello World")

loop = uasyncio.get_event_loop()
loop.create_task(naw.run())
loop.run_forever()
    

