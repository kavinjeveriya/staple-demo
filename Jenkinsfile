pipeline {
    agent {
        kubernetes {
            cloud 'k8s'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: slave
spec:
  serviceAccountName: jenkins-admin
  nodeSelector:
    kubernetes.io/arch: amd64
  containers:
  - name: jnlp
    image: jenkins/inbound-agent
  - name: aws
    image: amazon/aws-cli
    command: ["/bin/sh", "-c", "sleep 1d"]
    tty: true
  - name: docker
    image: kavinjaveriya/dind-aws:latest
    command: ["sh", "-c", "dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock"]
    tty: true
    securityContext:
      privileged: true
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["/bin/sh", "-c", "sleep 1d"]
    tty: true
    securityContext:
      runAsUser: 0
  - name: helm
    image: alpine/helm:3.12.0
    command: ["/bin/sh", "-c", "sleep 1d"]
    tty: true
"""
        }
    }

    environment {
        IMAGE_TAG = "895533345638.dkr.ecr.us-east-1.amazonaws.com/staple:dev.${BUILD_NUMBER}"
        RELEASE_NAME = "staple-demo"
        KUBE_NAMESPACE = "dev"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                container(name: 'docker', shell: '/bin/sh') {
                    sh """
                    sleep 30
                    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 895533345638.dkr.ecr.us-east-1.amazonaws.com
                    ls
                    pwd
                    docker build -t ${IMAGE_TAG} .
                    docker push ${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Checkout Helm Repo') {
            steps {
                dir('helm') {
                    git branch: 'main', credentialsId: 'github-mj-auth-token', url: 'https://github.com/kavinjeveriya/Staple-HelmChart.git'
                }
            }
        }

        stage('Fetch Secrets Values') {
            steps {
                container('helm') {
                    dir('helm') {
                        withCredentials([usernamePassword(credentialsId: 'github-mj-auth-token', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            sh """
                            echo "Downloading secret values from Staple-devops repo..."
                            curl -s -u "$GIT_USER:$GIT_TOKEN" \
                                 -o staple-demo-secrets-values.yaml \
                                 https://raw.githubusercontent.com/kavinjeveriya/Staple-devops/secrets/staple-demo-secrets-values.yaml
                            ls -l
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy via Helm') {
            steps {
                container('helm') {
                    dir('helm') {
                        sh """
                          helm upgrade --install ${RELEASE_NAME} ./helm/staple-demo/ \
                          --namespace ${KUBE_NAMESPACE} --create-namespace \
                          --values ./helm/staple-demo-secrets-values.yaml \
                          --values ./helm/staple-demo//values.yaml \
                          --set image.tag=${IMAGE_TAG.split(':')[1]} \
                          --wait
                    """
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment succeeded!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
