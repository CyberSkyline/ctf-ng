#!/bin/bash

## Install plugins deps on load
for d in CTFd/plugins/*; do
    if [ -f "$d/requirements.txt" ]; then
        pip install --no-cache-dir -r "$d/requirements.txt";
    fi;
done;


python serve_debug.py
