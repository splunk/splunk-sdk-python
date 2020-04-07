@Library('jenkinstools@master') _

withSplunkWrapNode('master') {
    def orcaVersion = "1.0.5"

    stage('Build and Test'){

        echo "Before checkout"
        echo "Clone the repo into Jenkins container"
        splunkPrepareAndCheckOut repoName: 'git@github.com:splunk/splunk-sdk-python.git',
                                 branchName: "${env.BRANCH_NAME}";
        echo "Install tox and run smoke tests"
        splunkRunScript script: """#!/bin/sh
                    ls && \
                    pip install https://repo.splunk.com/artifactory/pypi-remote-cache/7b/4b/a90a0a89db60fc39fc92e31e7da436177a12c06038973c8b7199f47b47c0/tox-3.14.6-py2.py3-none-any.whl && \
                    ls && \
                    python scripts/build-splunkrc.py ~/.splunkrc && \
                    ls && \
                    tox -e py27,py37 -- -m smoke -v && \
                    ls
                """.stripIndent();
    }
}