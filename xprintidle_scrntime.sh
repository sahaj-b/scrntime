#!/bin/env bash

IDLE_THRESHOLD=150

while true; do
  idle_ms=$(xprintidle)
  idle_sec=$((idle_ms / 1000))
  echo "Idle time: $idle_sec seconds"

  if [ $idle_sec -ge $IDLE_THRESHOLD ]; then
    start_time=$(date +%s)
    echo "Idle state detected. Monitoring until activity resumes..."

    while [ $idle_sec -ge $IDLE_THRESHOLD ]; do
      idle_ms=$(xprintidle)
      idle_sec=$((idle_ms / 1000))
      sleep 5
    done

    end_time=$(date +%s)
    idle_duration=$((end_time - start_time))
    echo "Activity resumed after $idle_duration seconds of idle time."

    scrntime -a "$idle_duration"
  fi

  sleep 45
done
