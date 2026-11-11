import asyncio
from uuid import uuid4
from nlip_sdk.nlip import NLIPMessage, NLIPSubMessage
from nlip_sdk.nlip_client import NLIPClient
from nlip_sdk.nlip_server import NLIPServer


class Worker(NLIPServer):
    async def handle(self, request, session):
        delegation = request.find_labeled_submessage("budget-delegation").content
        credits = delegation["max_credits"]

        await asyncio.sleep(0.1)  # placeholder for real action

        print(f"{self.identity}: simulated cost = {credits}")

        return NLIPMessage.structured({
            "agent": self.identity,
            "result": f"Processed: {request.extract_text()}",
            "simulated_cost": credits,
        })


class Coordinator(NLIPServer):
    def __init__(self, config, security):
        super().__init__("coordinator", security=security)
        self.client = NLIPClient.from_config(config, identity="coordinator", exclude=["coordinator"], security=security)

    async def handle(self, request, session):
        budget = request.find_labeled_submessage("budget-request").content["credits"]
        task = request.extract_text()
        workflow_id = uuid4().hex[:12]

        async def delegate(name):
            message = NLIPMessage.text(f"{name} task: {task}")
            message.add_submessage(NLIPSubMessage(
                format="structured",
                subformat="json",
                label="budget-delegation",
                content={
                    "workflow_id": workflow_id,
                    "delegation_id": f"{workflow_id}-{name}",
                    "parent_allocation_id": f"{workflow_id}-root",
                    "allocation_id": f"{workflow_id}-{name}",
                    "max_credits": budget,
                },
            ))
            response = await self.client.send(name, message, scope=session.id)
            return response.content

        names = ["search", "analysis", "writer"]
        results = await asyncio.gather(*(delegate(name) for name in names))
        total_cost = sum(item["simulated_cost"] for item in results)

        return NLIPMessage.structured({
            "workflow_id": workflow_id,
            "authorized_budget": budget,
            "total_simulated_cost": total_cost,
            "overspend": max(0, total_cost - budget),
            "results": results,
        })
