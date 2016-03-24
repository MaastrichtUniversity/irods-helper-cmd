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

if len(sys.argv) == 1:
    sys.stderr.write("name-to-sid.py: Supply user as first argument \n")
    sys.exit(1)

l = ldap.initialize('ldap://ldap.maastrichtuniversity.nl')

l.protocol_version = ldap.VERSION3
l.simple_bind_s("CN=Irods (HML),OU=Hml-resources,OU=Users,OU=HML,OU=FHML,DC=unimaas,DC=nl", readLdapCredentials())

baseDN             = 'DC=unimaas,DC=nl'
searchScope        = ldap.SCOPE_SUBTREE
retrieveAttributes = ['objectSid']
searchFilter       = "sAMAccountName=%s" % sys.argv[1]

id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)

result_type, result = l.result(id, 0)

if not result_type == ldap.RES_SEARCH_ENTRY:
    sys.stderr.write("name-to-sid.py: User not found \n")
    sys.exit(1)

rawSid = result[0][1]['objectSid'][0]

print strsid(rawSid)
