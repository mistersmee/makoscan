import os
import google.generativeai as genai

def analyze_with_llm(txt_file):
    """
    Send the translated text file to the LLM for analysis.

    Args:
        txt_file (str): Path to the text file to analyze

    Returns:
        str: The analysis result text
    """
    if not os.path.exists(txt_file):
        return "No translated text file found."

    # Configure the Gemini API with the API key from environment variable
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except KeyError:
        return "Error: GEMINI_API_KEY environment variable not set."

    try:
        with open(txt_file, "r") as f:
            text_data = f.read()

        model = genai.GenerativeModel('gemini-2.0-flash')

        # Define a structured prompt
        custom_prompt = (
            "Analyze the following network traffic log and provide insights into potential threats, "
            "malicious patterns, or suspicious activity. Summarize key observations and include relevant "
            "protocol details. Provide a conclusion on whether the traffic seems benign or risky:\n\n"
            f"{text_data}"
        )

        response = model.generate_content(custom_prompt)
        return response.text
    except Exception as e:
        return f"Error during analysis: {e}"
