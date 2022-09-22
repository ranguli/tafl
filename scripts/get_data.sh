#!/usr/bin/env bash

echo "Downloading data"
wget -nc https://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip

echo "Unzipping data"
if [ ! -f "TAFL_LTAF.csv" ]; then
    unzip TAFL_LTAF.zip
fi
