import subprocess, re
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool 
from typing import List, Any, Optional, Dict
from dotenv import load_dotenv
load_dotenv()

SCRIPT_DIR = "/middleware_support_agent/server_maintenance/server_scripts/"
model_name = 'gemini-2.0-flash'

######################################################
# Function for running the server maintenance script #
######################################################

def execute_shell_command(command: str) -> str:
    """
    Executes a shell command and returns its stdout or stderr.
    This function should be used with caution as it runs arbitrary commands.
    """
    print(f"\n[Executing Command]: {command}") 
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True 
        )
        print(f"[Command Output]:\n{result.stdout.strip()}")
        return f"Command executed successfully. Output:\n{result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with exit code {e.returncode}.\nStderr:\n{e.stderr.strip()}"
        print(f"[Command Error]: {error_message}")
        return error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(f"[Execution Error]: {error_message}")
        return error_message

######################
# Function as a tool #
######################

command_execution = FunctionTool(func=execute_shell_command)

########################
# Tool to read scripts #
########################

def read_script_content(script_name: str) -> str:
    """
    Reads the content of a specified server script from the SCRIPT_DIR.
    Returns the script's content or an error message if not found/readable.
    """
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        return f"Error: Script '{script_name}' not found at {script_path}."
    if not os.path.isfile(script_path):
        return f"Error: '{script_name}' is not a file at {script_path}."

    try:
        with open(script_path, 'r') as f:
            content = f.read()
        return f"Content of {script_name}:\n```bash\n{content}\n```"
    except Exception as e:
        return f"Error reading script '{script_name}': {e}"

read_script_content_tool = FunctionTool(func=read_script_content)

########################
# Tool to list scripts #
########################

def list_available_scripts() -> str:
    """
    Lists all executable shell scripts in the SCRIPT_DIR.
    """
    try:
        scripts = [f for f in os.listdir(SCRIPT_DIR) if f.endswith('.sh') and os.path.isfile(os.path.join(SCRIPT_DIR, f))]
        if not scripts:
            return f"No .sh scripts found in {SCRIPT_DIR}."
        return "Available scripts:\n" + "\n".join(scripts)
    except Exception as e:
        return f"Error listing scripts in {SCRIPT_DIR}: {e}"

list_scripts_tool = FunctionTool(func=list_available_scripts)


###########################################################################
# LLMAgent for generating commands to perform server maintenance activity #
###########################################################################

cmd_generator_agent = LlmAgent(
    model=model_name,
    name='cmd_generator_agent',
    instruction = f"""You are an assistant that helps manage server operations. Below are the descriptions of three scripts:

    startserver.sh: Starts a specific server (web, db, or app) based on the argument provided.

    stopserver.sh: Stops a specific server (web, db, or app) based on the argument provided.

    healthcheck.sh: Checks the health/status of a specific server (web, db, or app) based on the argument provided.

    Your task is to determine the correct sequence of scripts to execute based on the user's request. For example:

    To restart a server, the sequence would be: stopserver.sh → startserver.sh → healthcheck.sh.

    To check the status of a server, the sequence would be: healthcheck.sh.

    Provide the sequence of scripts to execute as output, along with the appropriate arguments.

    Name of the servers: app , web, db

    And the order for full restart will be

    stop web -> app -> db

    start db -> app -> web

    script path= bash {SCRIPT_DIR}

    Example 1:
    User Request: "Restart the web server and check its health."
    AI Output:
    ["bash {SCRIPT_DIR}stopserver.sh web",
    "bash {SCRIPT_DIR}startserver.sh web",
    "bash {SCRIPT_DIR}healthcheck.sh web"]

    Example 2:
    User Request: "Check the status of the database server."
    AI Output:
    ["bash {SCRIPT_DIR}healthcheck.sh db"]

    Example 3:
    User Request: "Stop the application server."
    AI Output:
    ["bash {SCRIPT_DIR}stopserver.sh app"]

    Example 4:
    User Request: "Start the web server and ensure it's running."
    AI Output:
    ["bash {SCRIPT_DIR}startserver.sh web",
    "bash {SCRIPT_DIR}healthcheck.sh web"]
        """,
    output_key = "steps",
    tools=[
        read_script_content_tool,
        list_scripts_tool
    ]
)

###################
# Agent as a tool #
###################

cmd_generator_agent_tool = AgentTool(cmd_generator_agent)

###########################################################################
# Function callback, "before_tool_callback" for cross check the generated #
# commands satisfy gaurdrails to execute or not                           #
###########################################################################

def security_guardrail_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, str]]: # Return type should be Dict[str, str] if blocking
    """
    A callback to intercept tool calls and prevent execution of dangerous commands.
    Returns a dict to block the tool call, or None to allow it.
    """

    agent_name = tool_context.agent_name
    tool_name = tool.name
    print(f"[Callback] Before tool call for tool '{tool_name}' in agent '{agent_name}'")
    print(f"[Callback] Original args: {args}")
    if tool_name == command_execution.name:
        command_to_execute = args.get("command", "").lower()
        normal_patterns = [
            r"bash /middleware_support_agent/server_maintenance/server_scripts/healthcheck.sh web",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/healthcheck.sh app",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/healthcheck.sh db",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/stopserver.sh web",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/stopserver.sh app",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/stopserver.sh db",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/startserver.sh web",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/startserver.sh app",
            r"bash /middleware_support_agent/server_maintenance/server_scripts/startserver.sh db"
        ]
        is_allowed = False
        for pattern in normal_patterns:
            if re.fullmatch(pattern, command_to_execute):
                is_allowed = True
                break
        if is_allowed:
            print(f"[Callback] Command '{command_to_execute}' is whitelisted. Allowing execution.")
            return None
        else:
            print(f"\n[SECURITY ALERT] Blocked unapproved command: '{command_to_execute}'")
            return {
                "result": f"SECURITY BLOCKED: Attempted to execute an unapproved command: '{command_to_execute}'. This action has been prevented by security policies."
            }
    return None
    
##################################################
# Root LLMAgent for  server maintenance activity #
##################################################

root_agent = LlmAgent(
    model=model_name,
    name='middleware_support_agent',
    description="""
      You are an agent, who is responsible for middleware server maintenance activity.
""",
    instruction="""
      You will process user requests for server maintenance.

      **Step 1: Generate Command Sequence.**
      First, use the `cmd_generator_agent` tool to get the list of shell commands required to fulfill the user's request.
      Pass the *entire original user request* to the `cmd_generator_agent`.

      **Step 2: Execute Commands Iteratively with Analysis.**
      Once you receive the list of commands (from the `steps` output of `cmd_generator_agent`), you will iterate through each command.
      For each command:
      a. Use the `execute_shell_command` tool to run the command.
      b. **Crucially**, analyze the output from `execute_shell_command`. If the command indicates a failure (e.g., "Command failed", "Error"), inform the user and ask if they want to proceed with the remaining steps or if they want to stop and troubleshoot.
      c. If the command succeeds, inform the user about the success and the output, then proceed to the next command.
      d. If all commands complete successfully, confirm the maintenance activity is done.

      **Step 3: Handle Out of Context Requests.**
      If the user input is out of the context of server maintenance (e.g., "Tell me a joke", "What is the capital of France?"), regret for not being able to solve it and state that you are designed for server maintenance.

      Your responses should be clear, informative, and guide the user through the process, especially if an issue occurs.

      you can also get the name of the servers from cmd generator agent tool
""",
    tools=[
        cmd_generator_agent_tool,
        command_execution
    ],
    before_tool_callback=security_guardrail_callback
)
