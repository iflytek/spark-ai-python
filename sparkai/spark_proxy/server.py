import json
import uuid
from fastapi import FastAPI

from fastapi.responses import JSONResponse, StreamingResponse
from sparkai.spark_proxy.openai_types import ChatInput, ChatCompletion, Choice, StreamChoice, ChatCompletionChunk, ChatMessage
from sparkai.spark_proxy.generate_message import generate_message
from sparkai.spark_proxy.generate_stream import generate_stream

app = FastAPI(title="Spark Proxy OpenAI-Compatible API")


@app.post("/v1/chat/completions")
async def chat_endpoint(chat_input: ChatInput):
    request_id = str(uuid.uuid4())
    if not chat_input.stream:
        response_message = generate_message(
            messages=chat_input.messages,
            functions=chat_input.functions,
            tools=chat_input.tools,
            temperature=chat_input.temperature,
            model=chat_input.model
        )
        finish_reason = "stop"
        if response_message.function_call is not None:
            finish_reason = "function_call"  # need to add this to follow the format of openAI function calling
        result = ChatCompletion(
            id=request_id,
            choices=[Choice.from_message(response_message, finish_reason)],
        )
        return result.dict(exclude_none=True)

    else:
        response_generator = generate_stream(
            messages=chat_input.messages,
            functions=chat_input.functions,
            tools=chat_input.tools,
            temperature=chat_input.temperature,
            model=chat_input.model,  # type: ignore
        )

        def get_response_stream():
            i = 0
            for response in response_generator:
                print(response['payload']['choices']['text'][0]['content'], end='')
                if 'function_call' in response['payload']['choices']['text'][0]:
                    response = {
                        'delta': ChatMessage(
                            content=response['payload']['choices']['text'][0]['function_call']
                        ),
                        'finish_reason': 'tool_calls',
                        'index': i
                    }
                else:
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
