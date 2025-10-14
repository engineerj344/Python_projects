name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repo
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y python3-pip python3-setuptools git zip unzip openjdk-17-jdk python3-virtualenv
        pip install --upgrade pip
        pip install buildozer

    - name: Build APK
      run: |
        buildozer android debug

    - name: Upload APK Artifact
      uses: actions/upload-artifact@v4
      with:
        name: expense-tracker.apk
        path: bin/*.apk
        retention-days: 7
