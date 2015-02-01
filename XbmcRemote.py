from RPi import GPIO
import time, os, httplib, json, requests, pdb
import subprocess
from requests.auth import HTTPBasicAuth
GPIO.setmode(GPIO.BCM)

GPIO_PLAY = 14
GPIO_FORWARD = 15
GPIO_BACKWARD = 18
GPIO_SHUTDOWN = 17

def main():
    buttons = [GPIO_PLAY, GPIO_FORWARD, GPIO_BACKWARD, GPIO_SHUTDOWN]
    numbuttons = len(buttons)
    index = 0
    for index in range(numbuttons):
        GPIO.setup(buttons[index], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(buttons[index], GPIO.RISING, bouncetime=200)
    while True:
        index = 0
        for index in range(numbuttons):
            if GPIO.event_detected(buttons[index]):
                time_pressed = time.time()
                GPIO.wait_for_edge(buttons[index], GPIO.FALLING)
                time_released = time.time()
                GPIO.remove_event_detect(buttons[index])
                if (time_released - time_pressed) >= 3:
                    button_hold(buttons[index])
                else:
                    button_pressed(buttons[index])
                GPIO.add_event_detect(buttons[index], GPIO.RISING, bouncetime=200)
        time.sleep(0.01)

def button_pressed(button):
    #excute action if button pressed once
    url = 'http://192.168.1.5:80/jsonrpc'
    postheaders = {'content-type': 'application/json'}
    command = {"jsonrpc":"2.0", "id": "AudioGetItem", "method": "", "params": {}}
    if button == GPIO_PLAY:
        play(url, postheaders)
        print("play")
    elif button == GPIO_FORWARD:
        command['method'] = 'Player.GoTo'
        command['params'] = {"playerid": 0, "to": "next"}
        print("forward")
    elif button == GPIO_BACKWARD:
        command['method'] = 'Player.GoTo'
        command['params'] = {"playerid": 0, "to": "previous"}
        print("bakward")
    resp = requests.post(url, auth=('xbmc','xbmc'), data=json.dumps(command), headers=postheaders)

def button_hold(button):
    #execute action on button pressed and hold more than 3secs
    url = 'http://192.168.1.5:80/jsonrpc'
    postheaders = {'content-type': 'application/json'}
    command = {"jsonrpc":"2.0", "id": "AudioGetItem", "method": ""}
    if button == GPIO_SHUTDOWN:
        command['method'] = 'System.Shutdown'
        print("shutting down")
    resp = requests.post(url, auth=('xbmc','xbmc'), data=json.dumps(command), headers=postheaders)

def play(url, postheaders):
    #Play a cd if not playing, otherwithe play or pause cd
    command = {"jsonrpc":"2.0", "id": "AudioGetItem", "method": "", "params": {}}
    command['method'] = 'Player.GetItem'
    command['params'] = {"properties":["file"], "playerid": 0}
    resp = requests.get(url, auth=('xbmc','xbmc'), params={"request":json.dumps(command)})
    reponse = json.loads(resp.text)
    
    if reponse.get("error", None):
        command = {"jsonrpc":"2.0", "id": "AudioGetItem", "method": "", "params": {}}
        command['method'] = 'Player.Open'
        command['params'] = {"item": {"directory": "cdda://"} }
    else:
        command['method'] = 'Player.PlayPause'
        command['params'] = {"playerid": 0}
    resp = requests.post(url, auth=('xbmc','xbmc'), data=json.dumps(command), headers=postheaders)


if __name__ == '__main__':
    main()
