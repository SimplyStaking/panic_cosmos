#!/usr/bin/env bash
pipenv update
pipenv run coverage run run_tests.py
pipenv run coverage report -m