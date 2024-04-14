ARG PYTORCH="1.6.0"
ARG CUDA="10.1"
ARG CUDNN="7"

FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel

ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

# To fix GPG key error when running apt-get update
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/7fa2af80.pub

RUN apt-get update && apt-get install -y git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1-mesa-glx\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install xtcocotools
RUN pip install cython
RUN pip install xtcocotools

# Install MMCV
RUN pip install --no-cache-dir --upgrade pip wheel setuptools
RUN pip install --no-cache-dir mmcv-full==1.3.17 -f https://download.openmmlab.com/mmcv/dist/cu101/torch1.6.0/index.html

# Install MMPose
RUN conda clean --all
RUN export HTTP_PROXY=http://192.168.1.102:20171 && git clone https://github.com/open-mmlab/mmpose.git /mmpose
WORKDIR /mmpose
RUN mkdir -p /mmpose/data
ENV FORCE_CUDA="1"
RUN pip install -r requirements/build.txt -v -v --proxy=http://192.168.1.102:20171
RUN pip install --no-cache-dir -e . --proxy=http://192.168.1.102:20171
RUN pip install --no-cache-dir mmengine
RUN pip uninstall mmcv-full -y
RUN pip install --no-cache-dir mmcv==2.0.0rc4 -f https://download.openmmlab.com/mmcv/dist/cu101/torch1.6.0/index.html --proxy=http://192.168.1.102:20171

# Run app with CMD
# Copy the current directory contents into the container at /app
COPY . /mmpose
# # Install any needed dependencies specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
# Run app.py when the container launches
# TODO: add wait-for-it script here
# CMD ["python", "main.py"]
CMD ["nvidia-smi"]