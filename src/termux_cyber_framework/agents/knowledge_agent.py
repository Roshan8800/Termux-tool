import json
from typing import Optional, List, Dict, Any
from .file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel, AIProcessingPort

class KnowledgeAgent:
    """
    An agent that uses the Central AI Service to answer user questions about
    cybersecurity tools and concepts, with caching for repeated queries.
    """
    def __init__(self, ai_service: AIProcessingPort, file_manager: FileManagerAgent, logger: LoggerPort, tool_catalog: List[Dict[str, Any]], cache_path: str = "reports/knowledge_cache.json"):
        self.ai_service = ai_service
        self.file_manager = file_manager
        self.logger = logger
        self.tool_catalog = tool_catalog
        self.cache_path = cache_path
        self._load_tool_names()
        self._load_cache()

    def _load_tool_names(self):
        """Loads tool names from the catalog."""
        self.tool_names = [tool.get("name", "").lower() for tool in self.tool_catalog]

    def _load_cache(self):
        """Loads the query cache from a file."""
        self.query_cache = {}
        content = self.file_manager.read_file(self.cache_path)
        if content:
            try:
                self.query_cache = json.loads(content)
            except json.JSONDecodeError:
                self.logger.log(f"Knowledge cache file at {self.cache_path} is corrupt. Starting with an empty cache.", level=LogLevel.WARNING)

    def _save_cache(self):
        """Saves the query cache to a file."""
        content = json.dumps(self.query_cache, indent=2)
        self.file_manager.write_file(self.cache_path, content)

    def _detect_tool_in_question(self, question: str) -> Optional[str]:
        """Detects if a known tool is mentioned in the question."""
        for tool_name in self.tool_names:
            if tool_name in question.lower():
                return tool_name
        return None

    async def query(self, question: str) -> str:
        """
        Queries the Central AI Service or local cache with a user's question.
        """
        cache_key = question.strip().lower()
        if cache_key in self.query_cache:
            self.logger.log(f"Returning cached response for question: '{question}'", level=LogLevel.INFO)
            return self.query_cache[cache_key]

        self.logger.log(f"No cache hit. Querying Central AI Service for: '{question}'", level=LogLevel.INFO)

        detected_tool = self._detect_tool_in_question(question)

        try:
            answer = await self.ai_service.answer_knowledge_question(question, tool_context=detected_tool)
            self.query_cache[cache_key] = answer
            self._save_cache()
            return answer
        except Exception as e:
            self.logger.log(f"An error occurred while querying the knowledge base via Central AI Service: {e}", level=LogLevel.ERROR)
            return f"An error occurred while querying the knowledge base: {e}"
