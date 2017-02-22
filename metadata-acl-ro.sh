#!/bin/bash
source /etc/secrets

set -e

# Strip domain name of the username
user=$(echo $1 | cut -f1 -d"@")
# Get the token from the full path to the ingest zone

token=$(basename $2)

# Call MirthConnect to deny CIFS rights on metadata.xml file
curl --max-time 5 --fail --user $INGEST_MIRTHACL_USER:$INGEST_MIRTHACL_PASSWORD "http://${INGEST_MIRTHACL_URL}/?token=${token}&metadatafile=metadata.xml&user=${user}"

exit $?
