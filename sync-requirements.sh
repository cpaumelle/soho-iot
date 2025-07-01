#!/bin/bash
BASE=~/iot/requirements-base.txt

# Analytics Processor
cat "$BASE" > ~/iot/analytics-processor-v2/requirements.txt
echo -e "\n# Additional dependencies specific to analytics processor" >> ~/iot/analytics-processor-v2/requirements.txt
echo "databases[postgresql]==0.8.0" >> ~/iot/analytics-processor-v2/requirements.txt
echo "python-multipart==0.0.6" >> ~/iot/analytics-processor-v2/requirements.txt
echo "✅ Generated analytics-processor-v2/requirements.txt"

# Device Manager
cp "$BASE" ~/iot/device-manager/requirements.txt
echo "✅ Generated device-manager/requirements.txt"

# Ingest Service
cp "$BASE" ~/iot/ingest-server/requirements.txt
echo "✅ Generated ingest-server/requirements.txt"
