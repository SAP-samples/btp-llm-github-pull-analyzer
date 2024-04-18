"""
report.py:

This script contains the ReportGenerator class that generates a report
from configuration data (Manifest).

It interacts with GitHubProvider and OpenAiProvider which make API calls to
generate data for the report.
"""

import json
import logging
from program.config import Manifest
from program.providers import GitHubProvider
from program.providers import OpenAiProvider


class ReportGenerator:
    """Generates a report from the manifest."""

    def __init__(self,
                 manifest: Manifest) -> None:
        self.logger = logging.getLogger('root')
        self.config = manifest.report
        self.github_provider = GitHubProvider(manifest.github)
        self.openai_provider = OpenAiProvider(manifest.openai)

    def __str__(self) -> str:
        return json.dumps(self, default=vars, indent=2, sort_keys=True)

    def __repr__(self) -> str:
        return self.__str__()

    def generate_report(self) -> any:
        """Generate a report from the manifest."""

        pulls_report = self.generate_pulls_report()
        summary_report = self.generate_summary_report(pulls_report)

        return summary_report

    def generate_summary_report(self, pulls) -> any:
        """Generate a summary report of the pulls."""

        messages = [{
            'role': 'system',
            'content': self.config.grounding_prompt
        }]
        for pull in pulls:

            pull_json = json.dumps(pull, default=vars, indent=2, sort_keys=True)
            self.logger.debug('pull: %s', pull_json)

            messages.append({
                'role': 'assistant',
                'content': pull['analysis']
            })

        messages.append(
            {
                'role': 'user',
                'content': self.config.overview_prompt
            }
        )

        total_messages = len(messages)
        self.logger.debug('total_messages: %s', total_messages)

        message_groups = {
            'summary': messages
        }

        completions = self.openai_provider.get_completions(message_groups)

        completions_json = json.dumps(completions, default=vars, indent=2, sort_keys=True)
        self.logger.debug('completions: %s', completions_json)

        summary_report = {
            'prompts': {
                'grounding': self.config.grounding_prompt,
                'pull': self.config.pull_prompt,
                'overview': self.config.overview_prompt
            },
            'summary': completions[0]['completion']['choices'][0]['message']['content'],
            'pulls': pulls
        }

        return summary_report

    def generate_pulls_report(self) -> list[any]:
        """Generate a report of the pulls."""

        pulls = self.github_provider.get_pull_request_pulls()
        pulls_json = json.dumps(pulls, default=vars, indent=2, sort_keys=True)
        self.logger.debug('pulls: %s', pulls_json)

        message_groups = {}
        for pull in pulls:
            pull_url = pull['url']
            self.logger.info('pull_url: %s', pull_url)

            messages = []
            messages.append({
                'role': 'system',
                'content': self.config.grounding_prompt
            })
            messages.extend(pull['messages'])

            messages.append(
                {
                    'role': 'user',
                    'content': self.config.pull_prompt
                }
            )

            total_messages = len(messages)
            self.logger.debug('total_messages: %s', total_messages)

            message_groups[pull_url] = messages

        completions = self.openai_provider.get_completions(message_groups)

        completions_json = json.dumps(completions, default=vars, indent=2, sort_keys=True)
        self.logger.debug('completions: %s', completions_json)

        resulting_pulls = []
        for completion_info in completions:
            completion_info_json = json.dumps(completion_info,
                                              default=vars,
                                              indent=2,
                                              sort_keys=True)
            self.logger.debug('completion_info: %s', completion_info_json)

            pull_analysis = {
                'url': completion_info['group_name'],
                'analysis': completion_info['completion']['choices'][0]['message']['content']
            }

            pull_analysis_json = json.dumps(pull_analysis, default=vars, indent=2, sort_keys=True)
            self.logger.debug('pull_analysis: %s', pull_analysis_json)

            resulting_pulls.append(pull_analysis)

        return resulting_pulls
