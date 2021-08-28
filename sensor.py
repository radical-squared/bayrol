"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

import requests
import json
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup

import re



URL_LOGIN="https://www.bayrol-poolaccess.de/webview/p/login.php"
URL_PLANTS="https://www.bayrol-poolaccess.de/webview/p/plants.php"
URL_GETDATA="https://www.bayrol-poolaccess.de/webview/getdata.php?cid="
URL_AJAX="https://www.bayrol-poolaccess.de/webview/data_json.php"


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([Bayrol(config)])


class Bayrol(Entity):
    """Representation of a Sensor."""

    def __init__(self, config):
        """Initialize the sensor."""
        self._state = None
        # self._hass = hass
        self._name = config['name']
        self._cid = config['cid']
        self._authuser = config['authuser']
        self._authpass = config['authpass']
        self._autodismiss = config['autodismiss']
        self._autodismiss_entity = config['autodismiss_entity']
        self._attributes = {}

        
        self._sid = requests.get(URL_LOGIN).headers['Set-Cookie'].split(";")[0].split("=")[1]

        # AUTHORIZE PHPSESSIONID
        self.cookie = dict(authpass=self._authpass,authuser=self._authuser,language="en",PHPSESSID=self._sid)
        s = requests.get(URL_PLANTS,cookies=self.cookie)

        self.get_params()
        self.get_errors()


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name  

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attributes["autodismiss"] = self.hass.states.is_state(self._autodismiss_entity,"on")
        self.get_params()
        self.get_errors()
        


    def dismiss_error(self, topic):
        cookie = dict(PHPSESSID=self._sid)
        dismiss_request = {
            "device":self._cid,
            "action":"setAction",
            "data":{"items":[{"topic":topic}]}
            }
        dissmiss_response  = requests.post(URL_AJAX, cookies = cookie, data = json.dumps(dismiss_request))

    def get_params(self):
        # GET DATA
        url = URL_GETDATA+str(self._cid)
        cookie = dict(PHPSESSID=self._sid)
        try:
            z = requests.get(url,cookies=cookie)
        except:
            # print(datetime.now().strftime("%H:%M:%S")+": requests error ")
            sleep(30)
            return
        # print(z.text)
        soup = BeautifulSoup(z.text, 'html.parser')
        mydivs = soup.find_all("div", {"class": re.compile(r"tab_box stat_")})
        if len(mydivs) == 0:
            print(z.text)
            return
        self._attributes['ph'] = mydivs[0].find_all('h1')[0].get_text()
        self._attributes['rx'] = mydivs[1].find_all('h1')[0].get_text()
        self._state = "Online" if z.status_code == 200 else "Offline" 
    
    def get_errors(self):
        cookie = dict(PHPSESSID=self._sid)
        getItems = {
            "device":self._cid,
            "action":"getItems",
            "data":{"items":["7.3","7.4","7.5","7.6","7.7","7.8","7.9","7.14","7.15","7.16","7.17","7.21","7.22","7.23"]}
        }
        items = requests.post(URL_AJAX,cookies=cookie, data = json.dumps(getItems)).json()

        dismissable = []

        for i in items['data']['items']:
            if i['topic'] == '10': 
                continue
            if i['value'] == 1:
                if i['function'] == 1:
                    dismissable.append(i['topic'])
                if i['topic'] in self._attributes:
                    continue
                else:
                    self._attributes[i['topic']] = i['name']  #datetime.now()
            else:
                if i['topic'] in self._attributes:
                    self._attributes.pop(i['topic'])
        
        if self._autodismiss:
            for d in dismissable:
                self.dismiss_error(d)
