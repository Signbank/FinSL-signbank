#!/bin/bash

set -e
# Skip while testing
# python bin/openshift.py collectstatic --no-input
# python bin/openshift.py migrate
gunicorn --bind 0.0.0.0:8080 signbank.wsgi_openshift
