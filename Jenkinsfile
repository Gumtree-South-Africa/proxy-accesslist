#!groovy

if (! env.JENKINS_URL.contains("jenkins.cloud-ci.ams1.cloud")) {
  currentBuild.result = 'ABORTED'
  currentBuild.description = 'This pipeline is not configured for ' + env.JENKINS_URL
  return
}

pipeline {
    agent { label 'Slaves' }
    stages {

        // Prepare stuff to run other stages
        stage('Prepare slave') {
            steps {
                sh 'sudo yum install squid -y'
                writeFile file: '/tmp/squidtest.sh', text: '''#!/bin/bash
                    CONFIG=$(mktemp)
                    # Generate a simple configuration sourcing only the files in this directory
                    find $PWD -type f -name "domains-allowlist" -printf 'acl %P dstdomain "%p"\n' > $CONFIG
                    find $PWD -type f -name "ips-allowlist" -printf 'acl %P dst "%p"\n' >> $CONFIG
                    # Run squid to test the config
                    if sudo /usr/sbin/squid -f $CONFIG -k parse 2>&1 |egrep "(WARNING|ERROR|CRITICAL|FATAL)"; then
                      ERROR=1
                      echo "There were warnings or errors in the configuration"
                    else
                      ERROR=0
                    fi

                    # Clean up the config
                    rm -f $CONFIG
                    # Return the exit code (0=OK, 1=ERROR)
                    exit $ERROR'''
                
                slackSend color: 'good', message: "PROXY :: Running Proxy ACL test (<${env.BUILD_URL}/console|Link>)", teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'

            }
        }

        // Always build master to ensure its passing before the pull request
        stage('Build Master') {
            steps {
                slackSend color: 'good', message: 'PROXY :: Running Proxy ACL test against MASTER', teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'
                
                // Fetch master branch
                sshagent(['e3205e49-3955-4abc-ba26-f5fe3367b9cb']) {
                    sh 'git fetch -a -v'
                    sh 'git fetch origin master'
                }
                // Test master is ok
                sh 'git checkout master'
                sh 'sudo bash /tmp/squidtest.sh'
                sh './folder_test.py'
            }
        }

        stage('Checkout pull request') {
            // Build only if there is a pull request
            when {
                expression { env.GITHUB_PR_NUMBER != null }
            }
            steps {
                setGitHubPullRequestStatus([message: "Build Pending", state: "PENDING"])
                slackSend color: 'good', message: "PROXY :: Starting Proxy ACL test on (<${env.GITHUB_PR_URL}|#${env.GITHUB_PR_NUMBER}>) ", teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'
                // Fetch pull request
                sshagent(['e3205e49-3955-4abc-ba26-f5fe3367b9cb']) {
                    sh "git fetch origin pull/${env.GITHUB_PR_NUMBER}/head:pull-request-${env.GITHUB_PR_NUMBER}"                  
                }
                sh "git checkout pull-request-${env.GITHUB_PR_NUMBER}"
                sh "git diff master..pull-request-${env.GITHUB_PR_NUMBER}"
                sh "git show ${env.GITHUB_PR_HEAD_SHA}"   
                sh 'sudo bash /tmp/squidtest.sh'
                sh './folder_test.py'
            }
        }
      stage('Update PR status'){
        when {expression { env.GITHUB_PR_NUMBER != null}
          }
        if (currentBuild.currentResult == 'SUCCESS') {
          setGitHubPullRequestStatus([message: "Build Passed", state: "SUCCESS"])
          }
        else {
          setGitHubPullRequestStatus([message: "Build Failed", state: "FAILURE"])
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
          slackSend color: 'good', message: 'Proxy ACL test passed', teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'
        }
        failure {
          slackSend color: 'bad', message: 'Proxy ACL test failed', teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'
        }
        unstable {
          slackSend color: 'bad', message: 'Proxy ACL test failed', teamDomain: 'eclassifiedsgroup', tokenCredentialId: "slack-token", botUser: true, channel: '#ecg-cloud-proxy'
        }
    }
}
