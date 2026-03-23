"""
Main entry point for the sample Python project.
"""

# Import all needed libraries 

import src.GithubOperations as GithubOperations
import src.JsonOperations as JsonOperations 
import src.HTMLOperations as HTMLOperations
import src.configurations as configurations
import src.ConfluenceOperations as ConfluenceOperations
import src.Logger as Logger
import json
import os


# Global constants 
programName = "main.py"


"""
Method to write content to a file 
"""
def write_to_file(filePath, content):
	with open(filePath, "w") as file:
		if isinstance(content, dict):
			file.write(json.dumps(content))
		else:
			file.write(content)

def main():
    
    # Create all objects
    github_ops     = GithubOperations.GithubOperations()         # Object for github operations 
    confluenceOps  = ConfluenceOperations.ConfluenceOperations() # Object for confluence operations
    json_ops       = JsonOperations.JsonOperations()             # Object for JSON operations 
    html_ops       = HTMLOperations.HTMLOperations()             # Object for HTML operations
    logger 	       = Logger.Logger()
    logger.setup_logger(configurations.LOGGER_FILE)
    logger.write_log(programName + ":Automatic Datamodel Documentation project started !!!")
    logger.write_log(programName + ":Objects created successfully !")
    
    #-------------------------------------------------------------------------
    # From the input Github HTML URLs, identify all java classes and 
    # its content as a dictionary where the keyname is the file name and the
    # value is the file content. 
    # The structure of the dictionary is as follows :
    #             gitFileAndContent = 
    #                                {
    #                                  gitFileName : gitFileContent
    #                                }
    #-------------------------------------------------------------------------
    
    for url in configurations.GIT_HTML_URLS:
        github_ops.setRepoValues(url)
        classFiles = github_ops.getJavaFilesFromGithubUrl(url, logger)
        
    # Add to logs the identified eligible classes
    for i in github_ops.gitFileAndContent.keys():
         message = "File " + i 
         logger.write_log(message)
    
    #-------------------------------------------------------------------------
    # From the created dictionary , create a json string without LLM
    #-------------------------------------------------------------------------
    
    jsonStr = json_ops.java_dict_to_json_schema_withoutllm(github_ops.gitFileAndContent, file_to_repo=github_ops.gitFileToRepo)
    if configurations.RESOLVED_JSON:
                configurations.write_to_file(configurations.RESOLVED_JSON, jsonStr)  
     

    #---------------------------------------------------------------------------
    # Update the created dictionary , to have mongo collection information also
    #---------------------------------------------------------------------------
    
    github_ops.identifyCollections(logger)
    resultHTML = ""
    finalHTML = ""
    # Add to logs the identified MongoDB collections
    for i in github_ops.gitFileAndContentAndCollection.keys():
         if github_ops.gitFileAndContentAndCollection[i][1] is not False:
            message = "Collection Found : " + i 
            logger.write_log(message)
            base_name = os.path.basename(i)  # "PaymentTransactionEntity.java"
            class_name = os.path.splitext(base_name)[0]  # "PaymentTransactionEntity"
            repo_name = github_ops.gitFileToRepo.get(i, '')
            schema_key = f"{repo_name}_{class_name}" if repo_name else class_name
            message = "Generating HTML for class : " + schema_key
            logger.write_log(message)
            resultHTML = html_ops.generateHTML(jsonStr, schema_key, logger)
            if resultHTML:
                  finalHTML = finalHTML + resultHTML
            else:
                  logger.write_log(f"WARNING: Empty HTML generated for {schema_key} - check for exceptions above")
    if finalHTML:
        confluenceOps.update_page(finalHTML, logger)

if __name__ == "__main__":
    main()
