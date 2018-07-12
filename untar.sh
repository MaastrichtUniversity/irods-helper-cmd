#!/bin/sh
# Author Matthew Saum
# Copyright 2018 SURFsara BV
# Apache License 2.0

# This is to allow iRODS to untar very large tarball files.
# Currently iRODS does not unpack tarballs over ~10GB (varies).
# It will be called via the untar rule, and triggered to run
# on the resource object server where the tarball has been moved to.

# Best practice: make sure this exists on all servers.
# In the rule: msiExecCmd("untar.sh", "tarPath tarDir", "resourceServer", "", *returnCode);

# Then we untar into the correct location

/bin/tar -xf $1 -C $2