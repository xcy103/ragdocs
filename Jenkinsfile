// CI/CD pipeline: build the backend image, push it to ECR, deploy to the App EC2.
//
// Configure these in Jenkins (NOT committed here, to keep account IDs/hosts private):
//   - Global env vars (Manage Jenkins > System > Global properties > Environment variables):
//       ECR_REGISTRY  e.g. <acct>.dkr.ecr.us-west-2.amazonaws.com
//       APP_HOST      the App EC2 private/public host to deploy to
//   - SSH credential (Manage Jenkins > Credentials), kind "SSH Username with private key":
//       id: app-ssh, username: ec2-user, key: contents of ~/.ssh/ragdocs-key.pem
// The Jenkins instance's IAM role grants ECR push; the App instance's role grants ECR pull.

pipeline {
    agent any

    environment {
        AWS_REGION = 'us-west-2'
        IMAGE_REPO = "${ECR_REGISTRY}/ragdocs-backend"
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build image') {
            steps {
                sh 'docker build -t $IMAGE_REPO:$IMAGE_TAG -t $IMAGE_REPO:latest ./backend'
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                      | docker login --username AWS --password-stdin $ECR_REGISTRY
                    docker push $IMAGE_REPO:$IMAGE_TAG
                    docker push $IMAGE_REPO:latest
                '''
            }
        }

        stage('Deploy to App EC2') {
            steps {
                sshagent(['app-ssh']) {
                    sh 'ssh -o StrictHostKeyChecking=no ec2-user@$APP_HOST "cd ~/ragdocs && aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin $ECR_REGISTRY && sudo docker compose -f compose.prod.yml pull && sudo docker compose -f compose.prod.yml up -d"'
                }
            }
        }
    }

    post {
        success { echo "Deployed build ${IMAGE_TAG} to ${APP_HOST}" }
        failure { echo 'Pipeline failed — check the stage logs.' }
    }
}
