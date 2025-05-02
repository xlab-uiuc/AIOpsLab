# Copyright contributors to the ITBench project. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from typing import Dict, Optional

import litellm
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


class LiteLLMBackend:

    def __init__(
        self,
        provider: str,
        model_name: str,
        url: str,
        api_key: str,
        api_version: str,
        seed: int,
        top_p: float,
        temperature: float,
        reasoning_effort: str,
        thinking_tools: str,
        thinking_budget_tools: int,
        max_tokens: int,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        self.provider = provider
        self.model_name = model_name
        self.url = url
        self.api_key = api_key
        self.api_version = api_version
        self.temperature = temperature
        self.seed = seed
        self.top_p = top_p
        self.reasoning_effort = reasoning_effort
        self.thinking_tools = thinking_tools
        self.thinking_budget_tools = thinking_budget_tools
        self.max_tokens = max_tokens
        self.extra_headers = extra_headers
        litellm.drop_params = True

    def inference(self, payload: list[dict[str, str]]) -> str:

        kwargs = {
            "model": f"{self.provider}/{self.model_name}",
            "api_key": self.api_key,
            "api_base": self.url,
            "api_version": self.api_version,
            "seed": self.seed,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "reasoning_effort": self.reasoning_effort,
            "max_tokens": self.max_tokens,
            "messages": payload,
            "extra_headers": self.extra_headers,
        }

        completion = litellm.completion(**kwargs)
        
        return completion
