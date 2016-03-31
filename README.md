# pyxml

Overview:
  This is a simple XML file parser for Python 3.  Parsing is done at a character level, whitespace is ignored except to indicate the end of a token.  First it reads a full token, then identifies it as a comment, open tag, attribute, element, or close tag.  Parsing is done recursively.
  --Note that it does not support parsing a string.  Currently it uses file descriptor characterconsumption to advance through the XML.

Data Organization:
  XmlParser uses self.data to store everything read out of the file.  data is an ordered list of XmlTag objects that represent the outermost tags.  While in the process of parsing, XmlParser tracks the line and character coordinate that it is parsing in XmlParser._lineno and Xmlparser._charno.  The current token is XmlParser._token and the current character is XmlParser._char. The file being processed is XmlParser.xml_file.  The file descriptor is XmlParser._stream.  If no parsing is in progress, these values are all None, and they should not be modified by anything other than the parser itself.
  
  All the data ends up in XmlTag objects.  XmlTag objects have a .name string, .attributes dictionary, and a .elements list.  Index operations into an XmlTag will look through .attributes if indexed with a string, or .elements if indexed with an int.  Any other index type will result in an error. In operations with an XmlTag will first check in .attributes' keys for a string and, if nothing is found, will then search .elements
