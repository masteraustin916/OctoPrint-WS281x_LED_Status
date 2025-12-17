FROM octoprint/octoprint

# Install build dependencies for lgpio
RUN apt-get update && apt-get install -y \
    swig \
    git \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Build and install lgpio C library
RUN cd /tmp && \
    git clone https://github.com/joan2937/lg.git && \
    cd lg && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /tmp/lg

# Install Python lgpio module
RUN pip install lgpio
