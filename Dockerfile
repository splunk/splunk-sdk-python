ARG SPLUNK_VERSION=latest
FROM splunk/splunk:${SPLUNK_VERSION}

USER root

# We need to copy the entire folder, because Dockerfile doesn't offer optional copy
# I.e. if splunk-mcp-server.tgz doesn't exist, the entire build fails
RUN mkdir /tmp/sdk
COPY . /tmp/sdk
RUN /bin/bash -c '[ -f /tmp/sdk/splunk-mcp-server.tgz ] && cp /tmp/sdk/splunk-mcp-server.tgz /splunk-mcp-server.tgz'
RUN rm -rf /tmp/sdk

RUN mkdir /tmp/sdk
COPY ./pyproject.toml /tmp/sdk/pyproject.toml
COPY ./splunklib /tmp/sdk/splunklib

RUN mkdir /splunklib-deps
RUN chown splunk:splunk /splunklib-deps
RUN chown -R splunk:splunk /tmp/sdk
RUN chown splunk:splunk /tmp/sdk

USER splunk

WORKDIR /tmp/sdk

RUN /bin/bash -c "LD_LIBRARY_PATH=/opt/splunk/lib /opt/splunk/bin/python3.13 -m pip install '.[openai]' --target=/splunklib-deps"

USER ${ANSIBLE_USER}
WORKDIR /opt/splunk
