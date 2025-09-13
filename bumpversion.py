import argparse
from logging import getLogger
from pathlib import Path

import ruamel.yaml

logger = getLogger()

chart_path = Path("./chart/Chart.yaml")

parser = argparse.ArgumentParser(description="Scritp to update the package version in the required files")
parser.add_argument("version", type=str, help="Version number")
args = parser.parse_args()
version = args.version

if chart_path.exists():
    # Update the Helm's Chart
    with open(chart_path) as f:
        yaml = ruamel.yaml.YAML()
        chart_file = yaml.load(f)

        chart_file["appVersion"] = version

        with open(chart_path, "w") as f:
            yaml.dump(chart_file, f)
else:
    logger.error("Chart.yaml file not found!")
