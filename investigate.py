import json
import os
from parse_data import get_unclaimed_items, load_items, save_result


## Build your prompt based on the description the user provides
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = (
        "You are a campus lost-and-found assistant. Your job is to find possible "
        "matches between an item a user lost and items in the lost-and-found database.\n\n"
        "RULES:\n"
        "1. You must ONLY use the items provided in the available_items JSON list. "
        "Do not invent items or IDs.\n"
        "2. Not all details of an item must match to be a possible match. "
        "Partial or fuzzy matches are allowed (e.g., color, category, location, date).\n"
        "3. You must return ONLY valid JSON, with exactly this structure:\n"
        '   { "matches": ["ITEM_ID"], "confidence": "LOW" }\n'
        "4. 'matches' contains ALL possible matching item IDs (a list of strings).\n"
        "5. 'confidence' must be exactly one of: LOW, MEDIUM, HIGH.\n"
        "6. If there is no match, return an empty list for matches.\n"
        "7. Do not include any explanation, markdown, or text outside the JSON."
    )

    user_prompt = (
        f'The user lost the following item:\n"{description}"\n\n'
        f"Here are the available unclaimed items in the lost-and-found database "
        f"(JSON):\n{json.dumps(available_items, indent=2)}\n\n"
        "Return only the JSON result as specified."
    )

    return system_prompt, user_prompt  
    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    try:
        # If the dashscope SDK is available, use it (Qwen via DashScope).
        import dashscope
        response = dashscope.Generation.call(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            result_format="message",
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise RuntimeError(f"Qwen API error: {response.code} - {response.message}")
    except ImportError:
        # Fallback: use OpenAI-compatible endpoint (e.g., DashScope compatible mode)
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content


## Logic to parse the response from Qwen and return the result.
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    text = response_text.strip()
    # Strip markdown code fences if the model added them
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first JSON object found in the text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise

## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if not isinstance(result["confidence"], str):
        return False
    if result["confidence"].upper() not in ("LOW", "MEDIUM", "HIGH"):
        return False
    for m in result["matches"]:
        if not isinstance(m, str):
            return False

    valid_ids = {str(item.get("id")) for item in available_items}
    for m in result["matches"]:
        if m not in valid_ids:
            return False

    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    items_by_id = {str(item.get("id")): item for item in available_items}

    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence'].upper()}")
    print()

    if not result["matches"]:
        print("Possible matches: None")
        print("No matching items were found in the lost-and-found database.")
        return

    print("Possible matches:")
    for match_id in result["matches"]:
        item = items_by_id.get(match_id, {})
        print()
        print(f"ID: {match_id}")
        print(f"Item: {item.get('name', item.get('item', 'N/A'))}")
        print(f"Color: {item.get('color', 'N/A')}")
        print(f"Location: {item.get('location', 'N/A')}")
        print(f"Date found: {item.get('date_found', item.get('date', 'N/A'))}")

    

## Control center for the entire program.
def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()

    description = input("Describe the item you lost: ")

    print("\nSearching for possible matches...")

    items = load_items("lost_and_found.json")
    available_items = get_unclaimed_items(items)

    system_prompt, user_prompt = build_prompt(description, available_items)
    response_text = ask_qwen(system_prompt, user_prompt)
    result = parse_response(response_text)

    if not validate_result(result, available_items):
        print("\nThe model returned an invalid result. Please try again.")
        return

    display_matches(result, available_items)

    save_result(result, "output/match_result.json")
    print("\nResult saved to output/match_result.json")


if __name__ == "__main__":
    main()