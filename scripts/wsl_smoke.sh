#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest discover -s tests -v
python3 -m src.erdos835_one_color stats
python3 -m src.erdos835_one_color rows --limit 5
python3 -m src.erdos835_one_color opb --v 6 --t 1 --extension-count 2 --no-row-comments --no-column-comments --output artifacts/toy.opb
wc -l artifacts/toy.opb
