"""
Functionality for working with Telegram
"""

from libdev.cfg import cfg
from tgio import Telegram


tg = Telegram(cfg('tg.token'))
