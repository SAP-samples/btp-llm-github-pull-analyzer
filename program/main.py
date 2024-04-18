"""
main.py:

This file is the entry point for the BTP LLM GitHub Pull Analyzer program.

It sets up command line arguments, logging, loads the configuration from stdin,
generates a report on the sentiment and themes from the located GitHub pull requests.

Lastly, it outputs the report in JSON format to stdout.

Expected input (via stdin):

- A JSON object representing the configuration for the program.  See README.md for details.

Command-line arguments:
- --verbose: Use this switch to increase output verbosity (enables debug level logging)

Example command-line usage:
$ echo '{...}' | python3 main.py [--verbose]

Note:

Replace {...} with the JSON object expected in stdin.
The verbose flag is optional and can be used when more detailed output is required.
"""

import argparse
import json
import logging
import sys
from program.config import Manifest
from program.report import ReportGenerator


def main() -> None:
    """Entry point for the BTP LLM GitHub Pull Analyzer program."""

    parser = argparse.ArgumentParser(description='BTP LLM GitHub Pull Analyzer program')
    parser.add_argument('--verbose', help='increase output verbosity', action='store_true')
    args = parser.parse_args()

    log_format_string = '%(asctime)s - %(levelname)s '
    log_format_string += '[%(module)s - %(funcName)s - '
    log_format_string += '%(filename)s:%(lineno)s] - %(message)s'
    formatter = logging.Formatter(fmt=log_format_string)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    logger = logging.getLogger('root')
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('loading configuration from stdin')
    manifest = Manifest()
    manifest.load(sys.stdin)
    logger.info('configuration loaded')

    logger.info('generating report ...')
    report_generator = ReportGenerator(manifest)
    report = report_generator.generate_report()
    logger.info('report generated')

    logger.info('outputting report to stdout')
    print(json.dumps(report, indent=4, sort_keys=True))
    logger.info('report outputted')


if __name__ == "__main__":
    main()
