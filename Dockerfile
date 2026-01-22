ARG SPLUNK_VERSION=latest
FROM splunk/splunk:${SPLUNK_VERSION}

USER root

RUN mkdir /tmp/sdk
COPY ./pyproject.toml /tmp/sdk/pyproject.toml
COPY ./uv.lock /tmp/sdk/uv.lock
COPY ./splunklib /tmp/sdk/splunklib

RUN mkdir /splunklib-deps
RUN chown splunk:splunk /splunklib-deps
RUN chown -R splunk:splunk /tmp/sdk
RUN chown splunk:splunk /tmp/sdk

USER splunk

WORKDIR /tmp/sdk

RUN /opt/splunk/bin/python3.13 -m venv .venv
RUN /bin/bash -c "source .venv/bin/activate && LD_LIBRARY_PATH=/opt/splunk/lib python -m pip install '.[openai]' --target=/splunklib-deps"

USER ${ANSIBLE_USER}
WORKDIR /opt/splunk
