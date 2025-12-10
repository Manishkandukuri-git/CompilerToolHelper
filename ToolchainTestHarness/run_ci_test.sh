#!/bin/bash
# Simulates a Jenkins/GitLab CI job for Toolchain Validation and Release

set -e # Exit immediately if a command exits with a non-zero status

BUILD_GENERATOR="ninja"
PROJECT_DIR=$(pwd)
REPORT_FILE="validation_report.json"
INSTALL_DIR="${PROJECT_DIR}/release_artifacts" # Local directory for staging release artifacts

echo "=========================================================="
echo "CI JOB START: Toolchain Integrity and Performance Test"
echo "=========================================================="

# 1. Run the main Python validation script (this executes O0 and O3 builds)
echo "--- Running Automated Validation Harness (${BUILD_GENERATOR}) ---"
python3 configure.py --generator "${BUILD_GENERATOR}"
VALIDATION_EXIT_CODE=$?

# 2. Check the validation result from the Python script's exit code
if [ $VALIDATION_EXIT_CODE -ne 0 ]; then
    echo "=========================================================="
    echo "❌ CI JOB FAILED: Validation harness detected a regression."
    echo "=========================================================="
    cat ${REPORT_FILE}
    exit 1
fi

# 3. Release/Install Stage (Uses the final successful O3 build)
echo "--- Validation PASSED. Proceeding to Manual Release Stage (cp) ---"
BUILD_DIR="${PROJECT_DIR}/build_${BUILD_GENERATOR}_-O3"

# Ensure install directory exists locally
mkdir -p ${INSTALL_DIR}/bin
mkdir -p ${INSTALL_DIR}/lib

# --- FIX: Explicitly copy artifacts to the local release directory ---
echo "Copying artifacts from ${BUILD_DIR}..."

# Copy the executable
cp "${BUILD_DIR}/integrity_checker" "${INSTALL_DIR}/bin/"

# Copy the static library (assuming libCRC_Utils.a is built)
cp "${BUILD_DIR}/libCRC_Utils.a" "${INSTALL_DIR}/lib/"

echo "Artifacts installed successfully to: ${INSTALL_DIR}"

echo "=========================================================="
echo "✅ CI JOB SUCCESS: Toolchain validated. Release artifacts staged."
echo "=========================================================="
