#!/bin/sh

set -e

# Enables an ingest zone for a certain user by setting the cifs acl. First obtain the sid

sid=$($(dirname "$0")/name-to-sid.py $1)

if [ -z "$sid" ]; then
	exit 1
fi

mkdir $2

# Set all rights except special permissions and full control, also let them inherit
# Versions of setcifsacl that I tested would always return a non zero return code, even on success
set +e
/usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI|CI/CHANGE" $2

exit 0
