.PHONY: help generate-mock generate build serve clean test install

help:
	@echo "Weekly Summary Generator - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install        - Install dependencies"
	@echo "  make test           - Run tests"
	@echo ""
	@echo "Report Generation:"
	@echo "  make generate-mock  - Generate report with mock data (no auth required)"
	@echo "  make generate       - Generate report with real APIs (requires config.yaml)"
	@echo ""
	@echo "Website:"
	@echo "  make build          - Build Hugo website"
	@echo "  make serve          - Start Hugo development server"
	@echo "  make website        - Generate mock report + build + serve"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove generated files"

# Installation
install:
	uv sync

# Testing
test:
	uv run pytest -v

# Report generation
generate-mock:
	@echo "Generating report with mock data..."
	uv run weekly-summary --config config.mock.yaml --start-date 2024-01-01 --end-date 2024-01-07
	@echo "Report generated in reports/"

generate:
	@echo "Generating report with real APIs..."
	uv run weekly-summary --config config.yaml
	@echo "Report generated in reports/"

# Hugo website
build:
	@echo "Building Hugo website..."
	cd site && hugo --cleanDestinationDir
	@echo "Website built in site/public/"

serve:
	@echo "Starting Hugo development server..."
	@echo "Visit http://localhost:1313 to view the website"
	cd site && hugo server -D

# Combined workflow - generate, build, and serve
website: generate-mock build
	@echo ""
	@echo "Website ready! Starting server..."
	@echo "Visit http://localhost:1313 to view your weekly summaries"
	@echo ""
	$(MAKE) serve

# Cleanup
clean:
	@echo "Cleaning generated files..."
	rm -rf reports/*.md
	rm -rf site/public
	rm -rf site/resources
	@echo "Cleanup complete"
