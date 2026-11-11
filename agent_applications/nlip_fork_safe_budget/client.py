import asyncio
import json
from nlip_sdk.nlip import NLIPMessage, NLIPSubMessage
from nlip_sdk.nlip_client import NLIPClient


async def main():
    client = NLIPClient({"coordinator": "http://127.0.0.1:8010/nlip"}, identity="user")
    message = NLIPMessage.text("Research how the integration of AI tools in the workplace impacts employee job satisfaction")
    message.add_submessage(NLIPSubMessage(
        format="structured",
        subformat="json",
        label="budget-request",
        content={"credits": 100},
    ))

    response = await client.send("coordinator", message)
    print(json.dumps(response.content, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
