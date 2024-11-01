from __future__ import annotations

import logging
from typing import List, Optional

from openai import APIError, AzureOpenAI, OpenAI
from openai.types import Model

from autogpt.core.resource.model_providers.openai import (
    OPEN_AI_MODELS,
    OpenAICredentials,
)
from autogpt.core.resource.model_providers.schema import ChatModelInfo
from autogpt.singleton import Singleton

logger = logging.getLogger(__name__)

_all_models = [Model(id='gpt-4-turbo', created=1712361441, object='model', owned_by='system'), Model(id='gpt-4-turbo-2024-04-09', created=1712601677, object='model', owned_by='system'), Model(id='tts-1', created=1681940951, object='model', owned_by='openai-internal'), Model(id='tts-1-1106', created=1699053241, object='model', owned_by='system'), Model(id='chatgpt-4o-latest', created=1723515131, object='model', owned_by='system'), Model(id='dall-e-2', created=1698798177, object='model', owned_by='system'), Model(id='whisper-1', created=1677532384, object='model', owned_by='openai-internal'), Model(id='gpt-4-turbo-preview', created=1706037777, object='model', owned_by='system'), Model(id='gpt-4o-audio-preview', created=1727460443, object='model', owned_by='system'), Model(id='gpt-3.5-turbo-instruct', created=1692901427, object='model', owned_by='system'), Model(id='gpt-4o-audio-preview-2024-10-01', created=1727389042, object='model', owned_by='system'), Model(id='gpt-4-0125-preview', created=1706037612, object='model', owned_by='system'), Model(id='gpt-3.5-turbo-0125', created=1706048358, object='model', owned_by='system'), Model(id='gpt-3.5-turbo', created=1677610602, object='model', owned_by='openai'), Model(id='babbage-002', created=1692634615, object='model', owned_by='system'), Model(id='davinci-002', created=1692634301, object='model', owned_by='system'), Model(id='gpt-4o-realtime-preview-2024-10-01', created=1727131766, object='model', owned_by='system'), Model(id='dall-e-3', created=1698785189, object='model', owned_by='system'), Model(id='gpt-4o-realtime-preview', created=1727659998, object='model', owned_by='system'), Model(id='gpt-4o-2024-08-06', created=1722814719, object='model', owned_by='system'), Model(id='gpt-4o', created=1715367049, object='model', owned_by='system'), Model(id='gpt-4o-mini', created=1721172741, object='model', owned_by='system'), Model(id='gpt-4o-2024-05-13', created=1715368132, object='model', owned_by='system'), Model(id='gpt-4o-mini-2024-07-18', created=1721172717, object='model', owned_by='system'), Model(id='tts-1-hd', created=1699046015, object='model', owned_by='system'), Model(id='tts-1-hd-1106', created=1699053533, object='model', owned_by='system'), Model(id='gpt-4-1106-preview', created=1698957206, object='model', owned_by='system'), Model(id='text-embedding-ada-002', created=1671217299, object='model', owned_by='openai-internal'), Model(id='gpt-3.5-turbo-16k', created=1683758102, object='model', owned_by='openai-internal'), Model(id='text-embedding-3-small', created=1705948997, object='model', owned_by='system'), Model(id='text-embedding-3-large', created=1705953180, object='model', owned_by='system'), Model(id='gpt-3.5-turbo-1106', created=1698959748, object='model', owned_by='system'), Model(id='gpt-4-0613', created=1686588896, object='model', owned_by='openai'), Model(id='gpt-4', created=1687882411, object='model', owned_by='openai'), Model(id='gpt-3.5-turbo-instruct-0914', created=1694122472, object='model', owned_by='system')]

class ApiManager(metaclass=Singleton):
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0
        self.models: Optional[list[Model]] = None

    def reset(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0.0
        self.models = None

    def update_cost(self, prompt_tokens, completion_tokens, model):
        """
        Update the total cost, prompt tokens, and completion tokens.

        Args:
        prompt_tokens (int): The number of tokens used in the prompt.
        completion_tokens (int): The number of tokens used in the completion.
        model (str): The model used for the API call.
        """
        # the .model property in API responses can contain version suffixes like -v2
        model = model[:-3] if model.endswith("-v2") else model
        model_info = OPEN_AI_MODELS[model]

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost += prompt_tokens * model_info.prompt_token_cost / 1000
        if isinstance(model_info, ChatModelInfo):
            self.total_cost += (
                completion_tokens * model_info.completion_token_cost / 1000
            )

        logger.debug(f"Total running cost: ${self.total_cost:.3f}")

    def set_total_budget(self, total_budget):
        """
        Sets the total user-defined budget for API calls.

        Args:
        total_budget (float): The total budget for API calls.
        """
        self.total_budget = total_budget

    def get_total_prompt_tokens(self):
        """
        Get the total number of prompt tokens.

        Returns:
        int: The total number of prompt tokens.
        """
        return self.total_prompt_tokens

    def get_total_completion_tokens(self):
        """
        Get the total number of completion tokens.

        Returns:
        int: The total number of completion tokens.
        """
        return self.total_completion_tokens

    def get_total_cost(self):
        """
        Get the total cost of API calls.

        Returns:
        float: The total cost of API calls.
        """
        return self.total_cost

    def get_total_budget(self):
        """
        Get the total user-defined budget for API calls.

        Returns:
        float: The total budget for API calls.
        """
        return self.total_budget

    def get_models(self, openai_credentials: OpenAICredentials) -> List[Model]:
        """
        Get list of available GPT models.

        Returns:
            list[Model]: List of available GPT models.
        """
        if self.models is not None:
            return self.models

        try:
            if openai_credentials.api_type == "azure":
                all_models = _all_models
                # all_models = (
                #     AzureOpenAI(**openai_credentials.get_api_access_kwargs())
                #     .models.list()
                #     .data
                # )
            else:
                all_models = _all_models
                # all_models = (
                #     OpenAI(**openai_credentials.get_api_access_kwargs())
                #     .models.list()
                #     .data
                # )
            self.models = [model for model in all_models if "gpt" in model.id]
        except APIError as e:
            logger.error(e.message)
            exit(1)

        return self.models
