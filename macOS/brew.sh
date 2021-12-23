#!/usr/bin/env bash

grep -v '#' brew.txt | xargs -n1 brew install

brew tap homebrew-ffmpeg/ffmpeg
# --with-chromaprint --with-decklink
brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-fdk-aac --with-game-music-emu --with-jack --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-libopenmpt --with-librist --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvmaf --with-libxml2 --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-openssl@1.1 --with-rav1e --with-rtmpdump --with-rubberband --with-speex --with-srt --with-tesseract --with-two-lame --with-webp --with-xvid --with-zeromq --with-zimg
