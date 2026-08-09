from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers.json import JsonOutputParser
from logassistant.config.prompts import SECURITY_AGENT_SYSTEM_PROMPT, SECURITY_AGENT_USER_PROMPT
from logassistant.models.threat_report import ThreatReport
from logassistant.agent_tools import get_ip_activity_history, get_mitre_knowledge_base

class SecurityAgentService:
    def __init__(self):
        self.tools_map = {
            "get_ip_activity_history": get_ip_activity_history,
            "get_mitre_knowledge_base": get_mitre_knowledge_base
        }
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.0)
        self.llm_with_tools = self.llm.bind_tools(list(self.tools_map.values()))
        self.output_parser = JsonOutputParser(pydantic_object=ThreatReport)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", SECURITY_AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", SECURITY_AGENT_USER_PROMPT),
        ])

    async def analyze_log_entry(self, attack_type: str, ip: str, log_entry: str) -> dict[str, any]:

        format_instructions = self.output_parser.get_format_instructions()

        messages = self.prompt_template.format_messages(
            attack_type=attack_type,
            ip=ip,
            log_entry=log_entry,
            format_instructions=format_instructions,
            chat_history=[]
        )

        for _ in range(5):
            response = await self.llm_with_tools.ainvoke(messages)
            messages.append(response)

            if not response.tool_calls:
                raw_content = response.content
                if isinstance(raw_content, list):
                    raw_text = "".join([block.get("text", "") for block in raw_content if isinstance(block, dict)])
                else:
                    raw_text = str(raw_content)

                try:
                    clean_json_str = raw_text.replace("```json", "").replace("```", "").strip()
                    parsed_response = self.output_parser.parse(clean_json_str)
                    return parsed_response
                except Exception as parse_error:
                    print(f"parsing failed: {parse_error}")
                    return {"raw_text": raw_text, "error": "Output parsing failed"}


            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                tool_function = self.tools_map[tool_name]
                tool_result = tool_function.invoke(tool_args)
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
        return {"error": "Failed to generate a valid response after multiple attempts."}