

# Audio Transcription Core

Audio Transcription Core is a service for audio transcription, which together with Audio Segment Core, creates subtitles for audios that were extracted from videos.

## Table of Contents

- **[Getting Started](#getting-started)**
  - [System Requirements](#system-requirements)
  - [Prerequisites](#prerequisites)
  - [Installing](#installing)
- **[Contributors](#contributors)**



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### System Requirements

* OS: Ubuntu 18.04.2 LTS (Bionic Beaver) or later
* OS: Windows (WSL 2)

### Prerequisites

Before starting the installation, you need to install some prerequisites:

[RabbitMQ](https://www.rabbitmq.com/)

```sh
wget -O - "https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey" | sudo apt-key add -
```

```sh
curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | sudo bash
```

```sh
sudo apt install -y rabbitmq-server --fix-missing
```

### Installing

After installing all the prerequisites, at the root of the project, install it by running the command:

```sh
sudo make install
```

To test the installation, simply start the Translation Core with the following command:

```sh
make dev start
```

## Contributors

* Ewerton André de Sousa Moura - <ewerton.asmoura@gmail.com>
