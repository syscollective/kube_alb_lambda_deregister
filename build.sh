#!/bin/bash

pip3 install --target ./ kubernetes 
zip -r lambda_deregister.zip * -x lambda_deregister.zip -x README.md -x build.sh
