#!/bin/bash

BASE=~/iot/requirements-base.txt

# Inline full requirements for analytics processor
cat "$BASE" > ~/iot/analytics-processor-v2/requirements.txt
echo -e "\n# Additional dependencies specific to analytics processor" >> ~/iot/analytics-processor-v2/requirements.txt
echo "databases[postgresql]==0.8.0" >> ~/iot/analytics-processor-v2/requirements.txt
echo "python-multipart==0.0.6" >> ~/iot/analytics-processor-v2/requirements.txt

echo "✅ Generated full analytics-processor-v2/requirements.txt"