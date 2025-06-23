# middleware_support_agent

Middleware Support Agent used to automate server maintenance activity , which simplifies the complex scripting of maintenance activity into ai agent. Existing scripts will be handled by ai agent.

Use Case:
In middleware, there are scripts to do task such as healthcheck, startserver, stopserver etc,. For maintenance activity, these scripts need to be executed then and there based on needs, it won't be same in pattern eg: we may need to depend on other server status before taking action on the current server. Writing an orchestrator script is doable, but complex in nature considering the pre-requisites to proceed before each steps. AI agent will remove this complexity by taking user prompt as input and serilaize the script execution according to it. 

Keys:

1. Callback as gaurdrail prevent execution of unauthorized commands.
2. Multiagent, one for analyzing and one for generating the command is used for seamless execution.

Architecture Diagram:
![plot](./arch_diagram.png)
