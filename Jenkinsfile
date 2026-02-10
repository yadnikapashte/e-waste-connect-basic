pipeline {
    agent any

    tools {
        jdk 'JDK11'          // Replace with your configured JDK name
        maven 'Maven3'       // Replace with your configured Maven name
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/yadnikapashte/e-waste-connect-basic.git', branch: 'main'

            }
        }

        stage('Build') {
            steps {
                sh 'mvn clean install'   // Maven build
            }
        }

        stage('Test') {
            steps {
                sh 'mvn test'           // Run tests
            }
        }

        stage('Deploy') {
            steps {
                // Copy the WAR file to Tomcat webapps folder
                sh 'cp target/e-waste-connect.war /path/to/tomcat/webapps/'
                // Restart Tomcat to apply the deployment
                sh '/path/to/tomcat/bin/shutdown.sh || true'
                sh '/path/to/tomcat/bin/startup.sh'
            }
        }
    }

    post {
        success {
            echo 'Deployment Successful!'
        }
        failure {
            echo 'Deployment Failed!'
        }
    }
}
