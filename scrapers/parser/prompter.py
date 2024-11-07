import os
import json
from litellm import acompletion
from dotenv import load_dotenv

os.environ["MISTRAL_API_KEY"] = os.getenv('MISTRAL_API_KEY')

async def extractData(html):
    load_dotenv()
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