#!/usr/bin/python

import ldap
import struct
import string
import sys

def strsid(byte):
    '''
    Convert bytes into a string SID
    byte - bytes to convert
    '''
    ret = 'S'
    sid = []
    sid.append(byteToLong(byte[0]))
    sid.append(byteToLong(byte[2:2+6], False))
    for i in range(8, len(byte), 4):
        sid.append(byteToLong(byte[i:i+4]))
    for i in sid:
        ret += '-' + str(i)
    return ret

def byteToLong(byte, little_endian=True):
    '''
    Convert bytes into a Python integer
    byte - bytes to convert
    little_endian - True (default) or False for little or big endian
    '''
    if len(byte) > 8:
        raise Exception('Bytes too long. Needs to be <= 8 or 64bit')
    else:
        if little_endian:
            a = string.ljust(byte, 8, '\x00')
            return struct.unpack('<q', a)[0]
        else:
            a = string.rjust(byte, 8, '\x00')
            return struct.unpack('>q', a)[0]

def readLdapCredentials():
    with open("/etc/secrets") as f:
        for line in f:
            if line.startswith('LDAP_PASSWORD='):
                password = line[line.index('=') + 1:]

    return (password.strip())

if len(sys.argv) == 0:
    sys.stderr.write("name-to-sid.py: ERROR: Supply user as first argument \n")
    sys.exit(1)

voPersonExternalID = sys.argv[1]
userSplit = voPersonExternalID.split('@')
userName = userSplit[0]
# Change domain to lowercase to make it compatible with domains written in uppercase, lowercase or combinations thereof
domain = userSplit[1].lower()


# Make distinction between UM- and AZM-LDAP server
if domain == "unimaas.nl":
    l = ldap.initialize('ldap://ldap.maastrichtuniversity.nl')

    l.protocol_version = ldap.VERSION3
    l.simple_bind_s("CN=Rit-dev (FACBURFHML),OU=Resources,OU=Users,OU=FACBURFHML,OU=FHML,DC=unimaas,DC=nl", readLdapCredentials())

    baseDN             = 'DC=unimaas,DC=nl'
    searchScope        = ldap.SCOPE_SUBTREE
    retrieveAttributes = ['objectSid']
    # Search for the username or P-number
    searchFilter       = "sAMAccountName=%s" % userName
elif domain == "mumc.nl":
    l = ldap.initialize('ldap://a.corp')

    l.protocol_version = ldap.VERSION3
    l.simple_bind_s("CN=SASritmumcacc,OU=Power Users,OU=Accounts,DC=A,DC=CORP", readLdapCredentials())

    baseDN             = 'DC=a,DC=corp'
    searchScope        = ldap.SCOPE_SUBTREE
    retrieveAttributes = ['objectSid']
    # Search for the G-number
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

print strsid(rawSid)
