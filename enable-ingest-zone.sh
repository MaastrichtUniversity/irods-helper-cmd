#!/bin/bash
set -e

source /etc/secrets

if [ "${USE_SAMBA}" = "true" ] ; then
    voPersonExternalID=$1

    # First obtain the sid
    sid=$($(dirname "$0")/name-to-sid.py $voPersonExternalID)
    
    if [ -z "$sid" ]; then
        exit 1
    fi
    
    # Creates the token directory + empty schema.json+instance.json files
    mkdir $2
    touch $2/instance.json
    touch $2/schema.json
    
    # Set all rights except special permissions and full control, also let them inherit
    /usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI|CI/CHANGE" $2
    /usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI/READ" $2/instance.json
    /usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI/READ" $2/schema.json
    
    exit 0
else
    # Creates the token directory + empty schema.json+instance.json files
    mkdir $2
    touch $2/instance.json
    touch $2/schema.json
    exit 0
fi
