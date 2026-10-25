.PHONY: setup demo run lint test report clean

setup:
	pip install -r requirements.txt

demo:
	python run.py run --icp config/icp.yaml

run:
	python run.py run --icp $(ICP) --limit $(LIMIT)

lint:
	python src/lint_copy.py

test:
	python -m pytest tests -q

report:
	python run.py report

clean:
	rm -rf data/out/*.csv
