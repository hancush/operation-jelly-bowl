MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail
.DEFAULT_GOAL := all

data/newsletter_wines.csv :
	python scrape_du_vin.py > $@