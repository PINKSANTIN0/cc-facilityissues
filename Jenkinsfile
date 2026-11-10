// ===============================================
// Jenkinsfile - Declarative CI/CD Pipeline
// Facility Issue Reporting System
// Telkom University - Cloud Computing UTS
// ===============================================
//
// Jenkins berjalan DI DALAM kontainer dan mengendalikan Docker milik host
// lewat /var/run/docker.sock. Konsekuensinya:
//   1. Bind mount dibaca dari sisi HOST, bukan dari workspace Jenkins.
//      Maka file frontend disalin ke /deploy (folder host yang di-mount ke
//      Jenkins) dan compose memakai HOST_DEPLOY_DIR (path folder itu di host).
//   2. "localhost" di dalam Jenkins adalah kontainer Jenkins sendiri.
//      Aplikasi diakses lewat host.docker.internal.
//
// HOST_DEPLOY_DIR diisi saat kontainer Jenkins dibuat (lihat README).

pipeline {
    agent any

    environment {
        DEPLOY_DIR = '/deploy'                  // folder deploy dilihat dari dalam Jenkins
        APP_HOST   = 'host.docker.internal'     // alamat host dilihat dari dalam Jenkins
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

                sh 'python3 -m py_compile app.py'
                echo '✅ Python syntax OK.'

                sh 'docker compose config --quiet'
                echo '✅ Docker Compose syntax OK.'

                sh 'test -f frontend/index.html && test -f nginx.conf'
                echo '✅ Frontend files exist.'
            }
        }

        // ---- STAGE 3: BUILD IMAGE ----
        stage('Build Image') {
            steps {
                echo '🔨 Stage 3: Building Docker images...'
                sh 'docker compose build --no-cache'
                echo '✅ Docker images built successfully.'
            }
        }

        // ---- STAGE 4: AUTOMATED DEPLOYMENT ----
        stage('Automated Deployment') {
            steps {
                echo '🚀 Stage 4: Deploying application stack...'

                // Pastikan Jenkins dijalankan dengan folder deploy (lihat README)
                sh '''
                    if [ -z "$HOST_DEPLOY_DIR" ] || [ ! -d "$DEPLOY_DIR" ]; then
                        echo "❌ HOST_DEPLOY_DIR belum di-set atau $DEPLOY_DIR belum di-mount."
                        echo "   Jalankan ulang kontainer Jenkins sesuai README (bagian Jenkins)."
                        exit 1
                    fi
                '''

                // Salin file UI ke folder host yang di-bind-mount oleh Nginx
                sh '''
                    mkdir -p "$DEPLOY_DIR/frontend"
                    cp -r frontend/. "$DEPLOY_DIR/frontend/"
                    cp nginx.conf "$DEPLOY_DIR/nginx.conf"
                '''

                // Hentikan stack lama (Named Volume TIDAK dihapus), lalu jalankan yang baru
                sh 'docker compose down --remove-orphans || true'
                sh 'docker rm -f facility-backend facility-frontend 2>/dev/null || true'
                sh 'docker compose up -d'
                echo '✅ Application deployed successfully.'
            }
        }

        // ---- STAGE 5: HEALTH CHECK ----
        stage('Health Check') {
            steps {
                echo '🏥 Stage 5: Running health checks...'

                // Tunggu backend siap (maks. 30 detik)
                sh '''
                    echo "Checking Backend API..."
                    for i in $(seq 1 15); do
                        if curl -sf "http://$APP_HOST:5000/health"; then
                            echo ""
                            echo "✅ Backend API is healthy."
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "❌ Backend health check FAILED"
                    exit 1
                '''

                // Frontend + jalur reverse proxy Nginx -> backend (DNS service name)
                sh '''
                    echo "Checking Frontend..."
                    curl -sf -o /dev/null "http://$APP_HOST:8080/" || (echo "❌ Frontend health check FAILED" && exit 1)
                    echo "✅ Frontend is healthy."

                    echo "Checking Nginx reverse proxy -> backend..."
                    curl -sf -o /dev/null "http://$APP_HOST:8080/api/reports" || (echo "❌ Reverse proxy check FAILED" && exit 1)
                    echo "✅ Reverse proxy is working."
                '''

                // Uji POST -> GET -> DELETE. Yang dihapus adalah data uji itu sendiri
                // (index terakhir), bukan aduan asli milik pengguna.
                sh '''
                    API="http://$APP_HOST:5000/reports"

                    echo "Testing POST /reports..."
                    curl -sf -X POST "$API" \
                        -H "Content-Type: application/json" \
                        -d '{"location":"Test Room","category":"Lainnya","description":"Health check test","reporter":"Jenkins CI"}' \
                        || (echo "❌ POST test FAILED" && exit 1)
                    echo ""
                    echo "✅ POST endpoint working."

                    echo "Testing GET /reports..."
                    COUNT=$(curl -sf "$API" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])") \
                        || (echo "❌ GET test FAILED" && exit 1)
                    echo "✅ GET endpoint working. Total reports: $COUNT"

                    LAST=$((COUNT - 1))
                    echo "Testing DELETE /reports?index=$LAST (data uji)..."
                    curl -sf -X DELETE "$API?index=$LAST" || (echo "❌ DELETE test FAILED" && exit 1)
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
            sh 'docker compose logs --tail 50 || true'
        }
        always {
            echo '📊 Pipeline execution completed.'
        }
    }
}
