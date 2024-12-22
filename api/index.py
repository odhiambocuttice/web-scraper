# from http.server import BaseHTTPRequestHandler
# import json
# from scraper import create_dynamic_listing_model, create_listings_container_model, fetch_html_selenium, format_data, html_to_markdown_with_readability

# class handler(BaseHTTPRequestHandler):

#     def do_GET(self):
#         try:
#             url = 'https://www.ticketsasa.com/events/listing/upcoming'
#             fields=['Name', 'Price', 'Location','Time', 'Photos']
            
#             # Scrape data
#             raw_html = fetch_html_selenium(url)

#             # Scrape data
#             raw_html = fetch_html_selenium(url)
        
#             markdown = html_to_markdown_with_readability(raw_html)
            
#             # Create the dynamic listing model
#             DynamicListingModel = create_dynamic_listing_model(fields)

#             # Create the container model that holds a list of the dynamic listing models
#             DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
            
#             # Format data
#             formatted_data, token_counts = format_data(markdown, DynamicListingsContainer,DynamicListingModel,"Groq Llama3.1 70b")  # Use markdown, not raw_html
#             print(formatted_data)
#             # Save formatted data

#             # Convert formatted_data back to text for token counting
#             formatted_data_text = json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data) 
          
        
#             self.send_response(200)
#             self.send_header('Content-type','text/plain')
#             self.end_headers()
#             self.wfile.write(formatted_data_text.encode('utf-8'))
#             return
#         except Exception as e:
#             print(f"An error occurred: {e}")


from http.server import BaseHTTPRequestHandler
import json
from scraper import (
    create_dynamic_listing_model,
    create_listings_container_model,
    fetch_html_selenium,
    format_data,
    html_to_markdown_with_readability
)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Define constants for scraping
        url = 'https://www.ticketsasa.com/events/listing/upcoming'
        fields = ['Name', 'Price', 'Location', 'Time', 'Photos']

        try:
            # Step 1: Scrape data
            raw_html = fetch_html_selenium(url)

            # Step 2: Convert to markdown with better readability
            markdown = html_to_markdown_with_readability(raw_html)

            # Step 3: Create dynamic models
            DynamicListingModel = create_dynamic_listing_model(fields)
            DynamicListingsContainer = create_listings_container_model(DynamicListingModel)

            # Step 4: Format the scraped data
            formatted_data, token_counts = format_data(
                markdown,
                DynamicListingsContainer,
                DynamicListingModel,
                "Groq Llama3.1 70b"
            )

            # Step 5: Send the formatted response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Convert formatted data to JSON string for response
            formatted_data_text = json.dumps(
                formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data
            )
            self.wfile.write(formatted_data_text.encode('utf-8'))

        except Exception as e:
            # Log the error for debugging
            error_message = {"error": str(e)}
            print(f"An error occurred: {e}")

            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
