from typing import Optional, List, Generator, Dict, Any
from openai_types import ChatMessage, Function, Tool, FunctionCall, ToolCall

from spark_api import SparkAPI

s_k = "key&secret&appid"


def generate_stream(
        *,
        model: str,
        messages: List[ChatMessage],
        functions: Optional[List[Function]] = None,
        tools: Optional[List[Tool]] = None,
        temperature: float = 0.7,
) -> Generator[Dict, Any, Any]:
    s_api = SparkAPI(s_k, model=model, temperature=temperature)
    print('generate_message ~~~~~')
    print('messages:', messages)
    print('functions:', functions)
    print('tools:', tools)
    print('temperature:', temperature)

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
