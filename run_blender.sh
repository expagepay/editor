#!/bin/bash

# Simple wrapper to execute Blender in background mode using the generated
# script. Adjust the path to the Blender executable if necessary.

blender -b -P blender_script.py "$@"

