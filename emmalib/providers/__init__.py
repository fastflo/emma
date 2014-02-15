
emma_registered_providers = []

# print "before import", emma_registered_providers

import mysql
import sqlite

# print 'after import', emma_registered_providers


def check_provider(provider_name):
    return provider_name in emma_registered_providers