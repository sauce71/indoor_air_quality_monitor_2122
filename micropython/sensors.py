import gc
from time          import sleep
from machine import Pin, I2C
import uasyncio
from BME280 import BME280
from CCS811 import CCS811
from hdc1080 import HDC1080


i2c = I2C(1, scl=Pin(22), sda=Pin(21))
bmp = BME280(i2c=i2c)
ccs = CCS811(i2c=i2c, addr=90)
hdc = HDC1080(i2c=i2c)

readings_bmp_temperature = []
readings_bmp_pressure = []
readings_ccs_tvoc = [0,] # Tar litt tid før det kommer data fra ccs811
readings_ccs_eco2 = [0,] # Initaliserer med en 0 verdi og sjekker at det ikke er 0 før append
readings_hdc_humidity = []
readings_hdc_temperature = []

async def read_bmp():
    temperature = bmp.read_temperature() / 100
    pressure = bmp.read_pressure() / 25600
    return temperature, pressure


async def read_ccs():
    if ccs.data_ready():
        tvoc = ccs.tVOC
        eco2 = ccs.eCO2
        return tvoc, eco2
    else:
        return 0, 0
    
    
async def read_hdc():
    humidity = hdc.read_humidity()
    temperature = hdc.read_temperature(celsius=True)
    return humidity, temperature

def _pop0(l):
    if len(l) >= 60:
        l.pop(0)

def _mid(l):
    return sorted(l)[len(l)//2]
    

async def update_sensors_data(data):
    global readings_bmp_temperature
    global readings_bmp_pressure
    global readings_ccs_tvoc
    global readings_ccs_eco2
    global readings_hdc_humidity
    global readings_hdc_temperature
    
    temperature, pressure = await read_bmp()
    readings_bmp_pressure.append(pressure)
    readings_bmp_temperature.append(temperature)
  
    tvoc, eco2 = await read_ccs()
    if eco2:
        readings_ccs_tvoc.append(tvoc)
        readings_ccs_eco2.append(eco2)
    uasyncio.sleep_ms(1)
    
    humidity, temperature = await read_hdc()
    readings_hdc_humidity.append(humidity)
    readings_hdc_temperature.append(temperature)
 
    _pop0(readings_bmp_temperature)
    _pop0(readings_bmp_pressure)
    _pop0(readings_ccs_tvoc)
    _pop0(readings_ccs_eco2)
    _pop0(readings_hdc_humidity)
    _pop0(readings_hdc_temperature)
     
    data['bmp']['temperature'] = _mid(readings_bmp_temperature)
    data['bmp']['pressure'] = _mid(readings_bmp_pressure)
    data['ccs']['tvoc'] = _mid(readings_ccs_tvoc)
    data['ccs']['eco2'] = _mid(readings_ccs_eco2)
    data['hdc']['humidity'] = _mid(readings_hdc_humidity)
    data['hdc']['temperature'] = _mid(readings_hdc_temperature)


async def collect_sensors_data(data, test=False):    
    while True:
        await update_sensors_data(data)
        if test:
            print(data)
    
        await uasyncio.sleep_ms(5000)

def test():
    data = dict(
        bmp = dict(temperature=0, pressure=0),
        ccs = dict(tvoc=0, eco2=0),
        hdc = dict(temperature=0, humidity=0),
        )
    loop = uasyncio.get_event_loop()
    loop.create_task(collect_sensors_data(data, True))
    loop.run_forever()

if __name__ == '__main__':
    test()
    