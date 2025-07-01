#!/bin/bash

# -----------------------------------------------------------------------------
# archive_and_timestamp_legacy_files.sh
#
# This script scans ~/iot for legacy/dev backup files with names containing:
#   - *.bak*  *.broken*  *.disabled*  *.corrupted*  *.backup*
#
# All matched files are archived to:
#   ~/iot/backups/iot_legacy_files_<UTC_TIMESTAMP>.tar.gz
#
# After archiving, the user is shown a list of the files and prompted whether
# they want to permanently delete the originals.
# -----------------------------------------------------------------------------

BASE_DIR=~/iot
BACKUP_DIR=~/iot/backups
UTC_TIMESTAMP=$(date -u +"%Y-%m-%d_%H-%M")
ARCHIVE_NAME="iot_legacy_files_$UTC_TIMESTAMP.tar.gz"
OUTPUT_TAR="$BACKUP_DIR/$ARCHIVE_NAME"
LEGACY_LIST=$(mktemp)

mkdir -p "$BACKUP_DIR"

# Search for legacy files
find "$BASE_DIR" -type f \( \
  -name "*.bak*" -o \
  -name "*.broken*" -o \
  -name "*.disabled*" -o \
  -name "*.corrupted*" -o \
  -name "*.backup*" \
\) > "$LEGACY_LIST"

NUM_FILES=$(wc -l < "$LEGACY_LIST")
echo "📦 Found $NUM_FILES legacy files to archive."

if [ "$NUM_FILES" -eq 0 ]; then
  echo "⚠️  No files found. Exiting."
  rm "$LEGACY_LIST"
  exit 0
fi

# Create archive
tar -czf "$OUTPUT_TAR" -T "$LEGACY_LIST" --transform "s|^$BASE_DIR/||"
echo "✅ Archive created: $OUTPUT_TAR"
echo

# Display file list
echo "📄 Archived Files:"
nl "$LEGACY_LIST"
echo

# Prompt user to confirm deletion
read -rp "❓ Do you want to delete the original files listed above? Type 'yes' to confirm: " CONFIRM
if [ "$CONFIRM" = "yes" ]; then
  echo "🗑️ Deleting original files..."
  xargs rm -v < "$LEGACY_LIST"
  echo "✅ Files deleted."
else
  echo "🚫 Files not deleted."
fi

# Clean up temp file
rm "$LEGACY_LIST"