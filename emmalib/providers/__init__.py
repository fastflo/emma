emma_registered_providers = []

import mysql
import sqlite

from Connection import Connection
from Connections import Connections


def check_provider(provider_name):
    return provider_name in emma_registered_providers