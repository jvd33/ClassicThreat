#!/bin/bash

cd backend
$(aws ecr get-login --no-include-email --region us-east-1)
echo 'Building...' && docker build -t classicthreat-api .
echo 'Tagging...' && docker tag classicthreat-api:latest 093651261482.dkr.ecr.us-east-1.amazonaws.com/classicthreat-api:latest
echo 'Pushing...' && docker push 093651261482.dkr.ecr.us-east-1.amazonaws.com/classicthreat-api:latest
echo 'Success!'

