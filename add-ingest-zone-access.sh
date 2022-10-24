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

    # Set all rights except special permissions and full control, also let them inherit
    /usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI|CI/CHANGE" $2

    exit 0
else
    exit 0
fi
