"""
config.py

This module defines various classes to store configurations and
a manifest for the BTP LLM GitHub Pull Analyzer program. Each class
establishes a structure for different types of configuration -
GitHubConfiguration, OpenAiConfiguration,
ReportConfiguration and the Manifest
which holds instances of the previous configurations.

The Manifest class has a load() method, which takes an input stream
containing a JSON file, and initializes the manifest object's
attributes accordingly.

See README.md for more details.
"""

import json
from typing import IO


class GitHubConfiguration:
    """Configuration for the GitHub provider."""

    def __init__(self,
                 config: dict[str, any]) -> None:
        self.org_name = config['org_name']
        self.repo_name = config['repo_name']
        self.api_url = config['api_url']
        self.api_token = config['api_token']
        self.search_label = config['search_label']

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()


class OpenAiConfiguration:
    """Configuration for the OpenAI provider."""

    def __init__(self,
                 config: dict[str, any]) -> None:
        self.completions_url = config['completions_url']
        self.uaa_url = config['uaa_url']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.data_template = config['data_template']

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()


class ReportConfiguration:
    """Configuration for the report generator."""

    def __init__(self,
                 config: dict[str, any]) -> None:
        self.grounding_prompt = config['grounding_prompt']
        self.pull_prompt = config['pull_prompt']
        self.overview_prompt = config['overview_prompt']

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()


class Manifest:
    """Manifest for the BTP LLM GitHub Pull Analyzer program."""

    def __init__(self) -> None:
        self.github = None
        self.openai = None
        self.report = None

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()

    def load(self,
             input_stream: IO[str]) -> None:
        """Load the manifest from an input stream."""

        manifest_json = json.load(input_stream)

        self.github = GitHubConfiguration(manifest_json['github'])
        self.openai = OpenAiConfiguration(manifest_json['openai'])
        self.report = ReportConfiguration(manifest_json['report'])
