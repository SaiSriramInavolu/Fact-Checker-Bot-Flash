from src.prompt_chains import PromptChains
from src.search_tools import SearchTools
from typing import List, Dict
import logging
import re
from src.database import save_fact_check

class FactChecker:
    def __init__(self, model_name: str = "gemini-pro", search_tool_name: str = "duckduckgo"):
        self.prompt_chains = PromptChains(model_name=model_name)
        self.search_tools = SearchTools(search_tool_name=search_tool_name)

    def process_claim(self, claim: str) -> Dict:
        """Processes a claim through the fact-checking pipeline."""
        logging.info(f"Processing claim: {claim}")

        claim_type = self.prompt_chains.claim_classification_chain(claim)
        logging.info(f"Claim Type: {claim_type}")

        initial_response = self.prompt_chains.initial_response_chain(claim)
        logging.info(f"Initial Response: {initial_response}")

        if initial_response.strip().lower() in ["true", "false"]:
            logging.info("Initial response is a simple verdict. Skipping assumption extraction, verification, and evidence gathering.")
            assumptions = []
            assumptions_verdicts = ["No assumptions extracted for simple verdict."]
            gathered_evidence_list = ["No evidence gathered for simple verdict."]
            final_answer = self.prompt_chains.final_synthesis_chain(
                claim,
                initial_response,
                "No assumptions to verify for simple verdict.",
                "No evidence gathered for simple verdict."
            )
        else:
            assumptions_raw = self.prompt_chains.assumption_extraction_chain(initial_response)
            
            if assumptions_raw.strip().upper() == "NONE":
                assumptions = []
                logging.info("No assumptions extracted.")
            else:
                assumptions = re.findall(r'^- (.+)$', assumptions_raw, re.MULTILINE)
                assumptions = [a.strip() for a in assumptions if a.strip()]
                logging.info(f"Extracted Assumptions: {assumptions}")

            assumptions_verdicts = []
            gathered_evidence_list = []

            if assumptions:
                for assumption in assumptions:
                    verdict = self.prompt_chains.verification_loop_chain(assumption)
                    logging.info(f"Assumption: {assumption}\nVerdict: {verdict}")
                    assumptions_verdicts.append(f"Assumption: {assumption} | Verdict: {verdict}")

                    if "uncertain" in verdict.lower() or "false" in verdict.lower() or "true" in verdict.lower():
                        search_query = f"{assumption} fact check"
                        search_results = self.search_tools.search(search_query, num_results=10)
                        processed_search_results = self.search_tools.process_results(search_results)
                        
                        summarized_evidence_text = self.search_tools.summarize_search_results(processed_search_results)
                        
                        evidence = self.prompt_chains.evidence_gathering_chain(assumption, summarized_evidence_text)
                        logging.info(f"Evidence for '{assumption}': {evidence}")
                        gathered_evidence_list.append(f"Assumption: {assumption}\nEvidence: {evidence}")
            else:
                logging.info("Skipping assumption verification and evidence gathering as no assumptions were extracted.")

            final_answer = self.prompt_chains.final_synthesis_chain(
                claim,
                initial_response,
                "\n".join(assumptions_verdicts) if assumptions_verdicts else "No assumptions to verify.",
                "\n".join(gathered_evidence_list) if gathered_evidence_list else "No evidence gathered."
            )
        
        logging.info(f"Final Answer: {final_answer}")

        result = {
            "claim": claim,
            "claim_type": claim_type,
            "initial_response": initial_response,
            "assumptions": assumptions,
            "assumptions_verdicts": assumptions_verdicts,
            "gathered_evidence": gathered_evidence_list,
            "final_answer": final_answer
        }
        
        save_fact_check(result)

        return result