pipeline {
  agent any

  environment {
    PYTHONUNBUFFERED = '1'
  }

  stages {

    stage('Prepare Environment') {
      steps {
        sh '''
        echo "🔧 Preparing environment..."

        # Check Python
        python3 --version || (echo "❌ Python3 not found" && exit 1)

        # Create virtual environment
        python3 -m venv venv

        # Activate venv
        . venv/bin/activate

        # Upgrade pip
        pip install --upgrade pip

        # Install dependencies if requirements.txt exists
        if [ -f requirements.txt ]; then
          echo "📦 Installing dependencies from requirements.txt"
          pip install -r requirements.txt
        else
          echo "⚠️ No requirements.txt found, installing minimal deps"
          pip install pyyaml pytest
        fi

        echo "✅ Environment ready"
        '''
      }
    }

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
        sh '''
        . venv/bin/activate
        python scripts/validate_manifest.py
        '''
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
        . venv/bin/activate
        bash scripts/run_unit_tests.sh
        '''
      }
      post {
        always {
          junit 'reports/junit/unit_tests.xml'
        }
      }
    }

    stage('Security Checks') {
      steps {
        sh '''
        . venv/bin/activate
        bash scripts/run_security_checks.sh
        '''
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
        sh '''
        . venv/bin/activate
        bash scripts/run_model_eval.sh
        '''
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
        sh '''
        . venv/bin/activate
        bash scripts/run_ai_security_tests.sh
        '''
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
        sh '''
        . venv/bin/activate
        bash scripts/run_smoke_tests.sh
        '''
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
        sh '''
        . venv/bin/activate
        bash scripts/deploy.sh production
        bash scripts/run_integration_tests.sh
        '''
      }
      post {
        always {
          junit 'reports/junit/integration_tests.xml'
        }
      }
    }
  }
}