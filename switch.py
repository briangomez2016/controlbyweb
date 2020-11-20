from homeassistant.components.switch import SwitchEntity
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import logging

from .sesion import Auth, API
from requests import Session

_LOGGER = logging.getLogger(__name__)



def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    add_entities([MySwitch(hass,config['device'],config['nombre'],config['serial'])])
    
class MySwitch(SwitchEntity):
    def __init__(self,hass,device,nombre,serial):
        self._hass = hass
        self.serial = serial
        self.device = device
        #login_data = ""
        #self.api = api
        #client = api.getSession
        #self.client = client  
        #print(client)
        self._state = False
        self.nombre = nombre

    @property
    def name(self):
        """Name of the device."""
        return self.nombre

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
        api = API(auth)
        resp = api.cambiarEstado("devices/"+str(self.serial)+"/state.xml?"+self.device+"=1")
        if(resp == False):
            _LOGGER.warning("Creando otra sesion")
            auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
            api = API(auth)
            api.initsession()
            resp = api.cambiarEstado("devices/"+str(self.serial)+"/state.xml?"+self.device+"=0")
        if resp == None:
            self._state = None
        else: 
            if resp.ok == True : self._state = True

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
        api = API(auth)
        resp = api.cambiarEstado("devices/"+str(self.serial)+"/state.xml?"+self.device+"=0")
        if(resp == False):
            _LOGGER.warning("Creando otra sesion")
            auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
            api = API(auth)
            api.initsession()
            resp = api.cambiarEstado("devices/"+str(self.serial)+"/state.xml?"+self.device+"=0")
        if(resp == None):
            self._state = None
        else:
            if resp.ok == True : self._state = False

    def update(self):
        """Retrieve latest state."""
        auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
        api = API(auth)
        estado = api.async_fetch_state(self.serial,self.device) 
        if(estado == None):
            self._state = estado
        if(estado == "errEstado"):
            _LOGGER.warning("Creando otra sesion")
            auth = Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
            api = API(auth)
            api.initsession()
            estado = api.async_fetch_state(self.serial,self.device)
        self._state = estado
    

