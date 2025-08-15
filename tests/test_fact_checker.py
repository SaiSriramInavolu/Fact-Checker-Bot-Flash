import pytest
from src.fact_checker import FactChecker
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def mock_settings():
    with patch('config.settings.settings') as mock_settings:
        mock_settings.LLM_MODEL = "mock-gemini-model"
        mock_settings.SEARCH_TOOL = "mock-search"
        mock_settings.GEMINI_API_KEY = "mock-gemini-key"
        yield mock_settings

@pytest.fixture
def fact_checker_instance():
    return FactChecker(model_name="mock-gemini-model", search_tool_name="mock-search")

def test_fact_checker_initialization(fact_checker_instance):
    assert fact_checker_instance is not None
    assert fact_checker_instance.prompt_chains is not None
    assert fact_checker_instance.search_tools is not None

@patch('src.prompt_chains.PromptChains.claim_classification_chain')
@patch('src.prompt_chains.PromptChains.initial_response_chain')
@patch('src.prompt_chains.PromptChains.assumption_extraction_chain')
@patch('src.prompt_chains.PromptChains.verification_loop_chain')
@patch('src.search_tools.SearchTools.search')
@patch('src.search_tools.SearchTools.process_results')
@patch('src.search_tools.SearchTools.summarize_search_results')
@patch('src.prompt_chains.PromptChains.evidence_gathering_chain')
@patch('src.prompt_chains.PromptChains.final_synthesis_chain')
@patch('src.database.save_fact_check') # Mock database save
def test_process_claim(mock_save_fact_check, mock_final_synthesis, mock_evidence_gathering, mock_summarize_search_results, mock_process_results, mock_search,
                       mock_verification_loop, mock_assumption_extraction, mock_initial_response, mock_claim_classification,
                       fact_checker_instance):
    mock_claim_classification.return_value = "Factual"
    mock_initial_response.return_value = "Initial response to the claim."
    mock_assumption_extraction.return_value = "Assumption 1\nAssumption 2"
    mock_verification_loop.side_effect = ["True", "Uncertain"]
    mock_search.return_value = [{"title": "Test Result", "href": "http://example.com", "body": "Snippet"}]
    mock_process_results.return_value = "Processed search results."
    mock_summarize_search_results.return_value = "Summarized search results."
    mock_evidence_gathering.return_value = "Evidence gathered."
    mock_final_synthesis.return_value = "Final synthesized answer."

    claim = "This is a test claim."
    result = fact_checker_instance.process_claim(claim)

    mock_claim_classification.assert_called_once_with(claim)
    mock_initial_response.assert_called_once_with(claim)
    mock_assumption_extraction.assert_called_once_with("Initial response to the claim.")
    assert mock_verification_loop.call_count == 2
    assert mock_search.call_count == 2
    assert mock_process_results.call_count == 2
    assert mock_summarize_search_results.call_count == 2
    assert mock_evidence_gathering.call_count == 2
    mock_final_synthesis.assert_called_once()
    mock_save_fact_check.assert_called_once()

    assert result["claim"] == claim
    assert result["claim_type"] == "Factual"
    assert result["final_answer"] == "Final synthesized answer."
    assert "Initial response to the claim." in result["initial_response"]
    assert "Assumption 1" in result["assumptions"]
    assert "Assumption 2" in result["assumptions"]
