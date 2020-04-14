@Library('jenkinstools@master') _

withSplunkWrapNode('master') {
    def orcaVersion = "1.0.5"

    stage('Build and Test'){

        echo "Before checkout"
        def functionalJobs = [:]

        def jobName = "Python-SDK"
        functionalJobs[jobName] = {
            withCredentials([file(credentialsId: 'ucp_cicd_west_core2', variable: 'orcaTarFile')]) {
                splunkFunctionalTest repoName: "https://github.com/splunk/splunk-sdk-python.git",
                                branchName: "${env.BRANCH_NAME}",
                                imageName: "repo.splunk.com/splunk/infra/centos_py2py3",
                                runner: "userScript",
                                reportPrefix: "Enterprise_SDK",
                                orcaCredentialId: "ucp_cicd_west_core2",
                                debugMode: "",
                                files:"$orcaTarFile:orca.tar",
                                script: """#!/bin/bash
                                        cd /tmp/ && git clone "https://github.com/splunk/splunk-sdk-python.git" && cd splunk-sdk-python && \
                                        git checkout "${env.BRANCH_NAME}" && \
                                        tar xvf /build/orca.tar -C ~ && \
                                        ls -lah ~ && echo "the home directory is" && echo ~ && \
                                        ls &&  ls -lah /build && echo "I am:" && whoami && echo "python version" && python --version && sleep 30 && \
                                        pip install https://repo.splunk.com/artifactory/pypi-remote-cache/7b/4b/a90a0a89db60fc39fc92e31e7da436177a12c06038973c8b7199f47b47c0/tox-3.14.6-py2.py3-none-any.whl && \
                                        ls && \
                                        python scripts/build-splunkrc.py ~/.splunkrc && \
                                        ls && orca --help  && \
                                        ls -lah && pwd && mkdir .tox && \
                                        tox -e py27,py37 -- -m smoke -v && \
                                        ls
                                    """
            }
        }
        echo "before running test"
        parallel functionalJobs
        echo "after running test"
    }
}