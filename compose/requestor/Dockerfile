# pull official python alpine image
FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive


# Making source and static directory
RUN mkdir /requestor

# Creating Work Directory
WORKDIR /requestor

COPY start.sh /requestor/start.sh
# Adding mandatory packages to docker
RUN apt update && apt install -y \
    curl \
    git \
    python3 \
    python3-pip
# Installing temporary packages required for installing requirements.pip 
RUN apt install -y build-essential \
    python3-dev \ 
    jq

# Update pip
RUN pip3 install yapapi

RUN git clone https://github.com/golemfactory/yapapi/ && cd yapapi && git checkout b0.6

RUN mkdir -p $HOME/.local/share/ya-installer/terms
RUN touch $HOME/.local/share/ya-installer/terms/testnet-01.tag
RUN curl -sSf https://join.golem.network/as-requestor | bash - || echo "Downloaded Yagna Requestor"
ENV PATH=${PATH}:/root/.local/bin/:/root/.local/
COPY blender.py /requestor/blender.py
COPY utils.py /requestor/utils.py
# CMD will run when this dockerfile is running
CMD ["bash", "-c", "/requestor/start.sh; tail -f /dev/null"]
