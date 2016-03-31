import os
import re
import string


class XmlSyntaxError(SyntaxError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XmlTag:
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.elements = []

    def add_attribute(self, token):
        split = token.split("=")
        if re.match("[0-9]+", split[1]):
            self.attributes[split[0]] = int(split[1])
        elif re.match("[0-9A-Fa-f]+", split[1]):
            self.attributes[split[0]] = int(split[1], 16)
        elif re.match("[0-9]+\.[0-9]+", split[1]):
            self.attributes[split[0]] = float(split[1])
        elif re.match("[0-9A-Fa-f]+\.[0-9A-Fa-f]+", split[1]):
            self.attributes[split[0]] = float(split[1])
        else:
            self.attributes[split[0]] = split[1]

    def __iter__(self):
        return self.elements.__iter__()

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.attributes[item]
        elif isinstance(item, int):
            return self.elements[item]
        else:
            raise IndexError("Index given to XmlTag is not a string or int!")

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self.attributes
        return item in self.elements

    def __str__(self):
        s = "<" + self.name
        for key in self.attributes:
            s += " " + key + "=" + self.attributes[key]
        s += ">"
        s += ' '.join([str(element) for element in self.elements])
        s += "</" + self.name + ">"
        return s


class XmlParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self._stream = None
        self._lineno = None
        self._charno = None
        self._token = None
        self._char = None
        self.data = []
        self.parse()

    def next_char(self):
        self._char = self._stream.read(1)
        if self._char == os.linesep:
            self._lineno += 1
            self._charno = 0
        self._charno += 1

    def parse(self):
        self.data = []
        with open(self.xml_file) as self._stream:
            self._lineno = 1
            self._charno = 0
            self._token = ""
            self.next_char()
            while self._char != "":
                if self._char in string.whitespace:
                    self.next_char()
                    continue
                if self._char != "<" and self._token == "":
                    msg = 'Text encountered outside tags in "' + self.xml_file +\
                          '", line ' + str(self._lineno) + ', char ' + str(self._charno)
                    raise XmlSyntaxError(msg)
                else:
                    self._token += self._char
                    while self._char not in string.whitespace + ">":
                        self.next_char()
                        self._token += self._char
                    if self._token.startswith("<!--"):
                        self.parse_comment()
                    else:
                        tag = self.parse_tag()
                    self._token = ""
                self.data.append(tag)
        self._stream = None
        self._lineno = None
        self._charno = None
        self._token = None
        self._char = None

    def parse_comment(self):
        while not self._token.endswith("-->"):
            self.next_char()
            self._token += self._char
        self._token = ""
        self.next_char()

    def parse_tag(self):
        tagname = self._token.strip(string.whitespace + "<>")
        tag = XmlTag(tagname)
        self.next_char()
        if not self._token.endswith(">"):
            self.parse_attributes(tag)
        self.parse_elements(tag)
        return tag

    def parse_attributes(self, tag):
        self._token = ""
        while True:
            while self._char in string.whitespace:
                self.next_char()
            while self._char not in string.whitespace + ">":
                self._token += self._char
                self.next_char()
            if self._token.startswith("<!--"):
                self.parse_comment()
            else:
                tag.add_attribute(self._token)
            if self._char == ">":
                # We're done parsing attributes, move on to the contents
                break
            elif self._char == "":
                msg = 'EoF encountered while parsing tag in "' + self.xml_file +\
                      '", line ' + str(self._lineno) + ', char ' + str(self._charno)
                raise XmlSyntaxError(msg)
            self._token = ""
        # Advance one char past the ">"
        self.next_char()

    def parse_elements(self, tag):
        self._token = ""
        while True:
            if self._token.startswith("<!--"):
                self.parse_comment()
            if self._char in string.whitespace:
                self.next_char()
                continue
            self._token += self._char
            while True:
                self.next_char()
                if self._char in string.whitespace + "<":
                    break
                self._token += self._char
            if self._token.startswith("<!--"):
                self.parse_comment()
            elif self._token.startswith("</" + tag.name):
                self.next_char()
                break
            elif self._token.startswith("<"):
                if len(self._token) == 1:
                    self.next_char()
                    continue
                tag.elements.append(self.parse_tag())
            else:
                tag.elements.append(self._token)
            self._token = ""


def parse_xml(filename):
    return XmlParser(filename).data

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        parser = XmlParser(sys.argv[1])
        [print(tag) for tag in parser.data]


