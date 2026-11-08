#!/bin/bash
# SetupProject.sh
# WARNING: This script performs destructive operations.
# It deletes images/, tmp/, database/ImageEncryption.db, all __pycache__ dirs,
# and copies ~/Downloads/images to the project root.

set -euo pipefail

# Define project root
PROJECT_ROOT="/home/soumalya/Projects/Python/Image-Encryption"

# Define targets
IMAGES_FOLDER="${PROJECT_ROOT}/images"
TMP_FOLDER="${PROJECT_ROOT}/tmp"
DATABASE_FOLDER="${PROJECT_ROOT}/database"
DATABASE_FILE="${DATABASE_FOLDER}/ImageEncryption.db"
SOURCE_IMAGES="${HOME}/Downloads/images"

echo "Starting project setup..."

# STEP 1: Delete "images" folder
echo "Deleting images folder..."
if [ -d "${IMAGES_FOLDER}" ]; then
    rm -rf "${IMAGES_FOLDER}"
    echo "-> Deleted: ${IMAGES_FOLDER}"
else
    echo "-> Not found (skipped): ${IMAGES_FOLDER}"
fi

# STEP 2: Delete "tmp" folder
echo "Deleting tmp folder..."
if [ -d "${TMP_FOLDER}" ]; then
    rm -rf "${TMP_FOLDER}"
    echo "-> Deleted: ${TMP_FOLDER}"
else
    echo "-> Not found (skipped): ${TMP_FOLDER}"
fi

# STEP 3: Delete database file
echo "Deleting database file..."
if [ -f "${DATABASE_FILE}" ]; then
    rm -f "${DATABASE_FILE}"
    echo "-> Deleted: ${DATABASE_FILE}"
else
    echo "-> Not found (skipped): ${DATABASE_FILE}"
fi

# STEP 4: Remove all "__pycache__" directories
echo "Removing all __pycache__ directories..."
find "${PROJECT_ROOT}" -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
echo "-> Removed all __pycache__ directories under ${PROJECT_ROOT}"

# STEP 5: Copy images from Downloads
echo "Copying images from Downloads..."
if [ -d "${SOURCE_IMAGES}" ]; then
    cp -r "${SOURCE_IMAGES}" "${PROJECT_ROOT}/images"
    echo "-> Copied: ${SOURCE_IMAGES} -> ${PROJECT_ROOT}/images"
else
    echo "-> ERROR: Source folder not found: ${SOURCE_IMAGES}"
    exit 1
fi

echo "Project setup completed."
