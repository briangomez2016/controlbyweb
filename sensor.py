"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp


