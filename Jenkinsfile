pipeline {
    agent any
    environment {
        BASE_URL = 'http://127.0.0.1:8000'
    }
    stages {
        stage('Setup') {
            steps {
                sh 'python3 -m pip install -r requirements.txt'
                sh 'python3 -m playwright install --with-deps chromium'
                sh 'nohup python3 -m uvicorn app.main:app --port 8000 > app.log 2>&1 &'
                sh 'python3 -m scripts.derive_test_cases'
            }
        }
        stage('API') {
            steps {
                sh 'python3 -m scripts.run_all --wait --suites api'
            }
        }
        stage('E2E') {
            steps {
                sh 'python3 -m scripts.run_all --suites e2e'
            }
        }
        stage('Groovy') {
            steps {
                sh 'python3 -m scripts.run_all --suites groovy'
            }
        }
        stage('Report') {
            steps {
                sh 'python3 -m scripts.bug_matrix'
                sh 'python3 -m scripts.run_all --report-only'
                sh 'npx --yes allure-commandline generate reports/allure-results -o reports/allure-report --clean'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
