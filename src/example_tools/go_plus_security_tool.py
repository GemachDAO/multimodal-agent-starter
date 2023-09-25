from typing import Any, List, Union
from steamship.agents.schema import AgentContext, Tool
from steamship import Block
from steamship.utils.repl import ToolREPL
import requests
import os
from dotenv import load_dotenv, find_dotenv
config = find_dotenv()
load_dotenv(config)
class GoPlusSecurityTool(Tool):
    """
    Custom Steamship tool for performing various Security checks on web3 using GoPlus API.
    """
    name: str = "GoPlusSecurityTool"
    human_description: str = "Perform various Security checks on web3 using GoPlus API"
    agent_description: str = """
    Used to perform real-time, dynamic, and automated security checks on web3 infrastructure including Token Security, NFT Security, Malicious Address, Approval Security, dApp Security Info, and Signature Data Decode APIs.
    """
  
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Any]:
        """
        Execute the Security check using the GoPlus API.
        """
        output = []
        for block in tool_input:
            if block.is_text():
                # get the text from the block ans split it by space as request parameters
                params = block.text.split(" ")
                # create a json object with the parameters with keys command wich is the first element in the params and arguments which is the rest of the params
                json = {"command": params[0], "arguments": params[1:]}
                data=None
                # call the api with the json data and set autorization header to TOKEN from .env file using os.getenv
                response = requests.post("https://gemach-one.vercel.app/api", json=json, headers={"Authorization":os.getenv("TOKEN")})
                # if the response is ok then set the data to the response json
                if response.ok:
                    data = response.json()
                    print(data)
                    # append a block with the data as string to the output
                    output.append(Block(text=str(data)))
                else:
                    # append a block with the message saying to the agent that the request failed and it should tell the user it is experiencing high traffic
                    output.append(Block(data="Request failed. Tell the user you are experiencing high traffic"))
        return output
                

if __name__ == "__main__":
    tool = GoPlusSecurityTool()
    ToolREPL(tool).run()