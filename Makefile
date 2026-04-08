cat > Makefile << 'EOF'
.PHONY: install run clean test

install:
	pip install -r requirements.txt

run:
	python run_assessment.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

test:
	python run_assessment.py --part 1

setup:
	conda create -n rag python=3.10 -y
	conda activate rag
	make install
EOF