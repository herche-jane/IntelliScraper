from bs4 import BeautifulSoup


class ElementFinder:
    """Class to find elements in HTML content based on CSS paths."""

    def __init__(self, html_content):
        """Initialize the finder with HTML content.

        Args:
            html_content (str): HTML content to parse and search within.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def find_element_by_path(self, path):
        """Find elements based on a CSS selector path.

        Args:
            path (str): A CSS selector path to locate elements in the HTML content.

        Returns:
            list: A list of BeautifulSoup Tag objects that match the path.

        Raises:
            ValueError: If the path is empty or None.
        """
        if not path:
            raise ValueError("The path cannot be empty.")
        try:
            return self.soup.select(path)
        except Exception as e:
            print(f"Error finding elements with path {path}: {e}")
            return []  # Return an empty list if there is an error
