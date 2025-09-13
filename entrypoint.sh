#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

CONNECTION_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

python << END
import sys
import time

from sqlalchemy import create_engine

suggest_unrecoverable_after = 30
start = time.time()

for i in range(5):
    try:
        create_engine("${CONNECTION_URL}").connect()
        break

    except psycopg.OperationalError as error:
        sys.stderr.write("Waiting for PostgreSQL to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(error))

    time.sleep(1)
END

>&2 echo 'PostgreSQL is available'

# Relative path to the config file from the current working directory
CONFIG_FILE="app/core/config.py"

# Function to extract a variable value from the config file
get_config_value() {
    local var_name="$1"
    grep -E "${var_name}" "app/core/config.py" | sed "s/${var_name}[:][ ]*str//g" | sed "s/[ ]*[=]*[\"]*//g"
}

# Extract PROJECT_NAME and API_VERSION
PROJECT_NAME=$(get_config_value "PROJECT_NAME")
API_VERSION=$(get_config_value "API_VERSION")
ENVIRONMENT_DEFAULT=$(get_config_value "ENVIRONMENT")

# Get ENVIRONMENT or default ENVIRONMENT_DEFAULT var
ENVIRONMENT="${ENVIRONMENT:-$ENVIRONMENT_DEFAULT}"

# Concatenate the string
CONCAT_STRING="${ENVIRONMENT}-${PROJECT_NAME}-${API_VERSION}"

export POSTGRES_APP_NAME="$CONCAT_STRING"

uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8080
