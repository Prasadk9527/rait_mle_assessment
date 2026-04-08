#!/bin/bash
# check_files.sh

echo "Checking required files..."

files=(
    "run_assessment.py"
    "src/schema/canonical_schema.py"
    "src/adapters/base_adapter.py"
    "src/adapters/supplier_a_adapter.py"
    "src/adapters/supplier_b_adapter.py"
    "src/adapters/supplier_c_adapter.py"
    "src/metrics/base_metric.py"
    "src/metrics/security_metric.py"
    "src/metrics/fairness_metric.py"
    "src/metrics/transparency_metric.py"
    "src/adversarial/attack_patterns.py"
    "src/adversarial/semantic_search.py"
    "src/adversarial/llm_judge.py"
    "src/adversarial/red_team_pipeline.py"
    "src/coverage/coverage_reporter.py"
)

all_present=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo " $file"
    else
        echo " $file - MISSING"
        all_present=false
    fi
done

if [ "$all_present" = true ]; then
    echo ""
    echo " All files present! Ready to run."
else
    echo ""
    echo "Some files missing. Please create them."
fi