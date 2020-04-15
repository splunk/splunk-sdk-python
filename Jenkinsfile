@Library('jenkinstools@master') _
withSplunkWrapNode('master') {
    stage('Build and Test'){
        def functionalJobs = [:]
        def jobName = "Python-SDK"
        functionalJobs[jobName] = {
            withCredentials([file(credentialsId: 'srv-devplat-cicd', variable: 'orcaTarFile')]) {
                splunkFunctionalTest repoName: "https://github.com/splunk/splunk-sdk-python.git",
                                branchName: "${env.BRANCH_NAME}",
                                imageName: "repo.splunk.com/splunk/py2py3_orca_tox:latest",
                                runner: "userScript",
                                reportPrefix: "Enterprise_SDK",
                                orcaCredentialId: "ucp_cicd_west_core2",
                                debugMode: "",
                                jobTimeoutMinutes: 1440,
                                files:"$orcaTarFile:orca.tar",
                                script: """#!/bin/bash
                                        git clone "https://github.com/splunk/splunk-sdk-python.git" && cd splunk-sdk-python && \
                                        git checkout "${env.BRANCH_NAME}" && \
                                        tox --version && \
                                        tar xvf /build/orca.tar -C ~ && \
                                        orca -qqq --printer sdd-json create --splunk-version 7.2.10 --apps sdk-app-collection::https://repo.splunk.com/artifactory/Solutions/sdk-app-collection/legacy/sdk-app-collection.tar.gz | tee orca.json && \
                                        echo "Running cat orca.json" && \
                                        cat orca.json
                                        echo "Output script into file"
                                        cat orca.json | python scripts/build-splunkrc.py ~/.splunkrc && \
                                        ls -lah ~ && echo "the home directory is" && echo ~ && \
                                        ls &&  ls -lah /build && echo "I am:" && whoami && echo "python version" && python --version && sleep 30 && \
                                        ls && \
                                        orca --version && \
                                        ls && orca --help  && \
                                        ls -lah && pwd && mkdir .tox && \
                                        tox -e py27,py37 -- -m smoke -v && \
                                        ls
                                        =]]]
                                    """
            }
        }
        echo "before running test"
        parallel functionalJobs
        echo "after running test"
    }
}
