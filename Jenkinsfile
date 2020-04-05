@Library('jenkinstools@master') _

withSplunkWrapNode('master') {
    def orcaVersion = "1.0.5"

    def ucpServer = "ucp-cicd-west"

    stage('Build and Test'){

        echo "Before checkout"
        echo "Clone the repo into Jenkins container"
        splunkPrepareAndCheckOut repoName: 'git@github.com:splunk/splunk-sdk-python.git',
                                 branchName: "${env.BRANCH_NAME}";
        splunkFunctionalTest runner : "orca",
                    orcaVersion             : orcaVersion,
                    ucpServerName           : ucpServer,
                    orcaVerbose             : true,
        echo "orca version"
        splunkRunScript script: 'orca --version';
        echo "Create an orca instance for testing"
        splunkRunScript script: 'orca create --splunk-version 7.2.11';
        echo "Install tox"
        splunkRunScript script: 'pip install tox', debugMode: 'sleep';
    }
}