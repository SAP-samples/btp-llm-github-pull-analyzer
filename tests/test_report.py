"""
test_report.py:

This file contains the unit tests for the ReportGenerator class from within
the report.py module.
"""

from io import StringIO
from unittest.mock import patch
import pytest
from program.report import ReportGenerator
from program.config import Manifest


# pylint: disable=redefined-outer-name
# pylint: disable=duplicate-code
@pytest.fixture
def manifest_json():
    """Returns a JSON string representing a manifest configuration."""

    return '''{
        "github": {
            "org_name": "mock-org-name",
            "repo_name": "mock-repo-name",
            "api_url": "https://github.tools.mock/api/v3",
            "api_token": "mock-api-token",
            "search_label": "mock-search-label"
        },
        "openai": {
            "completions_url": "https://azure-openai.mock/chat/completions?api-version=mock",
            "uaa_url": "https://mock-openai.authentication.mock",
            "client_id": "mock-client-id",
            "client_secret": "mock-client-secret",
            "data_template": {
                "deployment_id": "gpt-mock-deployment-id",
                "messages": [],
                "max_tokens": 4000,
                "temperature": 0.7,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "top_p": 0.95,
                "stop": null
            }
        },
        "report": {
            "grounding_prompt": "test-grounding-prompt",
            "pull_prompt": "test-pull-prompt",
            "overview_prompt": "test-overview-prompt"
        }
    }'''


@patch('program.providers.OpenAiProvider.get_completion')
@patch('program.providers.OpenAiProvider.get_access_token')
@patch('program.providers.GitHubProvider.get_pull_request_pulls')
def test_generate_report(mock_get_pull_request_pulls,
                         mock_get_openai_access_token,
                         mock_get_openai_completion,
                         manifest_json):
    """Test generate_report method of ReportGenerator."""

    mock_get_pull_request_pulls.return_value = [{
        'url': 'mock_url',
        'messages': []
    }]

    mock_get_openai_access_token.return_value = 'mock-access-token'

    mock_get_openai_completion.return_value = {
        'group_name': 'mock_url',
        'completion': {
            'choices': [{
                'message': {
                    'content': 'mock_completion'
                }
            }]
        }
    }

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    rg = ReportGenerator(manifest)
    report = rg.generate_report()

    assert isinstance(report, dict)
    assert "summary" in report
    assert isinstance(report['summary'], str)
    assert "pulls" in report
    assert isinstance(report['pulls'], list)


@patch('program.providers.OpenAiProvider.get_completion')
@patch('program.providers.OpenAiProvider.get_access_token')
@patch('program.providers.GitHubProvider.get_pull_request_pulls')
def test_generate_summary_report(mock_get_pull_request_pulls,
                                 mock_get_openai_access_token,
                                 mock_get_openai_completion,
                                 manifest_json):
    """Test generate_summary_report method of ReportGenerator."""

    mock_get_pull_request_pulls.return_value = [{
        'url': 'mock_url',
        'messages': []
    }]

    mock_get_openai_access_token.return_value = 'mock-access-token'

    mock_get_openai_completion.return_value = {
        'group_name': 'mock_url',
        'completion': {
            'choices': [{
                'message': {
                    'content': 'mock_completion'
                }
            }]
        }
    }

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    rg = ReportGenerator(manifest)
    summary_report = rg.generate_summary_report([{
        'url': 'mock_url',
        'analysis': 'mock_analysis'
    }])

    assert isinstance(summary_report, dict)
    assert "prompts" in summary_report
    assert summary_report['prompts']['grounding'] == "test-grounding-prompt"
    assert summary_report['prompts']['pull'] == "test-pull-prompt"
    assert summary_report['prompts']['overview'] == "test-overview-prompt"
    assert "summary" in summary_report
    assert isinstance(summary_report['summary'], str)
    assert "pulls" in summary_report
    assert isinstance(summary_report['pulls'], list)


@patch('program.providers.OpenAiProvider.get_completion')
@patch('program.providers.OpenAiProvider.get_access_token')
@patch('program.providers.GitHubProvider.get_pull_request_pulls')
def test_generate_pulls_report(mock_get_pull_request_pulls,
                               mock_get_openai_access_token,
                               mock_get_openai_completion,
                               manifest_json):
    """Test generate_pulls_report method of ReportGenerator."""

    mock_get_pull_request_pulls.return_value = [{
        'url': 'mock_url',
        'messages': []
    }]

    mock_get_openai_access_token.return_value = 'mock-access-token'

    mock_get_openai_completion.return_value = {
        'group_name': 'mock_url',
        'completion': {
            'choices': [{
                'message': {
                    'content': 'mock_completion'
                }
            }]
        }
    }

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    rg = ReportGenerator(manifest)
    pulls_report = rg.generate_pulls_report()

    assert isinstance(pulls_report, list)
