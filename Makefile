.PHONY: install test run format deploy

install:
python -m venv .venv
. .venv/bin/activate && pip install -U pip && pip install -r requirements-dev.txt

test:
. .venv/bin/activate && pytest

run:
. .venv/bin/activate && python main.py data/sample_data.csv

format:
. .venv/bin/activate && autopep8 --in-place --recursive trading_bot tests main.py

deploy:
bash deploy.sh
