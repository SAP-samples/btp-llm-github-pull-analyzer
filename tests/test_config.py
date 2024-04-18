"""
test_config.py

This module defines unit tests for the config.py module.
"""

import json
from io import StringIO
import pytest
from program.config import Manifest
from program.config import GitHubConfiguration
from program.config import OpenAiConfiguration
from program.config import ReportConfiguration


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


def test_github_configuration(manifest_json):
    """Test GitHub configuration."""

    manifest_dict = json.loads(manifest_json)
    github_config = GitHubConfiguration(manifest_dict["github"])

    assert github_config.org_name == "mock-org-name"
    assert github_config.repo_name == "mock-repo-name"
    assert github_config.api_url == "https://github.tools.mock/api/v3"
    assert isinstance(github_config.api_token, str)
    assert isinstance(github_config.search_label, str)


def test_openai_configuration(manifest_json):
    """Test OpenAI configuration."""

    manifest_dict = json.loads(manifest_json)
    openai_config = OpenAiConfiguration(manifest_dict["openai"])

    assert openai_config.completions_url == "https://azure-openai.mock/chat/completions?api-version=mock"
    assert openai_config.uaa_url == "https://mock-openai.authentication.mock"
    assert isinstance(openai_config.client_id, str)
    assert isinstance(openai_config.client_secret, str)
    assert openai_config.data_template["deployment_id"] == "gpt-mock-deployment-id"
    assert isinstance(openai_config.data_template["messages"], list)
    assert openai_config.data_template["max_tokens"] == 4000
    assert openai_config.data_template["temperature"] == 0.7
    assert openai_config.data_template["frequency_penalty"] == 0
    assert openai_config.data_template["presence_penalty"] == 0
    assert openai_config.data_template["top_p"] == 0.95


def test_report_configuration(manifest_json):
    """Test report configuration."""

    manifest_dict = json.loads(manifest_json)
    report_config = ReportConfiguration(manifest_dict["report"])

    assert report_config.grounding_prompt == "test-grounding-prompt"
    assert report_config.pull_prompt == "test-pull-prompt"
    assert report_config.overview_prompt == "test-overview-prompt"


def test_manifest_load(manifest_json):
    """Test loading manifest from JSON."""

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    assert manifest.github.org_name == "mock-org-name"
    assert manifest.openai.client_id == "mock-client-id"
    assert manifest.report.grounding_prompt == "test-grounding-prompt"
    assert manifest.report.pull_prompt == "test-pull-prompt"
    assert manifest.report.overview_prompt == "test-overview-prompt"
