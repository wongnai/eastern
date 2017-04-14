#!/usr/bin/env python2.7
import sys
import deploy_project
import os
import subprocess

if (len(sys.argv) != 4):
    print("""Invalid parameters provided
    Usage:
        ./deploy.py namespace project-name image-tag""")
    exit(1)

try:
    deploy_project.deploy(sys.argv[1], sys.argv[2], sys.argv[3])
except subprocess.CalledProcessError as err:
    print(err)
    exit(err.returncode)