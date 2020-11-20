from homeassistant.components.switch import SwitchEntity
import requests, pickle
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time

from requests import Session
import logging

_LOGGER = logging.getLogger(__name__)


cliente = None

class Auth:
    """Class to make authenticated requests."""
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Auth.__instance == None:
            Auth("https://controlbyweb.cloud/", "amenoni","MeteoTec")
        return Auth.__instance

    def __init__(self,host: str, usr: str , passw: str): 
        """Initialize the auth."""
        self.host = host
        self.usr = usr
        self.passw = passw
        if Auth.__instance != None:
           print("Clase ya instanciada")
           return
        else:
            Auth.__instance = self
        s = requests.session()
        r = s.get(self.host+"login") 
        soup = BeautifulSoup(r.text, 'lxml')
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        #print(csrf_token)
        print("Primera sesion")
        global login_data    
        login_data = dict(_token=csrf_token , username=self.usr, password=self.passw, next='/')
        s.post(self.host+"login", data=login_data, headers=dict(Referer=self.host))  
        with open('cookiesession', 'wb') as f:
            pickle.dump(s.cookies, f)
        
    def getSession(self, **kwargs) -> requests.session():
        s = requests.session()
        s.cookies.clear()
        r = s.get(self.host+"login") 
        soup = BeautifulSoup(r.text, 'lxml')
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        print(csrf_token)
        global login_data    
        login_data = dict(_token=csrf_token , username=self.usr, password=self.passw, next='/')
        s.post(self.host+"login", data=login_data, headers=dict(Referer=self.host))  
        with open('cookiesession', 'wb') as f:
            pickle.dump(s.cookies, f)
            return False  

    def request(self, path: str) -> requests.session():   
        try:   
            session = requests.session()  # or an existing session
            with open('cookiesession', 'rb') as f:
                session.cookies.update(pickle.load(f))
            res =  session.get(self.host+path, headers=login_data , auth=('amenoni', 'webrelay'))
            #print(res.text) 
            if(res.text.find("/devices/unavailable") == -1):
                return res
            else:
                return "unavailable"
        except requests.exceptions.RequestException as e:  
            _LOGGER.error(e)
            return False

class API:
    """Class to communicate with the ExampleHub API."""
    __instance = None
    @staticmethod 
    def getInstance():
      """ Static access method. """
      if API.__instance == None:
        API(Auth.getInstance())
      return API.__instance
       
    def __init__(self, auth: Auth):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = auth

    def initsession(self):
        self.auth.getSession()
        

    def cambiarEstado(self,path:str):
        res = self.auth.request(path)
        if(res == "unavailable"):
            return None
        return res 

    def verEstado(self,path:str,device:str):
        res = self.auth.request(path) if self.auth.request(path) != False else False
        if (res == False ):
            _LOGGER.error("Dispositivo no disponible")
            return "errEstado"
        if(res == "unavailable"):
            _LOGGER.error("No hay conexion con controlbyweb ")
            return None
        soup2 = BeautifulSoup(res.text, 'lxml')
        if(soup2.select_one(device)==None):
            print("Error al iniciar Sesión") 
            _LOGGER.error("Error al iniciar Sesión") 
            return "errEstado"
        #_LOGGER.error("Error al iniciar Sesión") 
        #if(soup2.select_one(device) == None):
        #    
        if (res != False):
            estado = True
            if (soup2.select_one(device).text == "0"):
                estado = False
            return  estado
        else:
            return "errEstado"

    def async_fetch_state(self,serial,device):
        estado = self.verEstado("devices/"+str(serial)+"/state.xml?",device)
        return estado        
