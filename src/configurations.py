###################################################################################
###### This file contains all configurations needed by the document generator 
###################################################################################


#### General settings . If any of the below is not needed, assign it to None.
LOGGER_FILE         = r"outputs\\Logs.txt"        # Log file
ERROR_FILE          = r"outputs\\Error.txt"       # Error file
RESOLVED_JSON       = r"outputs\\result.txt"      # Json after resolving datatype 
                                          
CONFLUENCE_PAGE_ID      =           
GIT_HTML_URLS           =  [""] # Add the github html url here 
CONFLUENCE_TITLE        = "" # Add the confluence page title here


GITHUB_ENTERPRISE_HOST = "" # Add the github enterprise host here
BASE_API_URL           = f"https://{GITHUB_ENTERPRISE_HOST}/xxx"  # Constructing base API URL
GIT_HEADERS_BMP        = {
                           "Accept": "application/vnd.github.v3+json",
                           "Authorization": f"token xxxx"  # Adding the personal access token for authentication
                         }


#### Confluence documentation 
CONFLUENCE_URL              = ''          # Confluence URL 
CONFLUENCE_TOKEN            = ''   # Confluence token - expiry oct 20
CONFLUENCE_USERNAME         = ''   # Confluence user name
CONFLUENCE_PASSWORD         = ''                                    # Confluence password
CONFLUENCE_HEADERS          = { 
                                'Authorization': f'Bearer {CONFLUENCE_TOKEN}',
                                'Content-Type': 'application/json'
                              }
CONFLUENCE_SPACE            = '' #  Confluence space name                                         # Confluence space key


"""
Method to write content to a file 
"""
def write_to_file(filePath, content):
	with open(filePath, "w") as file:
		if isinstance(content, dict):
			file.write(json.dumps(content))
		else:
			file.write(content)