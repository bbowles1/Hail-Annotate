# Use Alpine Linux as the base image
FROM python:3.11-alpine AS build

# Install system dependencies
RUN apk --no-cache add build-base \ 
    libffi-dev openssl-dev gfortran \
    pkgconfig cmake gcc freetype-dev \
    libpng-dev openblas-dev==0.3.25-r0 \ 
    libstdc++

# Install and configure Poetry
RUN pip install poetry==1.7.1
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi -vvv

# Create a smaller execution layer
FROM python:3.11-alpine

# Copy only necessary files from the build layer
COPY --from=build /usr/local /usr/local

# install hail base dependencies
RUN apk --no-cache add libstdc++ openblas-dev

# Set the working directory for the application
WORKDIR /app

# add modules directory to path
ENV PATH="/app/modules/:${PATH}"
RUN mkdir /app/tmp/

# Copy the rest of the application code
COPY . /app

# Set the entry point for the container
CMD ["poetry", "run", "your_script.py"]
