#!/usr/bin/python3

import ldap
import struct
import sys

def byte_to_str_sid(binary):
    version = struct.unpack('B', binary[0:1])[0]
    assert version == 1, version
    length = struct.unpack('B', binary[1:2])[0]
    authority = struct.unpack(b'>Q', b'\x00\x00' + binary[2:8])[0]
    string = 'S-%d-%d' % (version, authority)
    binary = binary[8:]
    assert len(binary) == 4 * length
    for i in range(length):
        value = struct.unpack('<L', binary[4*i:4*(i+1)])[0]
        string += '-%d' % value
    return string

def read_ldap_credentials():
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

print(byte_to_str_sid(rawSid))