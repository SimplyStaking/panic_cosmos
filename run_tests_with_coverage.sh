#!/usr/bin/env bash
pipenv sync
pipenv run coverage run run_tests.py
pipenv run coverage report -m