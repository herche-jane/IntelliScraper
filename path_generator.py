from bs4 import BeautifulSoup


class PathGenerator:
    """Class to generate CSS paths for elements containing specific text in HTML content."""

    def __init__(self, html_content):
        """Initialize the generator with HTML content.

        Args:
            html_content (str): HTML content to parse and generate paths for.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self._remove_scripts()

    def _remove_scripts(self):
        """Remove all <script> tags from the soup to prevent interference."""
        for script in self.soup("script"):
            script.decompose()

    def find_element_by_text(self, text):
        """Find elements containing specific text and generate paths for them.

        Args:
            text (str): Text to search for in the HTML content.

        Returns:
            list: A list of tuples (path, element) where `path` is a CSS path and `element` is the BeautifulSoup Tag.
        """
        if not text:
            raise ValueError("Text for search cannot be empty.")
        elements = self.soup.find_all(string=lambda t: text in t if t else False)
        elements_with_path = [(self._generate_path(e.parent), e.parent) for e in elements]
        return self._filter_parent_elements(elements_with_path)

    def _filter_parent_elements(self, elements_with_path):
        """Filter out parent elements if they contain other matched child elements.

        Args:
            elements_with_path (list): List of tuples containing paths and elements.

        Returns:
            list: A filtered list of tuples (path, element).
        """
        final_elements = []
        element_set = set(e[1] for e in elements_with_path)
        for path, element in elements_with_path:
            if not any(e != element and element in e.parents for e in element_set):
                final_elements.append((path, element))
        return final_elements

    def _generate_path(self, element):
        """Generate a CSS path for an element.

        Args:
            element (Tag): A BeautifulSoup Tag object for which to generate the path.

        Returns:
            str: A CSS selector path for the given element.
        """
        path = []
        while element and element.name != "[document]":
            segment = element.name
            if 'id' in element.attrs:
                segment += f'#{element["id"]}'
            elif 'class' in element.attrs:
                segment += '.' + '.'.join(element['class'])
            path.append(segment)
            element = element.parent
        path.reverse()
        return ' > '.join(path)
