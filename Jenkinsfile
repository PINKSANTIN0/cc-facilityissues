// ===============================================
// Jenkinsfile - Declarative CI/CD Pipeline
// Facility Issue Reporting System
// Telkom University - Cloud Computing UTS
// ===============================================

pipeline {
    agent any

    environment {
        COMPOSE_PROJECT = 'facility-report'
        DOCKER_COMPOSE  = 'docker-compose'
    }

    stages {

        // ---- STAGE 1: CHECKOUT ----
        stage('Checkout') {
            steps {
                echo '📥 Stage 1: Checking out source code from GitHub...'
                checkout scm
                echo '✅ Source code checked out successfully.'
            }
        }

        // ---- STAGE 2: SYNTAX CHECK ----
        stage('Syntax Check') {
            steps {
                echo '🔍 Stage 2: Running syntax checks...'
                // Check Python syntax
                sh 'python3 -c "import py_compile; py_compile.compile(\'app.py\', doraise=True)"'
                echo '✅ Python syntax OK.'

                // Validate docker-compose file
                sh "${DOCKER_COMPOSE} config --quiet"
                echo '✅ Docker Compose syntax OK.'

                // Check if frontend files exist
                sh 'test -f frontend/index.html && echo "✅ Frontend index.html exists."'
            }
        }

        // ---- STAGE 3: BUILD IMAGE ----
        stage('Build Image') {
            steps {
                echo '🔨 Stage 3: Building Docker images...'
                sh "${DOCKER_COMPOSE} build --no-cache"
                echo '✅ Docker images built successfully.'
            }
        }

        // ---- STAGE 4: AUTOMATED DEPLOYMENT ----
        stage('Automated Deployment') {
            steps {
                echo '🚀 Stage 4: Deploying application stack...'
                // Stop any existing containers
                sh "${DOCKER_COMPOSE} down --remove-orphans || true"
                // Deploy fresh stack
                sh "${DOCKER_COMPOSE} up -d"
                echo '✅ Application deployed successfully.'
                // Wait for services to be ready
                sh 'sleep 10'
            }
        }

        // ---- STAGE 5: HEALTH CHECK ----
        stage('Health Check') {
            steps {
                echo '🏥 Stage 5: Running health checks...'

                // Check backend health
                sh '''
                    echo "Checking Backend API..."
                    curl -sf http://localhost:5000/health || (echo "❌ Backend health check FAILED" && exit 1)
                    echo ""
                    echo "✅ Backend API is healthy."
                '''

                // Check frontend health
                sh '''
                    echo "Checking Frontend..."
                    curl -sf http://localhost:8080/ || (echo "❌ Frontend health check FAILED" && exit 1)
                    echo ""
                    echo "✅ Frontend is healthy."
                '''

                // Test API endpoints
                sh '''
                    echo "Testing POST /reports..."
                    curl -sf -X POST http://localhost:5000/reports \
                        -H "Content-Type: application/json" \
                        -d '{"location":"Test Room","category":"AC Mati","description":"Health check test","reporter":"Jenkins CI"}' \
                        || (echo "❌ POST test FAILED" && exit 1)
                    echo ""
                    echo "✅ POST endpoint working."

                    echo "Testing GET /reports..."
                    curl -sf http://localhost:5000/reports || (echo "❌ GET test FAILED" && exit 1)
                    echo ""
                    echo "✅ GET endpoint working."

                    echo "Testing DELETE /reports?index=0..."
                    curl -sf -X DELETE "http://localhost:5000/reports?index=0" || (echo "❌ DELETE test FAILED" && exit 1)
                    echo ""
                    echo "✅ DELETE endpoint working."
                '''

                echo '✅ All health checks passed!'
            }
        }
    }

    post {
        success {
            echo '''
            =========================================
            ✅ PIPELINE SUCCESS!
            🌐 Frontend: http://localhost:8080
            🔧 Backend API: http://localhost:5000
            =========================================
            '''
        }
        failure {
            echo '❌ Pipeline FAILED. Check logs above for details.'
            sh "${DOCKER_COMPOSE} logs || true"
        }
        always {
            echo '📊 Pipeline execution completed.'
        }
    }
}
