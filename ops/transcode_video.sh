#!/bin/bash
INPUT=$1
OUTPUT="${INPUT%.*}.webm"
ffmpeg -i "$INPUT" -c:v libvpx -c:a libvorbis "$OUTPUT"
