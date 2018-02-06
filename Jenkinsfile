#!groovy

pipeline {
    agent { label 'Slaves' }
    environment {
        SLACK_TOKEN = credentials('slack-token')
    }
    stages {

        // Prepare stuff to run other stages
        stage('Prepare slave') {
            steps {
                sh 'sudo yum install squid -y'
                writeFile file: '/tmp/squidtest.sh', text: '''#!/bin/bash
                    CONFIG=$(mktemp)
                    # Generate a simple configuration sourcing only the files in this directory
                    find $PWD -type f -name "domains-whitelist" -printf 'acl %P dstdomain "%p"\n' > $CONFIG
                    find $PWD -type f -name "ips-whitelist" -printf 'acl %P dst "%p"\n' >> $CONFIG
                    # Run squid to test the config
                    if sudo /usr/sbin/squid -f $CONFIG -k parse 2>&1 |egrep "(WARNING|ERROR|CRITICAL)"; then
                      ERROR=1
                      echo "There were warnings or errors in the configuration"
                    else
                      ERROR=0
                    fi

                    # Clean up the config
                    rm -f $CONFIG
                    # Return the exit code (0=OK, 1=ERROR)
                    exit $ERROR'''
            }
        }

        // Always build master to ensure its passing before the pull request
        stage('Build Master') {
            steps {
                slackSend color: 'good', message: 'PROXY :: Running whitelist test against MASTER', teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
                
                // Fetch master branch
                sshagent(['e3205e49-3955-4abc-ba26-f5fe3367b9cb']) {
                    sh 'git fetch -a -v'
                    sh 'git fetch origin master'
                }
                // Test master is ok
                sh 'git checkout master'
                sh 'sudo bash /tmp/squidtest.sh'
            }
        }

        stage('Checkout pull request') {
            // Build only if there is a pull request
            when {
                expression { env.ghprbActualCommit != null }
            }
            steps {
                slackSend color: 'good', message: "PROXY :: Starting whitelist test on ${env.ghprbPullLink} ", teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
                // Fetch pull request
                sshagent(['e3205e49-3955-4abc-ba26-f5fe3367b9cb']) {
                    sh "git fetch origin pull/${ghprbPullId}/head:pull-request-${ghprbPullId}"                  
                }
                sh "git checkout pull-request-${ghprbPullId}"
                sh "git show ${ghprbActualCommit}"   
                sh 'sudo bash /tmp/squidtest.sh'
            }
        }
        // Clean up folder
        stage('Clean up workspace') {
            steps {
                cleanWs()
            }
        }
    }
    post {
        success {
          slackSend color: 'good', message: 'Whitelist test passed', teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
        }
        failure {
          slackSend color: 'bad', message: 'Whitelist test failed', teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
        }
        unstable {
          slackSend color: 'bad', message: 'Whitelist test failed', teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
        }
    }
}
