import json
import uuid
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, StreamingResponse
from sparkai.spark_proxy.openai_types import ChatInput, ChatCompletion, Choice, StreamChoice, ChatCompletionChunk, ChatMessage
from sparkai.spark_proxy.generate_message import generate_message
from sparkai.spark_proxy.generate_stream import generate_stream

from typing import Annotated
from sparkai.log import logger

app = FastAPI(title="Spark 2 OpenAI-Compatible API")


@app.post("/v1/chat/completions")
async def chat_endpoint(authorization: Annotated[str | None, Header()] = None, chat_input: ChatInput = None):
    key = authorization.split()[1]
    request_id = str(uuid.uuid4())
    if not chat_input.stream:
        response_message = generate_message(
            key=key,
            messages=chat_input.messages,
            functions=chat_input.functions,
            tools=chat_input.tools,
            temperature=chat_input.temperature,
            model=chat_input.model
        )
        print(chat_input.messages)
        finish_reason = "stop"
        if response_message.function_call is not None:
            finish_reason = "function_call"  # need to add this to follow the format of openAI function calling
        result = ChatCompletion(
            id=request_id,
            choices=[Choice.from_message(response_message, finish_reason)],
        )
        return result.dict(exclude_none=True)

    else:
        print(chat_input.messages)

        response_generator = generate_stream(
            key=key,
            messages=chat_input.messages,
            functions=chat_input.functions,
            tools=chat_input.tools,
            temperature=chat_input.temperature,
            model=chat_input.model,  # type: ignore
            stop=chat_input.stop
        )

        def get_response_stream():
            i = 0
            r_str = """"""
            for response in response_generator:
                if 'function_call' in response['payload']['choices']['text'][0]:
                    response = {
                        'delta': ChatMessage(
                            content=response['payload']['choices']['text'][0]['function_call']
                        ),
                        'finish_reason': 'tool_calls',
                        'index': i
                    }
                else:
                    print(response['payload']['choices']['text'][0]['content'], end='')
                    r_str += response['payload']['choices']['text'][0]['content']
                    for s in chat_input.stop or []:
                        if s in r_str:
                            yield "data: [DONE]\n\n"
                            return
                    response = {
                        'delta': ChatMessage(
                            content=response['payload']['choices']['text'][0]['content'],
                            role='assistant'
                        ),
                        'finish_reason': 'stop',
                        'index': i
                    }
                    i += 1
                chunk = StreamChoice(**response)
                result = ChatCompletionChunk(id=request_id, choices=[chunk])
                chunk_dic = result.dict(exclude_unset=True)
                chunk_data = json.dumps(chunk_dic, ensure_ascii=False)
                yield f"data: {chunk_data}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(get_response_stream(), media_type="text/event-stream")
