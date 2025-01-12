#!/bin/bash

if [ -f $GOOGLE_APPLICATION_CREDENTIALS ]; then
    gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
fi

pdm run python src/catifier/app.py