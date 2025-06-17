install:
	pip install -e .[dev]

run:
	streamlit run src/app.py

format:
	black src

lint:
	flake8 src

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + \
	&& rm -rf .pytest_cache .mypy_cache build dist

