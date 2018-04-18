#!/bin/bash

# Break on error
set -e

# First fix permissions so that we can always delete the files in a drop zone, in case files were made read-only
chmod -R 755 $1

# Then delete its contents and the directory
rm -rf $1

exit 0
