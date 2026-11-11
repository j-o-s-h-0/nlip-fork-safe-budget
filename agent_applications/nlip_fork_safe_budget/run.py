import sys
from pathlib import Path
import uvicorn
from nlip_sdk.config import load_config
from nlip_sdk.nlip_security_extensions import SecurityExtensionManager
from .agents import Coordinator, Worker


config = load_config(Path(__file__).with_name("config.toml"))
name = sys.argv[1]
security = SecurityExtensionManager.from_config(config, entity=name)
if name == "coordinator":
    agent = Coordinator(config, security)
else:
    agent = Worker(name, security=security)

uvicorn.run(agent.create_nlip_app(), host="127.0.0.1", port=config["entities"][name]["port"])
