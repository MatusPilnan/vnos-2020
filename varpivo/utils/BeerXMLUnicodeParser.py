from typing import Text, List
from xml.etree import ElementTree

from pybeerxml.parser import Parser
from pybeerxml.recipe import Recipe


class BeerXMLUnicodeParser(Parser):
    def parse(self, xml_file: Text) -> List[Recipe]:
        "Get a list of parsed recipes from BeerXML input"

        with open(xml_file, "rt", encoding='utf-8') as file:
            tree = ElementTree.parse(file)

        return self.parse_tree(tree)
