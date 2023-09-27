ARG VERSION_CUDA=11.4.3-cudnn8
ARG VERSION_UBUNTU=18.04

FROM nvidia/cuda:${VERSION_CUDA}-runtime-ubuntu${VERSION_UBUNTU} as build

ARG VERSION_FFMPEG=4.4.4
ARG VERSION_LIBTENSORFLOW=2.5.0
ARG DEPENDENCIES="\
  autoconf \
  automake \
  build-essential \
  cmake \
  curl \
  git \
  git-core \
  libass-dev \
  libfdk-aac-dev \
  libfreetype6-dev \
  libgnutls28-dev \
  libgomp1 \
  libmp3lame-dev \
  libnuma-dev \
  libopus-dev \
  libsdl2-dev \
  libtool \
  libunistring-dev \
  libva-dev \
  libvdpau-dev \
  libvorbis-dev \
  libvpx-dev \
  libxcb-shm0-dev \
  libxcb-xfixes0-dev \
  libxcb1-dev \
  #libx264-dev \
  libx265-dev \
  nasm \
  pkg-config \
  python3-pip \
  python3.8 \
  #python3.10-dev \
  texinfo \
  yasm \
  zlib1g-dev \
  #FFmbc libs
  libgpac-dev \
  libgsm1-dev \
  libspeex-dev \
  #libvorbis-dev \
  libdc1394-22-dev \
  libsdl1.2-dev \
  texi2html \
  libfaac-dev \
  libtheora-dev \
  libopencore-amrnb-dev \
  libopencore-amrwb-dev \
  frei0r-plugins-dev \
  libopencv-dev \
  libgavl1 \
  libx264-dev\
  mediainfo \
"

ENV DEBIAN_FRONTEND=noninteractive \
    TERM=xterm

COPY script/ /usr/local/sbin/

RUN set -o errexit \
 && set -o xtrace \
 && bootstrap-prepare \
 && bootstrap-upgrade \
 && bootstrap-install ${DEPENDENCIES} \
 && build ${VERSION_LIBTENSORFLOW} ${VERSION_FFMPEG} \
 && produce-sr-models ${VERSION_LIBTENSORFLOW} \
 && cleanup \
 && echo 'alias python="python3.8"' >> /etc/bash.bashrc 

ENTRYPOINT ["/bin/bash"]
