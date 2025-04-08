from models import invoke_claude_x, get_tag
from hybrid_search import hybrid_search


def intelligent_search(user_input, recent_history = "", last_attempt = False):

    prompt = f"""
    # Movie Search Criteria Extraction

    <USER_REQUEST>
    {user_input}
    </USER_REQUEST> 

    ## Available Keyword Categories
    ```
    "cast" : Full names of the main actors (e.g., Name and Surname)  
    "genres": One or more of: Comedy, Musical, Fantasy, War, Drama, History, Short, Thriller, Family, Romance, etc.  
    "directors" : Full names of the director(s)  
    "rated" : Official content rating, such as PG-13, G, OPEN, GP, Not Rated, TV-Y7, PASSED, or Approved  
    "type" : Indicates whether the title is a 'movie' or a 'series'
    "year" : Indicated the year when the movie was released
    ```

    ## Task

    When a user request is provided between <USER_REQUEST> tags, your task is to extract and format search criteria for a movie database query. You must provide:

    1. A refined version of the user request as a semantic search string between <SEMANTIC_SEARCH_TEXT> tags
    - This should capture the essence of the request in natural language
    - Maintain all relevant details while improving clarity

    2. A refined version of the user request as keyword text search terms between <KEYWORD_SEARCH_TEXT> tags
    - Include only specific searchable terms related to any of the Available Keyword Categories listed above
    - Be concise and focused on key identifiers

    3. A list of applicable keyword Categories between <KEYWORD_CATEGORIES> tags
    - Select only from the available Categories listed above
    - Include only Categories that are explicitly mentioned in the user request
    - Format as a comma-separated list with quotes (e.g., "cast", "genres")

    ## Important Restrictions
    - Do NOT provide any additional details about movies beyond what the user explicitly states
    - Do NOT guess or make assumptions about movie details
    - Only use information directly provided in the user request
    - DO NOT include keyword text search terms that are not related to keyword Categories between <KEYWORD_CATEGORIES>

    ## Example

    <USER_REQUEST>
    Hello, plese Give me a list of CRIME MOVIES ABOUT MAfiA faMILies With POWER STRUGGLES WITH LOYALTY RETAIN THEIR POWER AND LEGACY WITH MARLON brando... ok? ThankS!
    </USER_REQUEST>

    <SEMANTIC_SEARCH_TEXT>A powerful mafia family struggles with loyalty, power, and legacy, starring Marlon Brando.</SEMANTIC_SEARCH_TEXT>
    <KEYWORD_SEARCH_TEXT>mafia crime movie Marlon Brando</KEYWORD_SEARCH_TEXT>
    <KEYWORD_CATEGORIES>"cast", "genres", "type"</KEYWORD_CATEGORIES>
    """

    response = invoke_claude_x(prompt)

    print(f"Model Response:\n{response}")

    semantic_search_text = get_tag(response, "SEMANTIC_SEARCH_TEXT")
    keyword_search_text = get_tag(response, "KEYWORD_SEARCH_TEXT")
    keyword_categories = get_tag(response, "KEYWORD_CATEGORIES")

    return hybrid_search(semantic_search_text,keyword_search_text=keyword_search_text,keyword_search_categories=keyword_categories)


