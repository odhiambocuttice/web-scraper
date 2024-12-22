# import os
# import random
# import time
# import json
# from typing import List, Type

# from bs4 import BeautifulSoup
# from pydantic import BaseModel, create_model
# import html2text

# from dotenv import load_dotenv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# from groq import Groq

# from webdriver_manager.chrome import ChromeDriverManager
# from assets import USER_AGENTS,HEADLESS_OPTIONS,USER_MESSAGE,GROQ_LLAMA_MODEL_FULLNAME
# load_dotenv()

# # Set up the Chrome WebDriver options

# def setup_selenium():
#     options = Options()

#     # Randomly select a user agent from the imported list
#     user_agent = random.choice(USER_AGENTS)
#     options.add_argument(f"user-agent={user_agent}")

#     # Add other options
#     for option in HEADLESS_OPTIONS:
#         options.add_argument(option)

#     # Initialize the WebDriver
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)

#     return driver

# def click_accept_cookies(driver):
#     """
#     Tries to find and click on a cookie consent button. It looks for several common patterns.
#     """
#     try:
#         # Wait for cookie popup to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//button | //a | //div"))
#         )
        
#         # Common text variations for cookie buttons
#         accept_text_variations = [
#             "accept", "agree", "allow", "consent", "continue", "ok", "I agree", "got it"
#         ]
        
#         # Iterate through different element types and common text variations
#         for tag in ["button", "a", "div"]:
#             for text in accept_text_variations:
#                 try:
#                     # Create an XPath to find the button by text
#                     element = driver.find_element(By.XPATH, f"//{tag}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
#                     if element:
#                         element.click()
#                         print(f"Clicked the '{text}' button.")
#                         return
#                 except:
#                     continue

#         print("No 'Accept Cookies' button found.")
    
#     except Exception as e:
#         print(f"Error finding 'Accept Cookies' button: {e}")

# def fetch_html_selenium(url):
#     driver = setup_selenium()
#     try:
#         driver.get(url)
        
#         # Add random delays to mimic human behavior
#         time.sleep(1)  # Adjust this to simulate time for user to read or interact
#         driver.maximize_window()
        
#         # Add more realistic actions like scrolling
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)  # Simulate time taken to scroll and read
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(1)
#         html = driver.page_source
#         return html
#     finally:
#         driver.quit()

# def clean_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
    
#     # Remove headers and footers based on common HTML tags or classes
#     for element in soup.find_all(['header', 'footer']):
#         element.decompose()  # Remove these tags and their content

#     return str(soup)

# def html_to_markdown_with_readability(html_content):

#     cleaned_html = clean_html(html_content)  
    
#     # Convert to markdown
#     markdown_converter = html2text.HTML2Text()
#     markdown_converter.ignore_links = False
#     markdown_content = markdown_converter.handle(cleaned_html)
    
#     return markdown_content

# def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
#     """
#     Dynamically creates a Pydantic model based on provided fields.
#     field_name is a list of names of the fields to extract from the markdown.
#     """
#     # Create field definitions using aliases for Field parameters
#     field_definitions = {field: (str, ...) for field in field_names}
#     # Dynamically create the model with all field
#     return create_model('DynamicListingModel', **field_definitions)


# def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
#     """
#     Create a container model that holds a list of the given listing model.
#     """
#     return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

# def generate_system_message(listing_model: BaseModel) -> str:
#     """
#     Dynamically generate a system message based on the fields in the provided listing model.
#     """
#     # Use the model_json_schema() method to introspect the Pydantic model
#     schema_info = listing_model.model_json_schema()

#     # Extract field descriptions from the schema
#     field_descriptions = []
#     for field_name, field_info in schema_info["properties"].items():
#         # Get the field type from the schema info
#         field_type = field_info["type"]
#         field_descriptions.append(f'"{field_name}": "{field_type}"')

#     # Create the JSON schema structure for the listings
#     schema_structure = ",\n".join(field_descriptions)

#     # Generate the system message dynamically
#     system_message = f"""
#     You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
#                         from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
#                         with no additional commentary, explanations, or extraneous information. When the text has ellipsis, find the full text.The locations of the events should be in Kenya only.
#                         Make sure the photo links are valid.
#                         You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
#                         Please process the following text and provide the output in pure JSON format with no words before or after the JSON:
#     Please ensure the output strictly follows this schema:

#     {{
#         "listings": [
#             {{
#                 {schema_structure}
#             }}
#         ]
#     }} """

#     return system_message


# def format_data(data, DynamicListingsContainer, DynamicListingModel, selected_model):
#     token_counts = {}
        
#     # Dynamically generate the system message based on the schema
#     sys_message = generate_system_message(DynamicListingModel)
#     # Point to the local server
#     client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

#     completion = client.chat.completions.create(
#     messages=[
#         {"role": "system","content": sys_message},
#         {"role": "user","content": USER_MESSAGE + data}
#     ],
#     model=GROQ_LLAMA_MODEL_FULLNAME
#     )

#     # Extract the content from the response
#     response_content = completion.choices[0].message.content
    
#     # Convert the content from JSON string to a Python dictionary
#     parsed_response = json.loads(response_content)
    
#     # completion.usage
#     token_counts = {
#         "input_tokens": completion.usage.prompt_tokens,
#         "output_tokens": completion.usage.completion_tokens
#     }

#     return parsed_response, token_counts

import os
import random
import time
import json
from typing import List, Type
from bs4 import BeautifulSoup
from pydantic import BaseModel, create_model
import html2text
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from groq import Groq
from assets import USER_AGENTS, USER_MESSAGE, GROQ_LLAMA_MODEL_FULLNAME

load_dotenv()

def fetch_html_selenium(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-sandbox',
            ]
        )
        try:
            # Create a new page
            page = browser.new_page(
                user_agent=random.choice(USER_AGENTS)
            )
            
            # Navigate to the URL
            page.goto(url, wait_until='networkidle')
            
            # Simulate scrolling
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            
            # Get the page content
            content = page.content()
            return content
            
        except Exception as e:
            print(f"Error fetching HTML: {e}")
            return None
        finally:
            browser.close()

# Rest of your functions remain unchanged
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['header', 'footer']):
        element.decompose()
    return str(soup)

def html_to_markdown_with_readability(html_content):
    cleaned_html = clean_html(html_content)
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    return markdown_converter.handle(cleaned_html)

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def generate_system_message(listing_model: BaseModel) -> str:
    schema_info = listing_model.model_json_schema()
    field_descriptions = []
    for field_name, field_info in schema_info["properties"].items():
        field_type = field_info["type"]
        field_descriptions.append(f'"{field_name}": "{field_type}"')
    schema_structure = ",\n".join(field_descriptions)
    
    return f"""
    You are an intelligent text extraction and conversion assistant. Your task is to extract structured information 
    from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, 
    with no additional commentary, explanations, or extraneous information. When the text has ellipsis, find the full text.The locations of the events should be in Kenya only.
    Make sure the photo links are valid.
    You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language.
    Please process the following text and provide the output in pure JSON format with no words before or after the JSON:
    Please ensure the output strictly follows this schema:
    {{
        "listings": [
            {{
                {schema_structure}
            }}
        ]
    }} """

def format_data(data, DynamicListingsContainer, DynamicListingModel, selected_model):
    token_counts = {}
    sys_message = generate_system_message(DynamicListingModel)
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": sys_message},
            {"role": "user", "content": USER_MESSAGE + data}
        ],
        model=GROQ_LLAMA_MODEL_FULLNAME
    )
    
    response_content = completion.choices[0].message.content
    parsed_response = json.loads(response_content)
    
    token_counts = {
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }
    
    return parsed_response, token_counts