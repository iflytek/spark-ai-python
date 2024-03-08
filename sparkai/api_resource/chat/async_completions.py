#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: completions
@time: 2024/02/23
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.


from __future__ import annotations
from typing import Union, List, Optional, TYPE_CHECKING
from typing_extensions import Literal
from ...core._base_api import BaseAPI
from ...core._base_type import NotGiven, NOT_GIVEN, Headers
from ...types.chat.chat_completion import Completion


class AsyncCompletions(BaseAPI):
    def __init__(self, client) -> None:
        super().__init__(client)

    def create(
            self,
            *,
            model: str,
            request_id: Optional[str] | NotGiven = NOT_GIVEN,
            do_sample: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
            stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
            temperature: Optional[float] | NotGiven = NOT_GIVEN,
            top_p: Optional[float] | NotGiven = NOT_GIVEN,
            max_tokens: int | NotGiven = NOT_GIVEN,
            seed: int | NotGiven = NOT_GIVEN,
            messages: Union[str, List[str], List[int], object, None],
            stop: Optional[Union[str, List[str], None]] | NotGiven = NOT_GIVEN,
            sensitive_word_check: Optional[object] | NotGiven = NOT_GIVEN,
            tools: Optional[object] | NotGiven = NOT_GIVEN,
            tool_choice: str | NotGiven = NOT_GIVEN,
            extra_headers: Headers | None = None,
            disable_strict_validation: Optional[bool] | None = None,
            uid: str,
            op_open,
            on_mesage,
    ) -> Completion:
        if len(model) == 0:
            model = "v3.5"

        uri = "/v3.5/chat"
        domain = "generalv3.5"
        if model == "v3.5":
            domain = "generalv3.5"
            uri = "/v3.5/chat"
        elif model == "v3":
            domain = "generalv3"
            uri = "/v3.1/chat"
        elif model == "v2":
            domain = "generalv2"
            uri = "/v2.1/chat"
        elif model == "v1.5":
            domain = "general"
            uri = "/v1.1/chat"

        self._client.uri = uri    
                      
        self._client.stream(on_open=op_open, on_message=on_mesage)