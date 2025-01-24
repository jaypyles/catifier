#!/bin/bash

if [ -f $GOOGLE_APPLICATION_CREDENTIALS ]; then
    gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
fi

if [ "$APP_MODE" = "dev" ]; then
    pdm run python -m uvicorn src.catifier.app:app --reload --host 0.0.0.0 --port 8000
else
    pdm run python -m uvicorn src.catifier.app:app --host 0.0.0.0 --port 8000
fi
