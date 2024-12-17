import importlib
import argparse

AGENTS = ["ImageAgent", "CaptionAgent", "CatAgent", "QAAgent", "EvaluationAgent", "InstructionAgent", "CoIAgent"]
YOUR_API_KEY = "[YOUR_API_KEY]"

def import_agent(agent_name):
    try:
        module = importlib.import_module(f"agents.{agent_name}")
        return getattr(module, agent_name)
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error importing {agent_name}: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a specific agent with a given category.")
    parser.add_argument("--category", type=str, required=True, help="The category to be processed by the agent.")
    parser.add_argument("--agent_name", type=str, required=True, help="The name of the agent to use.", choices=AGENTS)
    args = parser.parse_args()

    agent_class = import_agent(args.agent_name)

    if agent_class is not None:
        agent_instance = agent_class(YOUR_API_KEY, args.category)
        agent_instance.run()
    else:
        print(f"{args.agent_name} could not be imported or instantiated.")
