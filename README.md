# GitHub Pull Request Analyzer (with SAP AI Core)

[![REUSE status](https://api.reuse.software/badge/github.com/SAP-samples/github-pull-analyzer)](https://api.reuse.software/info/github.com/SAP-samples/github-pull-analyzer)

The GitHub Pull Request Analyzer (with SAP AI Core) automates the task of analyzing pull request in GitHub, summarizing the themes, sentiments, points of resonation/repulsion, and difficulties in the collected interactions. The results are outputted as a JSON report which is easy to parse and process.

## Files in the Source Code

- [**main.py**](program/main.py) - Main driver of the program. It sets up logging, parsing command-line arguments, loading configuration, generating and processing the report.
- [**config.py**](program/config.py) - Contains classes to configure and load configuration from a JSON manifest.
- [**providers.py**](program/providers.py) - Contains classes that provide the interaction with the GitHub and OpenAI LLM APIs.
- [**report.py**](program/report.py) - Contains classes that generate and process the report based on the provided configuration and data retrieved from APIs.

## Files in the Source Code

- [**main.py**](program/main.py) - Main driver of the program. It sets up logging, parsing command-line arguments, loading configuration, generating and processing the report.
- [**config.py**](program/config.py) - Contains classes to configure and load configuration from a JSON manifest.
- [**providers.py**](program/providers.py) - Contains classes that provide the interaction with the GitHub and OpenAI LLM APIs.
- [**report.py**](program/report.py) - Contains classes that generate and process the report based on the provided configuration and data retrieved from APIs.

## Setup & Run the Utility Locally

To setup a local environment and run the program from scratch, perform the following steps:

### Prerequisites

- **Python** - Execution engine
- **Poetry** - Modern package manager for Python
- **GitHub** - Authorized access to GitHub API
  - See [GitHub REST API documentation](https://docs.github.com/en/rest)
- **SAP AI Core** - Authorized access to OpenAI Completions API via SAP AI Core
  - See [Generative AI Hub in SAP AI Core](https://help.sap.com/docs/sap-ai-core/sap-ai-core-service-guide/models-and-scenarios-in-generative-ai-hub) for setup instructions

### Configuration

The manifest.json file configures the analyzer and should be set up as follows:

```json
{
    "github": {
        "org_name": "mock-org",
        "repo_name": "mock-repo",
        "api_url": "https://<github-url>/api/v3",
        "api_token": (str),
        "search_label": (str)
    },
    "openai": {
        "completions_url": "https://<btp-llm-proxy-url>/chat/completions?api-version=<version>",
        "uaa_url": "https://<btp-uaa-authentication-url>",
        "client_id": (str),
        "client_secret": (str),
        "data_template": {
            "deployment_id": "gpt-4-32k",
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
        "grounding_prompt": "Interactions between the requestor (user) and reviewer(s) (assistant)",
        "pull_prompt": "Summarize the themes, sentiments, points of resonation, points of repulsion and difficulties for this interaction",
        "overview_prompt": "Summarize the themes, sentiments, points of resonation, points of repulsion and difficulties in aggregate for all interactions"
    }
}
```

During the runtime:

* The manifest is expected to be input through the standard input stream (stdin)
* All logging output (INFO, DEBUG, ERROR) is directed through the standard error stream (stderr)
* The resulting final report JSON is delivered through the standard output stream (stdout)

### Execution

1. **Clone the Source Code Repository**

```bash
git clone <url-to-repo>
cd <repo-dir>
```

2. **Setup the Python Environment Using Poetry**

```bash
poetry shell
```

3. **Install Dependencies**

```bash
poetry install
```

4. **Running Unit Tests with verbose logging**

```bash
poetry run pytest --verbose
```

5. **Running Unit Tests normally**

```bash
poetry run pytest
```

6. **Running the Program to display help**

```bash
poetry run python3 -m program.main -h
```

7. **Running the Program with verbose logging**

```bash
# Adjust as appropriate
MANIFEST_JSON_PATH=~/Downloads/mock/manifest.json
SUMMARY_LOG_PATH=~/Downloads/mock/summary.log
SUMMARY_JSON_PATH=~/Downloads/mock/summary.json

cat ${MANIFEST_JSON_PATH} | \
    poetry run python3 -m program.main --verbose \
    2> ${SUMMARY_LOG_PATH} | jq '.' \
    > ${SUMMARY_JSON_PATH}
```

8. **Running the Program normally**

```bash
# Adjust as appropriate
MANIFEST_JSON_PATH=~/Downloads/mock/manifest.json
SUMMARY_LOG_PATH=~/Downloads/mock/summary.log
SUMMARY_JSON_PATH=~/Downloads/mock/summary.json

cat ${MANIFEST_JSON_PATH} | \
    poetry run python3 -m program.main \
    2> ${SUMMARY_LOG_PATH} | jq '.' \
    > ${SUMMARY_JSON_PATH}
```

9. **Useful jq queries**

```bash
# Adjust as appropriate
SUMMARY_JSON_PATH=~/Downloads/mock/summary.json

jq -r '.pulls[] | .url' ${SUMMARY_JSON_PATH} | wc -l
jq -r '.pulls[] | .url' ${SUMMARY_JSON_PATH}
jq -r '.pulls[] | .analysis' ${SUMMARY_JSON_PATH}
jq -r '.summary' ${SUMMARY_JSON_PATH}
```

## How to obtain support

[Create an issue](https://github.com/SAP-samples/btp-llm-github-pull-analyzer/issues) in this repository if you find a bug or have questions about the content.

For additional support, [ask a question in SAP Community](https://answers.sap.com/questions/ask.html).

## Contributing

If you wish to contribute code, offer fixes or improvements, please send a pull request. Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

## License

Copyright (c) 2024 SAP SE or an SAP affiliate company. All rights reserved. This project is licensed under the Apache Software License, version 2.0 except as noted otherwise in the [LICENSE](LICENSE) file.
