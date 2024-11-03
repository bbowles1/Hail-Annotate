FROM ubuntu:24.10

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages and bedtools
RUN apt-get update && apt-get install -y \
    build-essential \
    bzip2 \
    ca-certificates \
    cmake \
    curl \
    gcc \
    g++ \
    libbz2-dev \
    libcurl4-openssl-dev \
    libgsl0-dev \
    liblzma-dev \
    libncurses5-dev \
    libperl-dev \
    libssl-dev \
    make \      
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    pipx \
    samtools \
    wget \
    zlib1g-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.4
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && cd /usr/local/bin \
    && ln -s /opt/poetry/bin/poetry \
    && poetry config virtualenvs.create false

# Copy poetry files
COPY pyproject.toml poetry.lock ./
RUN poetry install

# Create a non-root user
RUN useradd -m bedtools
USER bedtools

# Set default command
CMD ["bedtools", "--help"]