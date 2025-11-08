# ---------------------------------------------------------
# Q1. Gemini Integration and Intelligent Summarization
# ---------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# -------------------------------
# STEP 1: Configure Gemini
# -------------------------------
# Make sure you've set your Gemini API key:
# Either in environment variable:
#    setx GOOGLE_API_KEY "your_api_key"
# Or directly here:
genai.configure(api_key="AIzaSyAoQood962YeAVGo1IgOj7gnkNjncYXwUw")  # <-- replace with your key

model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------------
# STEP 2: Choose and fetch live webpage
# -------------------------------
url = "https://en.wikipedia.org/wiki/Artificial_intelligence"  # can change to BBC/CNN
print(f"Fetching webpage: {url}")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers)
response.raise_for_status()

# -------------------------------
# STEP 3: Clean HTML
# -------------------------------
soup = BeautifulSoup(response.text, "html.parser")

# remove scripts, navbars, footers, etc.
for tag in soup(["script", "style", "header", "footer", "nav", "aside", "noscript"]):
    tag.decompose()

# extract main readable text
clean_text = " ".join(soup.stripped_strings)

# limit length to prevent hitting token limit
clean_text = clean_text[:15000]

print(f"\n✅ Extracted {len(clean_text)} characters of cleaned text.\n")

# -------------------------------
# STEP 4: Create a smart prompt
# -------------------------------
prompt = f"""
You are an expert technology analyst with deep knowledge of artificial intelligence, ethics, and industry transformation.

Analyze the following webpage content carefully.

Summarize the key ideas and developments discussed — use no more than 5 bullet points written in a clear, factual, and objective tone.

Focus especially on the technological progress, real-world applications, and ethical or societal implications mentioned in the text.

After the summary, provide one insight line starting with ‘Insight:’ that captures what this information reveals about the evolving relationship between humans and intelligent systems.

The output must be concise yet analytical — not just a rephrasing, but a meaningful synthesis that shows understanding

Display output exactly in the following structure: 
Summary: 
• <point 1>   
• <point 2>   
• <point 3>   
• <point 4>   
• <point 5> 

Insight: 
<single-line insight> 


Text:
{clean_text}
"""

# -------------------------------
# STEP 5: Send to Gemini
# -------------------------------
print("🔍 Analyzing and summarizing with Gemini 2.5 Flash...\n")

response = model.generate_content(prompt)

# -------------------------------
# STEP 6: Print the result
# -------------------------------
print("----------- SUMMARY & INSIGHT -----------")
print(response.text)
print("-----------------------------------------")

with open("summary_output.txt", "w", encoding="utf-8") as file:
    file.write(response.text)

print("✅ Summary saved to summary_output.txt")
