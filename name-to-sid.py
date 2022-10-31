#!/usr/bin/python

import ldap
import struct
import string
import sys

def byte_to_str_sid(byte):
    """
    Convert bytes into a string SID
    byte - bytes to convert
    """
    ret = 'S'
    sid = []
    sid.append(byte_to_long(byte[0]))
    sid.append(byte_to_long(byte[2:2+6], False))
    for i in range(8, len(byte), 4):
        sid.append(byte_to_long(byte[i:i+4]))
    for i in sid:
        ret += '-' + str(i)
    return ret

def byte_to_long(byte, little_endian=True):
    """
    Convert bytes into a Python integer
    byte - bytes to convert
    little_endian - True (default) or False for little or big endian
    """
    if len(byte) > 8:
        raise Exception('Bytes too long. Needs to be <= 8 or 64bit')
    else:
        if little_endian:
            a = string.ljust(byte, 8, '\x00')
            return struct.unpack('<q', a)[0]
        else:
            a = string.rjust(byte, 8, '\x00')
            return struct.unpack('>q', a)[0]

def read_ldap_credentials():
    """

    """
    with open("/etc/secrets") as f:
        for line in f:
            if line.startswith('LDAP_PASSWORD='):
                ldap_password = line[line.index('=') + 1:].strip()
            elif line.startswith('LDAP_USER='):
                ldap_user = eval(line[line.index('=') + 1:].strip())
            elif line.startswith('LDAP_URL='):
                ldap_url = line[line.index('=') + 1:].strip()
            elif line.startswith('LDAP_DOMAIN='):
                ldap_domain = line[line.index('=') + 1:].strip()

    return ldap_user, ldap_domain, ldap_password, ldap_url

if len(sys.argv) == 0:
    sys.stderr.write("name-to-sid.py: ERROR: Supply user as first argument \n")
    sys.exit(1)

voPersonExternalID = sys.argv[1]
userSplit = voPersonExternalID.split('@')
userName = userSplit[0]
# Change domain to lowercase to make it compatible with domains written in uppercase, lowercase or combinations thereof
domain = userSplit[1].lower()

# Get LDAP credentials from secrets file
ldap_user, ldap_domain, ldap_password, ldap_url = read_ldap_credentials()

if domain == "unimaas.nl" or domain == "mumc.nl":
    l = ldap.initialize(ldap_url)

    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(ldap_user, ldap_password)

    baseDN             = ldap_domain
    searchScope        = ldap.SCOPE_SUBTREE
    retrieveAttributes = ['objectSid']
    # Search for the username or P-number (or if azM: G-number)
    searchFilter       = "sAMAccountName=%s" % userName
else:
    sys.stderr.write("name-to-sid.py: ERROR: Unknown domain "+domain+" from voPersonExternalID. Expected \"unimaas.nl\" or \"mumc.nl\"\n")
    sys.exit(1)

# Perform the LDAP search
id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)

result_type, result = l.result(id, 0)

if not result_type == ldap.RES_SEARCH_ENTRY:
    sys.stderr.write("name-to-sid.py: User not found \n")
    sys.exit(1)

rawSid = result[0][1]['objectSid'][0]

print byte_to_str_sid(rawSid)
