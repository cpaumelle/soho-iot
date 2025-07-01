#!/bin/bash
echo "=== IoT CODEBASE REVIEW ===" > review.txt
echo "Generated: $(date)" >> review.txt
echo "" >> review.txt

# Main files
echo "=== DOCKER COMPOSE ===" >> review.txt
cat docker-compose.yml >> review.txt
echo "" >> review.txt

echo "=== ENVIRONMENT ===" >> review.txt
cat .env >> review.txt
echo "" >> review.txt

echo "=== CADDY CONFIG ===" >> review.txt
cat unified-caddyfile >> review.txt
echo "" >> review.txt

echo "=== DOCKERFILES ===" >> review.txt
find . -name "Dockerfile" | while read f; do
  echo "FILE: $f" >> review.txt
  cat "$f" >> review.txt
  echo "" >> review.txt
done

echo "=== PYTHON MAIN FILES ===" >> review.txt
find . -name "main.py" | while read f; do
  echo "FILE: $f" >> review.txt
  cat "$f" >> review.txt
  echo "" >> review.txt
done

echo "=== CONFIG FILES ===" >> review.txt
find . -name "config.py" -o -name "requirements.txt" | while read f; do
  echo "FILE: $f" >> review.txt
  cat "$f" >> review.txt
  echo "" >> review.txt
done
