BROWSER_TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate to a URL in the browser",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL to navigate to (must include https://)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_page_content",
        "description": "Get the text content and links from the current page",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "search_google",
        "description": "Search Google for a query and return top results with titles, URLs, and snippets",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to send to Google"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "click_link",
        "description": "Click on a link by its text or navigate directly to its URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "link_text": {
                    "type": "string",
                    "description": "Visible text of the link to click"
                },
                "url": {
                    "type": "string",
                    "description": "Direct URL to navigate to (preferred over link_text when available)"
                }
            }
        }
    },
    {
        "name": "extract_data",
        "description": "Extract specific data from the current page based on a description of what you need",
        "input_schema": {
            "type": "object",
            "properties": {
                "data_description": {
                    "type": "string",
                    "description": "What data to extract, e.g. 'all product prices' or 'the main article text' or 'top headlines'"
                }
            },
            "required": ["data_description"]
        }
    },
    {
        "name": "finish",
        "description": "Complete the task and return the final result to the user. Call this when you have gathered all necessary information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The final answer or summary of extracted data, written clearly for the user"
                },
                "data": {
                    "type": "object",
                    "description": "Optional structured data if applicable (e.g. list of prices, articles, etc.)"
                }
            },
            "required": ["result"]
        }
    }
]
