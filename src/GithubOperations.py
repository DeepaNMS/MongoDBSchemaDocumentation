import json
import requests 
import base64
import src.configurations as configurations
import re

# Global Constants

programName = "GithubOperations.py"

class GithubOperations:
    """
    Integration class for Github operations.
    Handles reading the committed file content.
    """
    def __init__(self):
        """
        Initialize GithubOperations
        """
        self.repo_owner           = ""
        self.repo_name            = ""
        self.repo_branch          = ""
        self.target_path          = ""
        self.gitUrls              = configurations.GIT_HTML_URLS
        self.gitFileAndContent    = {}
        self.gitFileToRepo        = {}
        self.gitFileAndContentAndCollection    = {}

        

    """
    From a given Github HTML repo URL, extract the different repo parameters
    """
    def setRepoValues(self, url):
        original_url = url
        pattern = r'https://[^/]+/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<branch>[^/]+)/(?P<target_path>.+)'
        match = re.match(pattern, original_url)
        if match:
            self.repo_owner  = match.group('owner')
            self.repo_name   = match.group('repo')
            self.repo_branch = match.group('branch')
            self.target_path = match.group('target_path')
        else:
            raise ValueError("Could not parse original_url for owner, repo, branch, and target_path")
    
    """
    Check if the contents of file is a valid mongodb schema definition 
    Parameters :
                  fileContent - Git file content to be checked
    Returns    :
                  flgValid - Boolean flag . Returns true if file is valid, else return false
    """
    def isValidFile(self, fileContent): 
        flg = False
        if fileContent and ("@Data" in fileContent or "abstract class" in fileContent):
            flg = True
        
        return flg
    
    
    """
    From a given Github HTML repo URL, extract the different java files
    Parameters : GithubOperations object 
                 Git url to fetch the java files from
    Returns    : Sets a dictionary jsonOps.gitFileAndContent = 
                                           {
                                               gitFileName : gitFileContent
                                           }
    """
    def getJavaFilesFromGithubUrl(self, url, logger=None):
        methodName = "getJavaFilesFromGithubUrl"
        logger.write_log(programName + ":"+ methodName + "starts")
        # API endpoint to get the Git tree recursively

        tree_api_url = f"{configurations.BASE_API_URL}/repos/{self.repo_owner}/{self.repo_name}/git/trees/{self.repo_branch}?recursive=1"
        logger.write_log("----->tree_api_url="+tree_api_url)
        try:
            response = requests.get(tree_api_url, headers=configurations.GIT_HEADERS_BMP)
            response.raise_for_status()  # Raise an exception for bad status codes
            tree_data = response.json()

            java_files = []
            if "tree" in tree_data:
                for item in tree_data["tree"]:
                    if item["type"] == "blob" and item["path"].startswith(self.target_path) and item["path"].endswith(".java"):
                        file_content = self.getGitFileContent(item["path"], logger)
                        if self.isValidFile(file_content):
                            java_files.append(item["path"])
                            self.gitFileAndContent[item["path"]] = file_content
                            self.gitFileToRepo[item["path"]] = self.repo_name
            return java_files
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Git tree: {e}")
            logger.exception(f"Exception occurred during Git fetch: {e}")
            if configurations.ERROR_FILE:
                configurations.write_to_file(configurations.ERROR_FILE, e)  
            return []

    """
    Check if the file content contains the collection indicator. 
    If yes add a flag to the dictionary .
    Parameters : Dictionary gitFileAndContent 
    Returns    : Updated dictionary with a flag also added in values list 
    """
    def identifyCollections(self, logger=None):
        methodName = "identifyCollections"
        logger.write_log(programName + ":"+ methodName + "starts")
        updated_dict = {}
        for filename, content in self.gitFileAndContent.items():
            # Search for @Document(collection annotation, case-insensitive)
            found = False
            pattern = r"@Document\s*\("
            if re.search(pattern, content, re.IGNORECASE):
                found = True
            updated_dict[filename] = [content, found]
        self.gitFileAndContentAndCollection = updated_dict
      

    """
    Get the content of a Github java class file 
    Parameters :
                  filePath - Git File Path
    Returns    :
                  gitFileContent - Content of the git file
    """
    def getGitFileContent(self, filePath, logger=None):
        methodName = "getGitFileContent"
        logger.write_log(programName + ":"+ methodName + "starts")
        
        # Read the github committed file
        fileContent = ""
        fileGitPath = f"{configurations.BASE_API_URL}/repos/{self.repo_owner}/{self.repo_name}/contents/{filePath}"
        logger.write_log("-----> Git file path="+fileGitPath)
        try:
            response = requests.get(fileGitPath, headers=configurations.GIT_HEADERS_BMP)
            response.raise_for_status()
            logger.write_log("-----> Git file path content read!")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred while trying to fetch Github file content: {e}")
            logger.exception(f"Exception occurred during Git content fetch: {e}")
            self.committedFileContent = ""
            return
        except Exception as e:
            print(f"General error occurred: {e}")
            self.committedFileContent = ""
            return

        # Check for redirect or login page (not authenticated)
        if response.status_code != 200:
            print(f"Failed to fetch {fileGitPath}: {response.status_code}")
            logger.write_log("-----> Git content read status="+str(response.status_code ))
            return
        # Check if response is JSON and contains expected keys
        try:
            file_data = response.json()
            if 'content' in file_data:
                fileContent = base64.b64decode(file_data['content']).decode('utf-8')
                logger.write_log("-----> Git content read ")
            else:
                logger.write_log("-----> Unexpected JSON structure for "+fileGitPath)
                fileContent = ""
        except Exception as e:
            print(f"Error decoding JSON or file content for {fileGitPath}: {e}")
            logger.write_log("-----> Error decoding JSON or file content for "+ fileGitPath)
            fileContent = ""
        # Set the attribute
        return fileContent

    # Create json file out of data model definitions   
    # Parameters :
    #    gitFileAndContent : A dictionary of format  
    #                        {
    #                           gitFileName : gitFileContent
    #                        }
    # Returns :
    #     jsonContent : Json corresponding to data model definitions
    def generate_data_model_json(self, logger=None):
        methodName = "generate_data_model_json"
        logger.write_log(programName + ":"+ methodName + "starts")
        output = {}
        for filename, class_content in self.gitFileAndContent.items():
            class_name = filename.replace('.java', '')
            # Here you would parse class_content to extract fields and structure
            # For demonstration, we use a placeholder schema
            output[class_name] = {
                    "title": class_name,
                    "type": "object",
                    "description": f"Object containing information about the {class_name.lower()}",
                    "properties": {},  # TODO: parse actual properties from class_content
                    "additionalProperties": False
            }
            return json.dumps(output, indent=2)
    