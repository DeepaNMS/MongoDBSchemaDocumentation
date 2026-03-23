import src.configurations  as configurations
from atlassian import Confluence
import logging
import re

class ConfluenceOperations:
    """
    Integration class for Confluence operations.
    """
    
    """
    Constructor
    """ 
    def __init__(self):
        """
        Initialize ConfluenceOperations
        """
        self.confluence = Confluence(
                               url=configurations.CONFLUENCE_URL,
                               username=configurations.CONFLUENCE_USERNAME,
                               password=configurations.CONFLUENCE_PASSWORD,
                               verify_ssl=False
                          )
        self.PageName_PageId = {}
    """
    Check if a page with a specific title exists as a child of a parentPage
    Parameters :
                pageTitle : Title of the page to be searched
                parentPageId : Page id of the parent page 
    Returns : 
                If the page is found, return pageId. Otherwise return None.
    """
    def pageExists(self, pageTitle, parentPageId):
        try:
            # Get all child pages of the parent page
            children = self.confluence.get_child_pages(parentPageId)
            for child in children:
                # The title is usually in the 'title' key
                if 'title' in child and child['title'] == pageTitle:
                    return child.get('id')
            return None
        except Exception as e:
            logging.error(f"Error checking if page exists: {e}")
            return None
    
    """
    Create a page with a specific title as the child of a parent page
    Parameters:
                parentPageId - Page id of the parent page
                childPageTitle - Title of the child page
                confluenceSpace - Confluence Space in which the page needs to be created
                body - Body of the page to be created
    Return:
                If the page creation is successful, return id of the page created.
                Else return None.
    """
    def createChildPage(self, parentPageId, childPageTitle,confluenceSpace,body=""):
        print("parent id =", parentPageId)
        print("child title=", childPageTitle)
        try:
            result = self.confluence.create_page(
                space=confluenceSpace,  # Space is optional if parentPageId is provided
                title=childPageTitle,
                body=body,
                parent_id=parentPageId,
                type="page",
                representation="storage"
            )
            logging.info(f"Created child page '{childPageTitle}' under parent ID {parentPageId}.")
            # Return the ID of the created child page if available
            if result and isinstance(result, dict) and 'id' in result:
                return result['id']
        except Exception as e:
            logging.error(f"Error creating child page: {e}")
            return None

    # Update contents to an existing confluence page
    def update_page(self,body, logger):
        # Remove angle brackets from an input string
        def remove_angle_brackets_from_list_of(input_str):
            """
                Accepts a string and replaces occurrences of 'List of <xxxxx>' with 'List of xxxxx'.
                Removes angle brackets around xxxxx (dynamic text).
            """
            # Use regex to find and replace 'List of <xxxxx>' with 'List of xxxxx'
            return re.sub(r'List of\s*<([^>]+)>', r'List of \1', input_str)

        body = body.replace('\n', '')
        body = remove_angle_brackets_from_list_of(body)
        logger.write_log(f"In Update page : {body}")
    
        status = self.confluence.update_page(parent_id=None,
               page_id=configurations.CONFLUENCE_PAGE_ID,
               title=configurations.CONFLUENCE_TITLE,

               body=body,
               representation='storage'  )
        logging.info("Update confluence page status = %s", status)
        return status
