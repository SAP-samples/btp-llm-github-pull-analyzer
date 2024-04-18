"""
test_main.py

This module defines unit tests for the main.py module.
"""

import io
import json
import sys
from unittest.mock import MagicMock
from unittest.mock import patch
import pytest
from program.main import main


# pylint: disable=redefined-outer-name
@pytest.fixture()
def mock_manifest():
    """Returns a mock Manifest object."""

    manifest = MagicMock()
    manifest.load.return_value = None
    return manifest


# pylint: disable=redefined-outer-name
@pytest.fixture()
def mock_report_generator():
    """Returns a mock ReportGenerator object."""

    report_generator = MagicMock()
    report_generator.generate_report.return_value = {'result': 'report'}
    return report_generator


# pylint: disable=too-many-arguments
@patch('program.main.ReportGenerator')
@patch('program.main.Manifest')
def test_main(mock_manifest, mock_rpt_gen_cls, mock_report_generator):
    """Test main function."""

    mock_manifest.return_value = mock_manifest
    mock_rpt_gen_cls.return_value = mock_report_generator

    mock_stdin = io.StringIO(json.dumps({}))
    sys.stdin = mock_stdin

    main()

    mock_manifest.load.assert_called_once_with(sys.stdin)
    mock_report_generator.generate_report.assert_called_once_with()

    sys.stdin = sys.__stdin__
