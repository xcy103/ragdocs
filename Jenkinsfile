// CI/CD pipeline: build the backend + frontend images, push to ECR, deploy to the App EC2.
//
// Configure in Jenkins (NOT committed here, to keep account IDs/hosts private):
//   - Global env vars: ECR_REGISTRY (e.g. <acct>.dkr.ecr.us-west-2.amazonaws.com), APP_HOST
//   - SSH credential id `app-ssh` (ec2-user + ~/.ssh/ragdocs-key.pem)
// The Jenkins instance role grants ECR push; the App instance role grants ECR pull.

pipeline {
    agent any

    environment {
        AWS_REGION    = 'us-west-2'
        BACKEND_REPO  = "${ECR_REGISTRY}/ragdocs-backend"
        FRONTEND_REPO = "${ECR_REGISTRY}/ragdocs-frontend"
        TAG           = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build images') {
            steps {
                sh 'docker build -t $BACKEND_REPO:$TAG -t $BACKEND_REPO:latest ./backend'
                sh 'docker build -t $FRONTEND_REPO:$TAG -t $FRONTEND_REPO:latest ./frontend'
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                      | docker login --username AWS --password-stdin $ECR_REGISTRY
                    docker push $BACKEND_REPO:$TAG
                    docker push $BACKEND_REPO:latest
                    docker push $FRONTEND_REPO:$TAG
                    docker push $FRONTEND_REPO:latest
                '''
            }
        }

        stage('Deploy to App EC2') {
            steps {
                sshagent(['app-ssh']) {
                    // Keep the server's compose file in sync with the repo, then redeploy.
                    sh 'scp -o StrictHostKeyChecking=no compose.prod.yml ec2-user@$APP_HOST:~/ragdocs/compose.prod.yml'
                    sh 'ssh -o StrictHostKeyChecking=no ec2-user@$APP_HOST "cd ~/ragdocs && aws ecr get-login-password --region us-west-2 | sudo docker login --username AWS --password-stdin $ECR_REGISTRY && sudo docker compose -f compose.prod.yml pull && sudo docker compose -f compose.prod.yml up -d"'
                }
            }
        }
    }

    post {
        success { echo "Deployed build ${TAG} to ${APP_HOST}" }
        failure { echo 'Pipeline failed — check the stage logs.' }
    }
}
