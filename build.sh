#!/usr/bin/env bash

# Install necessary libraries for Chromium
apt-get update && apt-get install -y \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libcups2 \
    libatk1.0-0 \
    libgtk-3-0 \
    libxss1 \
    libgbm1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0
