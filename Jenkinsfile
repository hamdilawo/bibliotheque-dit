// =============================================================
// Jenkinsfile — Pipeline CI/CD Bibliothèque DIT
// =============================================================
// Stages :
//   1. Checkout
//   2. Tests (lint + syntaxe Python)
//   3. Build Docker
//   4. Pipeline DVC (preprocess → train → evaluate)
//   5. Deploy (dev ou prod selon la branche)
// =============================================================

pipeline {
    agent any

    environment {
        DOCKER_COMPOSE = 'docker compose'
        PROJET         = 'bibliotheque-dit'
        REGISTRY       = 'ghcr.io/votre-compte'
    }

    // Déclencher automatiquement sur push
    triggers {
        githubPush()
    }

    stages {

        // ── Stage 1 : Checkout ───────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Récupération du code source...'
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // ── Stage 2 : Vérifications ──────────────────────────
        stage('Lint & Vérifications') {
            parallel {

                stage('Syntaxe Python') {
                    steps {
                        echo '🐍 Vérification syntaxe Python...'
                        sh '''
                            find services/ dvc/ -name "*.py" | while read f; do
                                python3 -m py_compile "$f" && echo "  ✓ $f"
                            done
                        '''
                    }
                }

                stage('Secrets') {
                    steps {
                        echo '🔒 Vérification absence de secrets...'
                        sh '''
                            if grep -rE "password\s*=\s*['\"][^'\"]{8,}" services/ \
                                --include="*.py" \
                                | grep -v "changeme\|example\|test"; then
                                echo "⚠️  Secrets potentiels détectés"
                            else
                                echo "  ✓ Aucun secret détecté"
                            fi
                        '''
                    }
                }

                stage('Docker Compose Validate') {
                    steps {
                        echo '🐳 Validation docker-compose.yml...'
                        sh "${DOCKER_COMPOSE} config --quiet && echo '  ✓ docker-compose.yml valide'"
                    }
                }
            }
        }

        // ── Stage 3 : Build Docker ───────────────────────────
        stage('Build Docker') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                    branch pattern: 'release/*', comparator: 'GLOB'
                }
            }
            steps {
                echo '🏗️  Build des images Docker...'
                sh """
                    ${DOCKER_COMPOSE} --profile dev build \
                        --parallel \
                        --build-arg BUILDKIT_INLINE_CACHE=1
                """
            }
            post {
                success {
                    echo '✅ Images Docker construites avec succès'
                }
                failure {
                    echo '❌ Échec du build Docker'
                }
            }
        }

        // ── Stage 4 : Pipeline DVC ───────────────────────────
        stage('Pipeline DVC') {
            when {
                anyOf {
                    branch 'develop'
                    branch 'main'
                    changeset 'dvc/**'
                }
            }
            steps {
                echo '📊 Exécution du pipeline DVC...'

                dir('dvc') {
                    sh '''
                        pip install --quiet dvc[gdrive] pandas numpy scikit-learn joblib pyyaml

                        echo "→ Étape 1 : Prétraitement..."
                        python3 preprocess.py

                        echo "→ Étape 2 : Entraînement..."
                        python3 train.py

                        echo "→ Étape 3 : Évaluation..."
                        python3 evaluate.py

                        echo "→ Métriques :"
                        cat metrics.json
                    '''
                }
            }
            post {
                always {
                    // Archiver les métriques comme artefact Jenkins
                    archiveArtifacts artifacts: 'dvc/metrics.json', fingerprint: true

                    // Publier les métriques dans Jenkins
                    script {
                        def metrics = readJSON file: 'dvc/metrics.json'
                        echo """
                        ┌─────────────────────────────────┐
                        │   Métriques du modèle ML         │
                        ├─────────────────────────────────┤
                        │  RMSE        : ${metrics.rmse}   │
                        │  MAE         : ${metrics.mae}    │
                        │  Précision@5 : ${metrics['precision_at_5']} │
                        │  Rappel@5    : ${metrics['rappel_at_5']}    │
                        └─────────────────────────────────┘
                        """
                    }
                }
            }
        }

        // ── Stage 5 : Tests d'intégration ───────────────────
        stage('Tests Intégration') {
            when { branch 'develop' }
            steps {
                echo '🧪 Tests d\'intégration des APIs...'
                sh """
                    # Lancer les services en arrière-plan
                    ${DOCKER_COMPOSE} --profile dev up -d db livres utilisateurs emprunts
                    sleep 15

                    # Attendre que les services soient prêts
                    for service in 8001 8002 8003; do
                        timeout 30 bash -c "until curl -sf http://localhost:\$service/api/; do sleep 2; done"
                        echo "  ✓ Service :\$service disponible"
                    done

                    # Tests des endpoints
                    echo "Test GET /api/livres/ ..."
                    curl -sf http://localhost:8001/api/livres/ | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'  ✓ {d[\"count\"]} livres')"

                    echo "Test GET /api/utilisateurs/ ..."
                    curl -sf http://localhost:8002/api/utilisateurs/ | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'  ✓ {d[\"count\"]} utilisateurs')"

                    echo "Test POST /api/emprunts/emprunter/ ..."
                    STATUS=\$(curl -s -o /dev/null -w "%{http_code}" \\
                        -X POST http://localhost:8003/api/emprunts/emprunter/ \\
                        -H "Content-Type: application/json" \\
                        -d '{"utilisateur_id": 1, "livre_id": 1}')
                    echo "  HTTP \$STATUS (201=OK, 400=normal si déjà emprunté)"
                """
            }
            post {
                always {
                    sh "${DOCKER_COMPOSE} --profile dev down --remove-orphans || true"
                }
            }
        }

        // ── Stage 6 : Déploiement ────────────────────────────
        stage('Deploy DEV') {
            when { branch 'develop' }
            steps {
                echo '🚀 Déploiement en environnement DEV...'
                sh """
                    ${DOCKER_COMPOSE} --profile dev up -d --build
                    echo "  ✓ Déployé en DEV"
                    echo "  Frontend     : http://dev.bibliotheque.dit.sn:3000"
                    echo "  API Livres   : http://dev.bibliotheque.dit.sn:8001/api/docs/"
                    echo "  Reco API     : http://dev.bibliotheque.dit.sn:8004/docs"
                """
            }
        }

        stage('Deploy PROD') {
            when { branch 'main' }
            steps {
                echo '🚀 Déploiement en PRODUCTION...'

                // Confirmation manuelle obligatoire pour la prod
                input message: 'Confirmer le déploiement en production ?',
                      ok: 'Déployer',
                      submitter: 'admin,tech-lead'

                sh """
                    ${DOCKER_COMPOSE} --profile prod up -d --build
                    echo "  ✓ Déployé en PRODUCTION"
                """
            }
        }
    }

    // ── Post-actions ─────────────────────────────────────────
    post {
        success {
            echo """
            ╔══════════════════════════════════════════╗
            ║   ✅ Pipeline CI/CD réussi !              ║
            ║   Branche : ${env.BRANCH_NAME}            ║
            ║   Build   : #${env.BUILD_NUMBER}          ║
            ╚══════════════════════════════════════════╝
            """
        }
        failure {
            echo """
            ╔══════════════════════════════════════════╗
            ║   ❌ Pipeline CI/CD échoué                ║
            ║   Branche : ${env.BRANCH_NAME}            ║
            ║   Build   : #${env.BUILD_NUMBER}          ║
            ╚══════════════════════════════════════════╝
            """
        }
        always {
            // Nettoyage
            sh "${DOCKER_COMPOSE} --profile dev down --remove-orphans || true"
            cleanWs()
        }
    }
}
