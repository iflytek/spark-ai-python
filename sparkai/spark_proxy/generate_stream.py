from typing import Optional, List, Generator, Dict, Any
from sparkai.spark_proxy.openai_types import ChatMessage, Function, Tool, FunctionCall, ToolCall

from sparkai.spark_proxy.spark_api import SparkAPI

s_k = "key&secret&appid"


def generate_stream(
        *,
        key: str,
        model: str,
        messages: List[ChatMessage],
        functions: Optional[List[Function]] = None,
        tools: Optional[List[Tool]] = None,
        temperature: float = 0.7,
        stop: list[str] = None
) -> Generator[Dict, Any, Any]:

    s_api = SparkAPI(key, model=model, temperature=temperature)
    # print('generate_message ~~~~~')
    # print('messages:', messages)
    # print('functions:', functions)
    # print('tools:', tools)
    # print('temperature:', temperature)

    function_list = []
    if functions:
        for t in functions:
            function_list.append(
                {
                    'name': t.name,
                    'description': t.description,
                    'parameters': t.parameters
                }
            )
    if tools:
        for t in tools:
            f = t.function
            function_list.append(
                {
                    'name': f.name,
                    'description': f.description,
                    'parameters': f.parameters
                }
            )
    return s_api.yield_call(messages, function_list)
    # content, function_call = s_api.call(messages, function_list)
    # print("resp------------")
    # print('content::', content)
    # print('function_call::', function_call)
    # if function_call:
    #     f = FunctionCall(name=function_call['name'], arguments=function_call['arguments'], id="call_" + 'a' * 24)
    #     yield ChatMessage(
    #         content=content,
    #         role='assistant',
    #         tool_calls=[ToolCall(function=f)]
    #     )
    #
    # yield ChatMessage(
    #     content=content,
    #     role='assistant')
