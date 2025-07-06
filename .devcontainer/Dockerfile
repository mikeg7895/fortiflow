FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY .. .

RUN pip install --upgrade pip 

CMD ["tail", "-f", "/dev/null"]
