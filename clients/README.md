# AIOpsLab Clients

This directory contains implementation of clients that can interact with AIOPsLab.
These clients are some baselines that we have implemented and evaluated to help you get started.

## Clients

- [GPT](/clients/gpt.py): A naive GPT4-based LLM agent with only shell access.
- [ReAct](/clients/react.py): A naive LLM agent that uses the ReAct framework.
- [FLASH](/clients/flash.py): A naive LLM agent that uses status supervision and hindsight integration components to ensure the high reliability of workflow execution.

Note: The script /clients/gpt_managed_identity.py utilizes Azure Managed Identity to access Azure OpenAI resources. Please ensure the required Azure configuration is provided using the /configs/example_azure_config.yml file, or use it as a template to create a new configuration file.
