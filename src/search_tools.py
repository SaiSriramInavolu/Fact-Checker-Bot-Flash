from duckduckgo_search import DDGS
from typing import List, Dict
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import settings
import logging

class SearchTools:
    def __init__(self, search_tool_name: str = "duckduckgo"):
        self.search_tool_name = search_tool_name
        if self.search_tool_name != "duckduckgo":
            raise ValueError(f"Unsupported search tool: {self.search_tool_name}. Only 'duckduckgo' is supported in this configuration.")
        self.llm_for_summary = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=0.1,
            max_tokens=512,
            google_api_key=settings.GEMINI_API_KEY
        )
        self._cache = {}

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Performs a web search using the specified search tool."""
        cache_key = f"{query}_{num_results}"
        if cache_key in self._cache:
            logging.info(f"Returning search results from cache for query: {query}")
            return self._cache[cache_key]

        if self.search_tool_name == "duckduckgo":
            results = self._duckduckgo_search(query, num_results)
            self._cache[cache_key] = results
            return results
        else:
            raise ValueError(f"Unsupported search tool: {self.search_tool_name}")

    def _duckduckgo_search(self, query: str, num_results: int) -> List[Dict]:
        """Performs a DuckDuckGo search."""
        results = []
        try:
            ddgs = DDGS()
            for r in ddgs.text(keywords=query, max_results=num_results):
                results.append(r)
        except Exception as e:
            logging.error(f"Error during DuckDuckGo search: {e}")
        return results

    def process_results(self, search_results: List[Dict]) -> str:
        """Processes search results into a readable string format."""
        processed_string = ""
        for i, result in enumerate(search_results):
            processed_string += f"Result {i+1}:\n"
            processed_string += f"Title: {result.get('title', 'N/A')}\n"
            processed_string += f"Link: {result.get('href', 'N/A')}\n"
            processed_string += f"Snippet: {result.get('body', 'N/A')}\n\n"
        return processed_string

    def summarize_search_results(self, search_results_text: str) -> str:
        """Summarizes the raw text of search results using the LLM."""
        if not search_results_text.strip():
            return "No relevant search results found to summarize."

        prompt_template = ChatPromptTemplate.from_template(
            "Summarize the following search results concisely, focusing only on information relevant to fact-checking. Extract key facts and avoid opinions or irrelevant details:\n\n{search_results}"
        )
        chain = prompt_template | self.llm_for_summary
        summary = chain.invoke({"search_results": search_results_text})
        return summary.content
