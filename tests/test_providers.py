"""
test_providers.py

Unit tests for SumoLogicProvider and GardenerProvider classes of the providers module.
"""

from io import StringIO
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from pytest import mark
from pytest import fixture
from program.config import Manifest
from program.providers import GitHubProvider
from program.providers import OpenAiProvider


# pylint: disable=redefined-outer-name
# pylint: disable=duplicate-code
@fixture
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


@patch('requests.get')
def test_get_pull_requests(mock_get, manifest_json):
    """Test get_pull_requests method of GitHubProvider."""

    mock_get.return_value.json.return_value = []
    mock_get.return_value.status_code = 200

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    github_provider = GitHubProvider(manifest.github)

    pull_request_urls = github_provider.get_pull_requests('mock_url', 'mock_headers')

    assert len(pull_request_urls) == 0


@mark.asyncio
async def test_get_comments(manifest_json):
    """Test get_comments method of GitHubProvider."""

    return_json = [{
        'user': {
            'login': 'mock_student_login'
        },
        'body': 'mock_comment'
    }]

    mock_response = MagicMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json = AsyncMock(return_value=return_json)

    mock_session = AsyncMock()
    mock_session.get.return_value = mock_response

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    github_provider = GitHubProvider(manifest.github)

    comments = await github_provider.get_comments(mock_session,
                                                  'mock_url',
                                                  'mock_headers',
                                                  'mock_student_login')

    assert len(comments) == 1
    assert comments[0]['role'] == 'user'
    assert comments[0]['content'] == 'mock_comment'


@patch('program.providers.GitHubProvider.get_comments')
@mark.asyncio
async def test_get_pull_request_pull(mock_get_github_comments,
                                     manifest_json):
    """Test get_pull_request_pull method of GitHubProvider."""

    return_json = {
        'user': {
            'login': 'mock_student_login'
        },
        'body': 'mock_body',
        'comments_url': 'mock_comments_url',
        'review_comments_url': 'mock_review_comments_url'
    }

    mock_response = MagicMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json = AsyncMock(return_value=return_json)

    mock_session = AsyncMock()
    mock_session.get.return_value = mock_response

    mock_get_github_comments.return_value = [{
        'role': 'user',
        'content': 'mock_comment'
    }]

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    github_provider = GitHubProvider(manifest.github)

    pull = await github_provider.get_pull_request_pull(mock_session,
                                                       'mock_url',
                                                       'mock_headers')

    mock_session.get.assert_called_once()
    mock_response.json.assert_called_once()
    assert mock_get_github_comments.call_count == 2
    assert pull['url'] == 'mock_url'
    assert pull['messages'][0]['role'] == 'user'
    assert pull['messages'][0]['content'] == 'mock_body'
    assert pull['messages'][1]['role'] == 'user'
    assert pull['messages'][1]['content'] == 'mock_comment'


@patch('program.providers.GitHubProvider.get_pull_request_pull')
@patch('program.providers.GitHubProvider.get_pull_requests')
def test_get_pull_request_pulls(mock_get_github_pull_requests,
                                mock_get_github_pull_request_pull,
                                manifest_json):
    """Test get_pull_request_pulls method of GitHubProvider."""

    mock_get_github_pull_requests.return_value = ['mock_url']

    mock_get_github_pull_request_pull.return_value = {
        'url': 'mock_url',
        'messages': [
            {
                'role': 'user',
                'content': 'mock_comment'
            }
        ]
     }

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    github_provider = GitHubProvider(manifest.github)

    pulls = github_provider.get_pull_request_pulls()

    assert pulls[0]['url'] == 'mock_url'
    mock_get_github_pull_request_pull.assert_called_once()


@patch('requests.post')
def test_get_openai_access_token(mock_post, manifest_json):
    """Test get_access_token method of OpenAiProvider."""

    mock_post.return_value.json.return_value = {
        'access_token': 'mock-access_token'
    }
    mock_post.return_value.status_code = 200

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    openai_provider = OpenAiProvider(manifest.openai)

    assert openai_provider.access_token == 'mock-access_token'
    mock_post.assert_called_once()


@patch('program.providers.OpenAiProvider.get_access_token')
@mark.asyncio
async def test_get_openai_completion(mock_get_openai_access_token,
                                     manifest_json):
    """Test get_completion method of OpenAiProvider."""

    return_json = {
        'choices': [{
            'message': {
                'content': 'mock_completion'
            }
        }]
    }

    mock_response = MagicMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=return_json)

    mock_session = AsyncMock()
    mock_session.post.return_value = mock_response

    mock_get_openai_access_token.return_value = 'mock-access_token'

    manifest = Manifest()
    json_data = StringIO(manifest_json)
    manifest.load(json_data)

    openai_provider = OpenAiProvider(manifest.openai)

    completion = await openai_provider.get_completion(mock_session,
                                                      'mock_group_name',
                                                      ["message1", "message2"])

    mock_session.post.assert_called_once()
    mock_response.json.assert_called_once()
    assert completion['group_name'] == 'mock_group_name'
    assert completion['completion']['choices'][0]['message']['content'] == 'mock_completion'


@patch('program.providers.OpenAiProvider.get_completion')
@patch('program.providers.OpenAiProvider.get_access_token')
def test_get_openai_completions(mock_get_openai_access_token,
                                mock_get_openai_completion,
                                manifest_json):
    """Test get_completions method of OpenAiProvider."""

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

    openai_provider = OpenAiProvider(manifest.openai)

    completions = openai_provider.get_completions({
        'mock_url': [{
            'role': 'user',
            'content': 'mock_comment'
        }]
    })

    mock_get_openai_completion.assert_called_once()
    assert completions[0]['group_name'] == 'mock_url'
    assert completions[0]['completion']['choices'][0]['message']['content'] == 'mock_completion'
