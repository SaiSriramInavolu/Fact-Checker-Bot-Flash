# AI Fact-Checker Bot

## Description

The AI Fact-Checker Bot is a powerful tool designed to verify the accuracy of claims and questions by leveraging the power of large language models and web search. It systematically breaks down a claim, identifies underlying assumptions, and gathers evidence from the web to provide a comprehensive and well-supported final answer.

## Features

-   **LangChain Integration:** Utilizes LangChain for orchestrating LLM interactions.
-   **Prompt Chaining:** Implements a sophisticated prompt chaining mechanism for:
    -   Initial Response Generation
    -   Assumption Extraction
    -   Verification Loop (True/False/Uncertain)
    -   Evidence Gathering via Web Search
    -   Final Synthesis of Verified Information.
-   **Web Search Integration:** Integrates with DuckDuckGo for real-time information retrieval.
-   **User Interface:** A web-based interface built with Streamlit, featuring a clean design and fact-check history.
-   **API Key Management:** Securely handles API keys using environment variables.
-   **Logging:** Basic logging implemented for tracking key events and errors.
-   **Caching:** Simple caching for search queries to reduce redundant API calls.
-   **Claim Classification:** Categorizes claims into types like Factual, Opinion, Mixed, or Unverifiable.
-   **Persistent History:** Stores fact-check results in a local database for future access.

## How it Works

The bot operates in the following sequence:

1.  **Initial Response:** When a user enters a claim, the bot generates a preliminary answer, outlining the key points that require verification.
2.  **Assumption Extraction:** The bot identifies and extracts all the factual assumptions made in the initial response.
3.  **Verification Loop:** Each assumption is then independently verified.
    -   The bot first checks if the assumption is a known fact.
    -   If not, it performs a web search to find relevant evidence.
    -   Based on the search results, the assumption is evaluated as TRUE, FALSE, or UNCERTAIN.
4.  **Final Synthesis:** Finally, the bot synthesizes a comprehensive, fact-checked response based on the original claim, the initial response, and the verified assumptions.

## Project Structure

```
Fact-Checker-Bot-Flash/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
├── config/
│   ├── prompts.yaml
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── fact_checker.py
│   ├── prompt_chains.py
│   ├── search_tools.py
│   ├── utils.py
│   ├── database.py
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py
├── tests/
│   ├── test_fact_checker.py
│   └── test_search_tools.py
├── examples/
│   ├── example_queries.txt
│   └── demo_notebook.ipynb
└── data/...  
```

## Setup and Installation

1.  **Navigate to the project directory:**
    ```bash
    cd Fact-Checker-Bot-Flash
    ```

2.  **Create a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install the required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project by copying `.env.example`:
    ```bash
    copy .env.example .env   # Windows
    cp .env.example .env     # macOS/Linux
    ```
    Open the newly created `.env` file and replace the placeholder API key (`YOUR_GEMINI_API_KEY`) with your actual Google Gemini API key.

## Running the Application

Once the setup is complete and your virtual environment is activated, you can run the Streamlit application:

```bash
python main.py
```

This command will open the Streamlit application in your web browser.

## Running Tests

To run the unit tests, navigate to the project root directory and execute:

```bash
pytest tests/
```

## Screenshots
![alt text](.\data\ss1.png)

![alt text](.\data\ss1-2.png)

![alt text](.\data\ss1-3.png)

![alt text](.\data\ss2.png)


### Streamlit Interface

![alt text](data\sss.png)

## Future Improvements

-   **More Sophisticated Assumption Extraction:** The current assumption extraction uses a simple regex. This could be improved by using a more advanced NLP model or a dedicated LLM chain.
-   **Support for More Search Engines:** The bot currently only uses DuckDuckGo. It could be extended to support other search engines like Google, Bing, etc.