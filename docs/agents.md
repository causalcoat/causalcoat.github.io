<!-- Generated from COAT-Learn/docs; edit the source, then run build.py. -->

# Use COAT with an agent

The optional skill helps an agent act on behalf of a data analyst. It is different from the models inside COAT: the user-facing agent chooses and runs a task, while the internal proposer and annotator perform defined steps of that task.

Install or load the public [coatlearn skill](<https://github.com/causalcoat/COAT-Learn/tree/main/skills/coatlearn/SKILL.md>) using your agent application's skill mechanism. The skill follows the `SKILL.md` format and does not depend on a particular vendor. Keep its references directory alongside it when installing.

Describe your question and identify the dataset you permit the agent to inspect. For example: “Find factors related to customer ratings in this CSV. Show me the proposed configuration before calling a model.”

The agent should first explain the method, data columns, model roles, where text will be sent and the planned output location. It should get permission before model execution. Local configuration inspection alone does not send requests.

After execution, the agent should distinguish measured attributes, statistical relationships, supplied causal assumptions and effect estimates. It should use saved results to explain the run, rather than changing parameters and launching additional calls without approval.

Without an agent, use the same Python interfaces and CLI directly. Analysis does not depend on an agent platform.
