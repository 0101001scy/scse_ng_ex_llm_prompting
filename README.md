Rules for the Model:
- The model must use only the given JSON file
- Not all the details of an item must match to be a possible match.
- Only JSON must be returned, with exactly the following strucutre:
{
        "matches": ["ITEM_ID"],
        "confidence": "LOW"
}

- "matches" contains all the possible matches
- "confidence" measures how confident the model is about the matches. 
- It must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no match the the model must return the an empty list


SETUP AND TESTING:
- Create and activate a virtual environment
- Install requirements using: uv pip install -r requirements.txt
    -- The above command will install ollama in this virtual environment

