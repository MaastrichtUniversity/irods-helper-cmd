#!/bin/bash
source /etc/secrets/secrets

set -e

# Strip domain name of the username
user=$(echo $1 | cut -f1 -d"@")
domain=$(echo $1 | cut -f2 -d"@")

# Determine the organisation from the domain from e-mail
if [ $domain == "maastrichtuniversity.nl" ]; then
    org="UM"
elif [ $domain == "mumc.nl" ]; then
    org="AZM"
else
    echo "ERROR: Unknown organisation"
    exit 1
fi

# First obtain the sid
sid=$($(dirname "$0")/name-to-sid.py $user $org)

if [ -z "$sid" ]; then
	exit 1
fi

# Creates the token directory + empty metadata.xml file
mkdir $2
touch $2/metadata.xml

# Set all rights except special permissions and full control, also let them inherit
/usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI|CI/CHANGE" $2
/usr/bin/setcifsacl -a "ACL:${sid}:ALLOWED/OI/READ" $2/metadata.xml

exit 0
