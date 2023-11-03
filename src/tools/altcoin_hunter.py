import requests
from typing import Any, List, Union
from steamship.agents.schema import AgentContext, Tool
from steamship import Block
from steamship.utils.repl import ToolREPL
from dotenv import load_dotenv, find_dotenv
import os
from utils.filter_data import filter_data

# Load environment variables from .env file
config = find_dotenv()
load_dotenv(config)
dext_tools_key = os.getenv('DEXT_TOOLS_KEY')

# Define custom headers for API requests
headers = {
    'X-API-Key': dext_tools_key
}

class AltCoinHunter(Tool):
    """
    Custom Steamship tool for searching under valued alt coin using dexTools and geckoterminal API.
    """
    name: str = "AltCoinFinder"
    human_description: str = "Return top undervalued altcoin"
    agent_description: str = """
    The UndervaluedAltSeeker is a specialized tool designed to harness the power of both dexTools and geckoterminal APIs. It dynamically scans, analyzes, and identifies potential undervalued alt coins in the cryptocurrency market. By leveraging real-time data and advanced analytics, this tool provides users with insights into coins that may be poised for growth, offering a strategic edge in the ever-evolving world of digital assets. Ideal for both novice and seasoned crypto enthusiasts, the UndervaluedAltSeeker is your compass in the vast sea of alt coins, pointing you towards potential hidden gems.
    """
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Any]:
        """
        Execute the Security check using the GoPlus API.
        """
        output = []
        response = self.get_token_info()
        for block in tool_input:
            if block.is_text():
                output.append(Block(text=str(response)))
        return output

    # Define a method to fetch base token addresses from geckoterminal API
    def get_base_token_addresses(self):
        base_url = "https://api.geckoterminal.com/api/v2/networks/eth/pools?include=%20base_token"
        response = requests.get(base_url)
        
        if response.status_code != 200:
            return "Error fetching data:"

        data = response.json()["data"]
        base_token_addresses = []
        
        for pool in data:  
            base_token_id = pool["relationships"]["base_token"]["data"]["id"]
            for included in response.json()["included"]:
                if included["id"] == base_token_id:
                    base_token_addresses.append(included["attributes"]["address"])
        return base_token_addresses

    # Define a method to fetch token rate from dextools API
    def get_token_info(self):
        base_url = "https://api.dextools.io/v1/token"
        params = {
            "chain": 'ether',
        }
        token_addresses = self.get_base_token_addresses()
        respons_ouptut = []
        for token in token_addresses:
            params["address"] = token
            response = requests.get(base_url, headers=headers, params=params)
            data = filter_data(response.json())
            respons_ouptut.append(data)
            #Check the length of token_string
            if len(respons_ouptut) >= 15:
                break
        return respons_ouptut

# Main execution
if __name__ == "__main__":
    # Instantiate the tool and run it using the ToolREPL utility
    tool = AltCoinHunter()
    ToolREPL(tool).run()
