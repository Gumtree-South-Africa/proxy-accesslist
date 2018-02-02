#!groovy

pipeline {
    agent { label 'Slaves' }
    environment {
        SLACK_TOKEN = credentials('slack-token')
    }
    stages {
        stage('Checkout') {
             steps {
                slackSend color: 'good', message: 'Starting whitelist test', teamDomain: 'ebayclassifiedsgroup', token: "${env.SLACK_TOKEN}"
                
                sh 'sudo yum install squid -y'
                sh 'git status'
                sh 'git log -p | head -n 30' 
                sh '''CONFIG=$(mktemp)

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
