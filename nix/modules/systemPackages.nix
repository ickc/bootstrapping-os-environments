# List packages installed in system profile. To search by name, run:
# $ nix-env -qaP | grep wget
# Usage:
#   environment.systemPackages = import ./packages.nix { inherit pkgs; };
{ pkgs, pkgs-unstable }:
with pkgs;
[
  bashInteractive
  bat
  bat-extras.batdiff
  bat-extras.batgrep
  bat-extras.batman
  bat-extras.batpipe
  bat-extras.batwatch
  bat-extras.prettybat
  # bottom
  btop
  # code2prompt
  coreutils-full
  delta
  devbox
  # diffoscope
  difftastic
  diffutils
  direnv
  dua
  duti
  entr
  epubcheck
  exiftool
  f3
  fastfetch
  fd
  ffmpeg_7
  file
  findutils
  fish
  fzf
  gawk
  gh
  ghostscript
  git
  gnugrep
  gnumake
  gnupatch
  gnused
  gnutar
  go-task
  # gpsbabel
  graphviz
  gron
  gzip
  html-tidy
  htop
  hyperfine
  imagemagick
  inetutils
  iperf
  joshuto
  jq
  less
  libarchive
  # libimobiledevice
  librsvg
  lsd
  lux
  mediainfo
  mediainfo-gui
  mermaid-cli
  minify
  mosh
  nano
  nil
  nixd
  nixfmt
  nmap
  onefetch
  # openai-whisper
  whisper-cpp
  opencc
  pam-reattach
  parallel
  pdf2svg
  poppler-utils
  potrace
  procps
  ripgrep
  rsync
  sd
  shellcheck
  shfmt
  smartmontools
  sshuttle
  starship
  streamlink
  time
  tmux
  tokei
  units
  verapdf
  w3m
  wakeonlan
  wdiff
  wget
  which
  yt-dlp
  zsh
]
