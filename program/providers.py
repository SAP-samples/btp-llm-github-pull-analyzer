"""
providers.py


This file contains classes for interacting with services like GitHub and OpenAI API.

The GitHubProvider class fetches and parses data related to pull requests
and associated comments from the GitHub API according to the given configuration.

The OpenAiProvider class interacts with the OpenAI API to get completions based
on the given prompts.

Both provider classes take configuration data during their initialization and include
methods for string representation of the object for debugging and logging purposes.
"""

import json
import logging
import time
import asyncio
import aiohttp
import requests
from program.config import GitHubConfiguration
from program.config import OpenAiConfiguration


class GitHubProvider:
    """Provider for the GitHub API."""

    def __init__(self,
                 config: GitHubConfiguration) -> None:
        self.logger = logging.getLogger('root')
        self.config = config

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()

    def get_pull_requests(self, url: str, headers: dict[str, str]) -> list[str]:
        """Get pull requests from the GitHub API via issue search."""

        params = {
            'page': 1
        }

        pull_request_urls = []
        i = 0
        while True:
            data = requests.get(url, headers=headers, params=params).json()

            if 'items' not in data:
                break

            if len(data['items']) == 0:
                break

            for issue_record in data['items']:
                issue_url = issue_record['url']
                self.logger.info('%s issue_url: %s', i, issue_url)

                pull_request_url = issue_record['pull_request']['url']
                self.logger.info('%s pull_request_url: %s', i, pull_request_url)

                pull_request_urls.append(pull_request_url)

                i = i + 1

            params["page"] += 1

        return pull_request_urls

    async def get_comments(self,
                           session: aiohttp.ClientSession,
                           data_url: str,
                           headers: dict,
                           student_login: str) -> list[dict[str, str]]:
        """Get comments from a GitHub API URL."""

        self.logger.debug('data_url: %s', data_url)

        comments_response = await session.get(data_url, headers=headers)
        comments_json = await comments_response.json()
        comments = []

        for comment in comments_json:
            author_login = comment['user']['login']
            role_name = 'user' if author_login == student_login else 'assistant'
            content = comment['body']

            if not content:
                self.logger.debug('skipping comment without body from %s', author_login)
                continue

            message = {
                'role': role_name,
                'content': comment['body']
            }

            message_json = json.dumps(message, default=vars, indent=2, sort_keys=True)
            self.logger.debug('message: %s', message_json)

            comments.append(message)

        return comments

    async def get_pull_request_pull(self,
                                    session: aiohttp.ClientSession,
                                    url: str,
                                    headers: dict[str, str]) -> dict[str, any]:
        """Get a pull request from the GitHub API."""

        response = await session.get(url, headers=headers)
        pull_request = await response.json()

        student_login = pull_request['user']['login']
        self.logger.info('student_login: %s', student_login)

        pull = {
            'url': url,
            'messages': []
        }

        if not pull_request["body"]:
            self.logger.debug('skipping pull message (empty body) from %s', student_login)
        else:
            pull['messages'].append({
                'role': 'user',
                'content': pull_request["body"]
            })

        comments = await self.get_comments(session,
                                           pull_request['comments_url'],
                                           headers,
                                           student_login)
        pull['messages'].extend(comments)

        comments = await self.get_comments(session,
                                           pull_request['review_comments_url'],
                                           headers,
                                           student_login)
        pull['messages'].extend(comments)

        return pull

    def get_pull_request_pulls(self) -> list[any]:
        """Get messages from pull request pulls."""

        url = f'{self.config.api_url}/search/issues?q=type:pr+state:closed+'
        url += f'label:{self.config.search_label}+'
        url += f'repo:{self.config.org_name}/{self.config.repo_name}'

        self.logger.debug('url: %s', url)

        headers = {
            'Authorization': f'token {self.config.api_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        pull_request_urls = self.get_pull_requests(url, headers)
        self.logger.info('pull_request_urls_found: %s', len(pull_request_urls))

        async def get_all_pull_request_pulls():
            async with aiohttp.ClientSession() as session:
                tasks = [self.get_pull_request_pull(session,
                                                    pull_request_url,
                                                    headers)
                         for pull_request_url in pull_request_urls]
                return await asyncio.gather(*tasks)

        result_pulls = asyncio.run(get_all_pull_request_pulls())

        pulls = []
        i = 0
        for pull in result_pulls:

            pull_url = pull['url']

            self.logger.info('%s pull_url: %s', i, pull_url)

            pulls.append(pull)
            i = i + 1

        self.logger.info('pulls_found: %s', len(pulls))

        return pulls


class OpenAiProvider:
    """Provider for the OpenAI API."""

    def __init__(self,
                 config: OpenAiConfiguration) -> None:
        self.logger = logging.getLogger('root')
        self.config = config
        self.access_token = self.get_access_token()

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()

    def get_access_token(self) -> str:
        """Get an access token from the OpenAI API."""

        client_id = self.config.client_id
        client_secret = self.config.client_secret
        uaa_url = self.config.uaa_url

        self.logger.debug('client_id: %s', client_id)
        self.logger.debug('client_secret: %s', client_secret)
        self.logger.debug('uaa_url: %s', uaa_url)

        params = {"grant_type": "client_credentials"}
        resp = requests.post(f"{uaa_url}/oauth/token",
                             auth=(client_id, client_secret),
                             params=params)

        return resp.json()["access_token"]

    async def get_completion(self,
                             session: aiohttp.ClientSession,
                             group_name: str,
                             messages: list[dict[str, str]]) -> dict[str, any]:
        """Get a completion from the OpenAI API."""

        # perform a deep copy of the data template
        data = json.loads(json.dumps(self.config.data_template))
        data_json = json.dumps(data, default=vars, indent=2, sort_keys=True)
        self.logger.debug('data (configuration): %s', data_json)

        data['messages'] = messages

        data_json = json.dumps(data, default=vars, indent=2, sort_keys=True)
        self.logger.debug('data: %s', data_json)

        headers = {
            "Authorization":  f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        completions_url = self.config.completions_url
        self.logger.debug('completions_url: %s', completions_url)

        while True:

            self.logger.info('invoking: %s', group_name)

            response = await session.post(completions_url,
                                          headers=headers,
                                          json=data)
            response_json = await response.json()
            status_code = response.status

            self.logger.debug('status_code: %s', status_code)

            response_json_pretty = json.dumps(response_json, default=vars, indent=2, sort_keys=True)
            self.logger.debug('response: %s', response_json_pretty)

            if status_code == 200:
                self.logger.info('completed: %s', group_name)
                return {
                    'group_name': group_name,
                    'completion': response_json
                }

            if status_code == 500:
                self.logger.info('rate limit exceeded, will retry: %s', group_name)
                time.sleep(1)
            else:
                raise RuntimeError(f"unexpected status code: {status_code}")

    def get_completions(self, message_groups: dict[str, list[dict[str, str]]]) -> dict[str, any]:
        """Get completions from the OpenAI API for a group of message sets."""

        async def get_all_completions():
            async with aiohttp.ClientSession() as session:
                tasks = [self.get_completion(session,
                                             group_name,
                                             messages)
                         for group_name, messages in message_groups.items()]
                return await asyncio.gather(*tasks)

        result_completions = asyncio.run(get_all_completions())

        return result_completions
