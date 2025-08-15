import pytest
from src.search_tools import SearchTools
from unittest.mock import MagicMock, patch

@pytest.fixture
def search_tools_instance():
    return SearchTools(search_tool_name="duckduckgo")

def test_search_tools_initialization(search_tools_instance):
    assert search_tools_instance is not None
    assert search_tools_instance.search_tool_name == "duckduckgo"
    with pytest.raises(ValueError, match="Unsupported search tool: serpapi. Only 'duckduckgo' is supported in this configuration."):
        SearchTools(search_tool_name="serpapi")

@patch('duckduckgo_search.DDGS.text')
def test_duckduckgo_search(mock_ddgs_text, search_tools_instance):
    mock_ddgs_text.return_value = [
        {"title": "Result 1", "href": "http://link1.com", "body": "Snippet 1"},
        {"title": "Result 2", "href": "http://link2.com", "body": "Snippet 2"}
    ]
    query = "test query"
    results = search_tools_instance.search(query, num_results=2)

    mock_ddgs_text.assert_called_once_with(keywords=query, max_results=2)
    assert len(results) == 2
    assert results[0]["title"] == "Result 1"
    assert results[1]["href"] == "http://link2.com"

def test_process_results():
    search_results = [
        {"title": "Title A", "href": "http://linkA.com", "body": "Snippet A"},
        {"title": "Title B", "href": "http://linkB.com", "body": "Snippet B"}
    ]
    processed_string = SearchTools().process_results(search_results)
    assert "Result 1:" in processed_string
    assert "Title: Title A" in processed_string
    assert "Link: http://linkA.com" in processed_string
    assert "Snippet: Snippet A" in processed_string
    assert "Result 2:" in processed_string
    assert "Title: Title B" in processed_string
    assert "Link: http://linkB.com" in processed_string
    assert "Snippet: Snippet B" in processed_string

@patch('src.search_tools.logging') # Mock logging to prevent actual log output during test
@patch('src.search_tools.ChatGoogleGenerativeAI') # Mock LLM for summarization
def test_summarize_search_results(mock_llm, mock_logging):
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    mock_llm_instance.invoke.return_value.content = "This is a summarized result."

    search_tools_instance = SearchTools()
    search_results_text = "Some raw search results text here."
    summary = search_tools_instance.summarize_search_results(search_results_text)

    assert summary == "This is a summarized result."
    mock_llm_instance.invoke.assert_called_once()
    mock_logging.info.assert_not_called() # Ensure no info logs for successful summary

def test_search_cache(search_tools_instance):
    with patch('src.search_tools.SearchTools._duckduckgo_search') as mock_duckduckgo_search:
        mock_duckduckgo_search.return_value = [{"title": "Cached Result"}]
        
        # First call, should hit actual search
        results1 = search_tools_instance.search("test query", num_results=1)
        mock_duckduckgo_search.assert_called_once_with("test query", 1)
        assert results1 == [{"title": "Cached Result"}]

        mock_duckduckgo_search.reset_mock() # Reset mock call count

        # Second call with same query, should hit cache
        results2 = search_tools_instance.search("test query", num_results=1)
        mock_duckduckgo_search.assert_not_called() # Should not call actual search
        assert results2 == [{"title": "Cached Result"}]

        # Third call with different query, should hit actual search
        results3 = search_tools_instance.search("another query", num_results=1)
        mock_duckduckgo_search.assert_called_once_with("another query", 1)
        assert results3 == [{"title": "Cached Result"}]
