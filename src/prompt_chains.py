from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
from src.utils import load_prompts
from config.settings import settings

class PromptChains:
    def __init__(self, model_name: str = settings.LLM_MODEL, temperature: float = settings.TEMPERATURE, max_tokens: int = settings.MAX_TOKENS):
        self.prompts = load_prompts("D:\\AI-Fact-Checker-Bot\\gemini-fact-checker\\config\\prompts.yaml")
        self.llm = self._initialize_llm(model_name, temperature, max_tokens)

    def _initialize_llm(self, model_name: str, temperature: float, max_tokens: int):
        # Only Gemini is supported
        if "gemini" in model_name:
            return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, max_tokens=max_tokens, google_api_key=settings.GEMINI_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM model: {model_name}. Only Gemini models are supported in this configuration.")

    def claim_classification_chain(self, claim: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["claim_classification_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({"claim": claim})
        return response.content.strip() # Strip whitespace to get clean category

    def initial_response_chain(self, claim: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["initial_response_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({"claim": claim})
        return response.content

    def assumption_extraction_chain(self, initial_response: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["assumption_extraction_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({"initial_response": initial_response})
        return response.content

    def verification_loop_chain(self, assumption: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["verification_loop_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({"assumption": assumption})
        return response.content

    def evidence_gathering_chain(self, assumption: str, search_results: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["evidence_gathering_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({"assumption": assumption, "search_results": search_results})
        return response.content

    def final_synthesis_chain(self, claim: str, initial_response: str, assumptions_verdicts: str, gathered_evidence: str) -> str:
        prompt = ChatPromptTemplate.from_template(self.prompts["final_synthesis_prompt"])
        chain = prompt | self.llm
        response = chain.invoke({
            "claim": claim,
            "initial_response": initial_response,
            "assumptions_verdicts": assumptions_verdicts,
            "gathered_evidence": gathered_evidence
        })
        return response.content