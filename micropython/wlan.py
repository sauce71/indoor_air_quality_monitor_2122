import network

SSID = 'VG3Data'
PASSWORD = 'Admin:1234'

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)

        while sta_if.isconnected() == False:
          pass
        print('Connection successful')
    else:
        print('Already connected!')
    print(sta_if.ifconfig())
    return sta_if
