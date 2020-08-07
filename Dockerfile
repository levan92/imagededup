# FROM nvcr.io/nvidia/tensorflow:18.06-py3
# FROM nvcr.io/nvidia/tensorflow:18.10-py3
# FROM nvcr.io/nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
FROM nvcr.io/nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

ENV cwd="/home/"
WORKDIR $cwd

RUN apt-get -y update
# RUN apt-get -y upgrade

RUN apt-get install -y \
    software-properties-common \
    build-essential \
    checkinstall \
    cmake \
    pkg-config \
    yasm \
    git \
    vim \
    curl \
    wget \
    gfortran \
    libjpeg8-dev \
    libpng-dev \
    libtiff5-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libdc1394-22-dev \
    libxine2-dev \
    sudo \
    apt-transport-https \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    dbus-x11 \
    vlc \
    iputils-ping \
    python3-dev \
    python3-pip

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata python3-tk
ENV TZ=Asia/Singapore
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && apt-get -y autoremove

### APT END ###

RUN pip3 install --no-cache-dir --upgrade pip 

RUN pip3 install --no-cache-dir \
    numpy==1.15.3 \
    GPUtil \
    tqdm \
    requests \
    protobuf

RUN pip3 install --no-cache-dir  \
    scipy==1.0.0 \
    matplotlib \
    Pillow==5.3.0 \
    opencv-python \
    scikit-image

RUN pip3 install --no-cache-dir \
    tensorflow==1.13.1   \
    tensorflow-gpu==1.13.1   \
    Keras==2.2.4

RUN pip3 install --no-cache-dir jupyter
RUN echo 'alias jup="jupyter notebook --allow-root --no-browser"' >> ~/.bashrc
RUN pip3 install --no-cache-dir tensorboard==1.14
RUN pip3 install --no-cache-dir python-dotenv

RUN pip3 install --no-cache-dir imagededup