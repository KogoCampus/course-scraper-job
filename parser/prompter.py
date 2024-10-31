import os
import json
from litellm import acompletion

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     api_key="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"
# )

# os.environ["OPENAI_API_KEY"] = "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"
os.environ["MISTRAL_API_KEY"] = "nRZ4d8qtAG3qY1LQKZ3L3mF9sko84Ogr"

async def extractData(html):
    model = "mistral/mistral-large-latest"

    messages = [
        {
            "role": "user",
            "content": "I just want the output appear only an array of data that can be more than one according to this json format: {sectionName, deliveryMethod, term, activity, credits, startDate, startTime, endDate, endTime, days} extracted from this html: "+html,
        },
    ]

    response = await acompletion(
        model=model,
        messages=messages,
        response_format = {
            "type": "json_object",
        },
    )
    # print(json.dumps(json.loads(response.choices[0].message.content)))
    return json.loads(response.choices[0].message.content)

    
    # chat_response = await client.chat.complete_async(
    #     model = model,
    #     messages = messages,
    #     response_format = {
    #         "type": "json_object",
    #     }
    # )

    # print(chat_response.choices[0].message.content)
    # print(type(chat_response.choices[0].message.content))