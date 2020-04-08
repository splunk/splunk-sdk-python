@Library('jenkinstools@master') _

withSplunkWrapNode('master') {
    def orcaVersion = "1.0.5"

    stage('Build and Test'){

        echo "Before checkout"
        def functionalJobs = [:]

        def jobName = "Python-SDK"
        functionalJobs[jobName] = {
            splunkFunctionalTest repoName: "https://github.com/splunk/splunk-sdk-python.git",
                            branchName: "${env.BRANCH_NAME}",
                            imageName: "repo.splunk.com/splunk/products/splact:latest",
                            runner: "orca",
                            orcaTestAction: "--help",
                            reportPrefix: "Enterprise_SDK",
                            orcaCredentialId: "ucp_cicd_west_core2",
                            debugMode: " ",
                            splunk_installer: "nightlysplunk-fixture",
                            product: "splunk", //"${product}",
                            splunk_build_branch: "",
                            splunk_build_commit: "",
                            TEST_DIR: "/build/",
                            args: "",
                            'PRE_TEST_CMD': """#!/bin/sh
                                    ls && \
                                    pip install https://repo.splunk.com/artifactory/pypi-remote-cache/7b/4b/a90a0a89db60fc39fc92e31e7da436177a12c06038973c8b7199f47b47c0/tox-3.14.6-py2.py3-none-any.whl && \
                                    ls && \
                                    python scripts/build-splunkrc.py ~/.splunkrc && \
                                    ls && \
                                    tox -e py27,py37 -- -m smoke -v && \
                                    ls
                                """,
                            'POST_TEST_CMD' : 'mv report.html /build/target/$BUILD_NUMBER/'
        }
        echo "before running test"
        parallel functionalJobs
        echo "after running test"
    }
}