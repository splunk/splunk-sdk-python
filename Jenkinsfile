@Library('jenkinstools@master') _

withSplunkWrapNode('master') {
    def orcaVersion = "1.0.5"

    stage('Build and Test'){

        echo "Before checkout"
        echo "Clone the repo into Jenkins container"
        splunkPrepareAndCheckOut repoName: 'git@github.com:splunk/splunk-sdk-python.git',
                                 branchName: "${env.BRANCH_NAME}";
        echo "Install Orca"
        splunkRunScript script: 'pip install orca'
        splunkRunScript script: 'export PATH=$HOME/orca:$PATH; export LD_LIBRARY_PATH=$HOME/orca:$LD_LIBRARY_PATH'
        echo "Create an orca instance for testing"
        splunkRunScript script: 'orca create --splunk-version 7.2.11';
        echo "Install tox"
        splunkRunScript script: 'pip install tox', debugMode: 'sleep';
    }
}