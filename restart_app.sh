#!/bin/sh

#  restart_app.sh
#  
#
#  Created by Colin Bouvry on 04/10/2024.
#

# Path to your application executable
APP_PATH="./hidapitester --vidpid 0/1220 --ip 10.0.1.52 --port 5000 --TCP --open --timeout 0 --quiet --length 32 --read-input-forever"

# Function to restart the application if it crashes
restart_app() {
  echo "Starting application: $APP_PATH"
  while true; do
    # Run the application and wait for it to exit
    $APP_PATH
    EXIT_CODE=$?

    # Check if the application exited with a non-zero exit code (indicating a crash)
    if [ $EXIT_CODE -ne 2 ]; then
      echo "Application crashed with exit code $EXIT_CODE. Restarting..."
      sleep 2  # Optional: Wait 2 seconds before restarting
    else
      # If the app exits normally, break the loop
      echo "Application exited normally with code $EXIT_CODE."
      break
    fi
  done
}

# Start the app
restart_app
