# Use Alpine Linux as the base image
FROM python:3.9-alpine AS build

# Install system dependencies
RUN apk --no-cache add build-base libffi-dev openssl-dev

# Install and configure Poetry
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Install Hail library using Poetry
RUN poetry run pip install hail

# Create a smaller execution layer
FROM python:3.9-alpine

# Copy only necessary files from the build layer
COPY --from=build /usr/local /usr/local

# Set the working directory for the application
WORKDIR /app

# Copy the rest of the application code
COPY . /app

# Set the entry point for the container
CMD ["poetry", "run", "your_script.py"]
