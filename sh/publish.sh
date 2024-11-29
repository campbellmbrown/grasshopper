#!/bin/bash

rm -rf dist build stassh.spec resources/GIT_SHA
git rev-parse --short=8 HEAD > resources/GIT_SHA
pyinstaller --onefile --noconsole --add-data "resources;resources" stassh.py
