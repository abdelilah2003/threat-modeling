pipeline {
  agent {
    docker {
      image 'python:3.10'
      args '-u root'
    }
  }

  environment {
    PYTHONUNBUFFERED = '1'
  }

  stages {
    stage('Load Manifest') {
      steps {
        script {
          MANIFEST = readYaml file: 'ai_release.yaml'
          env.AI_TYPE = MANIFEST.ai.type
          env.USES_RAG = MANIFEST.ai.uses_rag.toString()
          echo "Loaded manifest for ${MANIFEST.app.name} (${MANIFEST.app.version})"
          echo "AI type: ${env.AI_TYPE}, uses_rag: ${env.USES_RAG}"
        }
      }
    }

    stage('Validate Manifest') {
      steps {
        sh 'python scripts/validate_manifest.py'
      }
    }

    stage('Unit Tests') {
      steps {
        sh 'bash scripts/run_unit_tests.sh'
      }
      post {
        always {
          junit 'reports/junit/unit_tests.xml'
        }
      }
    }

    stage('Security Checks') {
      steps {
        sh 'bash scripts/run_security_checks.sh'
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/security/*', allowEmptyArchive: true
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'bash scripts/build_image.sh ${BUILD_NUMBER}'
      }
    }

    stage('Model Validation') {
      when {
        expression { env.AI_TYPE == 'llm_rag' }
      }
      steps {
        sh 'test -f model/metadata.json'
      }
    }

    stage('AI Evaluation') {
      when {
        expression { env.AI_TYPE == 'llm_rag' }
      }
      steps {
        sh 'bash scripts/run_model_eval.sh'
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/eval/*', allowEmptyArchive: true
        }
      }
    }

    stage('AI Security Tests') {
      when {
        expression { env.AI_TYPE == 'llm_rag' }
      }
      steps {
        sh 'bash scripts/run_ai_security_tests.sh'
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/ai-security/*', allowEmptyArchive: true
        }
      }
    }

    stage('Deploy Staging') {
      steps {
        sh 'bash scripts/deploy.sh staging'
      }
    }

    stage('Smoke Tests') {
      steps {
        sh 'bash scripts/run_smoke_tests.sh'
      }
      post {
        always {
          junit 'reports/junit/smoke_tests.xml'
        }
      }
    }

    stage('Manual Approval') {
      steps {
        timeout(time: 1, unit: 'DAYS') {
          input message: 'Approve deployment to production?', ok: 'Deploy'
        }
      }
    }

    stage('Deploy Production') {
      steps {
        sh 'bash scripts/deploy.sh production'
        sh 'bash scripts/run_integration_tests.sh'
      }
      post {
        always {
          junit 'reports/junit/integration_tests.xml'
        }
      }
    }
  }
}