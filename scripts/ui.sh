#!/bin/bash

cd tps-calc-ui
$(aws ecr get-login --no-include-email --region us-east-1)
echo 'Building...' && docker build . -t classicthreat-ui
echo 'Tagging...' && docker tag classicthreat-ui:latest 093651261482.dkr.ecr.us-east-1.amazonaws.com/classicthreat-ui:latest
echo 'Pushing...' && docker push 093651261482.dkr.ecr.us-east-1.amazonaws.com/classicthreat-ui:latest
echo 'Success!'

