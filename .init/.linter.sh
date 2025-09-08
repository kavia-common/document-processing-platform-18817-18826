#!/bin/bash
cd /home/kavia/workspace/code-generation/document-processing-platform-18817-18826/intelligent_receipt_processing_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

