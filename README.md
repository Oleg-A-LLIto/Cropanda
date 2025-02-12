# Cropanda
Simple, open-source SFX cropper. Extracts individual sounds from files with silences or multiple takes.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What's This?

This is a Python script to automatically split audio files containing multiple sound effects (SFX) into individual files. It's useful for when you have a single audio file with many sounds, like a sound pack or multiple takes of a recording.

## How it Works

The script uses the `librosa` library for audio analysis. It identifies sound events in two main steps:

1.  **Onset Detection:** It detects the starting points of sounds by looking for sudden increases in the audio signal's energy.
2.  **Dual-Thresholding (Hysteresis):**  After an onset is found, it uses two thresholds:
    *   A higher threshold to confirm the initial onset.
    *   A lower threshold to track the beginning and end of the sound, capturing its quieter parts (attack and decay). This ensures the entire sound event is extracted, not just the loudest portion.

## How to Use It

1.  Have Python3.7+ installed.
2.  Install requirements.
3.  Double-click Cropanda.py, the rest is fairly obvious GUI.
4.  You can drag-and-drop your audio files into the Cropanda window.
5.  Tweak the settings until it gets it right.
6.  It saves to the same directory. Creates a child directory if multiple sounds are detected.
7.  There is no console version of this, but I welcome a fork with one if you would like to do that.

## Cross-Platform Compatibility

I've primarily tested this on Windows. In theory, it's multiplatform out of the box, but feel free to contribute if you find that it's broken on your favorite Linux distro and you know how to fix it there.
