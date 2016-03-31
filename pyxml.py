import os
import re
import string


class XmlSyntaxError(SyntaxError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class XmlParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.stream = None
        self.charno = 0
        self.lineno = 1
        self.token = ""
        self.char = None
        self.data = {}
        self.parse()

    def next_char(self):
        self.char = self.stream.read(1)
        if self.char == os.linesep:
            self.lineno += 1
            self.charno = 0
        self.charno += 1

    def parse(self):
        with open(self.xml_file) as self.stream:
            self.lineno = 1
            self.charno = 0
            self.token = ""
            self.next_char()
            while self.char != "":
                if self.char in string.whitespace:
                    self.next_char()
                    continue
                if self.char != "<" and self.token == "":
                    msg = 'Text encountered outside tags in "' + self.xml_file +\
                          '", line ' + str(self.lineno) + ', char ' + str(self.charno)
                    raise XmlSyntaxError(msg)
                    self.next_char()
                else:
                    self.token += self.char
                    while self.char not in string.whitespace + ">":
                        self.next_char()
                        self.token += self.char
                    if self.token.startswith("<!--"):
                        self.parse_comment()
                    else:
                        tag = self.parse_tag()
                    self.token = ""
                self.data[tag.name] = tag

    def parse_comment(self):
        while not self.token.endswith("-->"):
            self.next_char()
            self.token += self.char
        self.token = ""
        self.next_char()

    def parse_tag(self):
        tagname = self.token.strip(string.whitespace + "<>")
        tag = XmlTag(tagname)
        self.next_char()
        if not self.token.endswith(">"):
            self.parse_attributes(tag)
        self.parse_elements(tag)
        return tag

    def parse_attributes(self, tag):
        self.token = ""
        while True:
            while self.char in string.whitespace:
                self.next_char()
            while self.char not in string.whitespace + ">":
                self.token += self.char
                self.next_char()
            if self.token.startswith("<!--"):
                self.parse_comment()
            else:
                tag.add_attribute(self.token)
            if self.char == ">":
                # We're done parsing attributes, move on to the contents
                break
            elif self.char == "":
                msg = 'EoF encountered while parsing tag in "' + self.xml_file +\
                      '", line ' + str(self.lineno) + ', char ' + str(self.charno)
                raise XmlSyntaxError(msg)
            self.token = ""
        # Advance one char past the ">"
        self.next_char()

    def parse_elements(self, tag):
        self.token = ""
        while True:
            if self.token.startswith("<!--"):
                self.parse_comment()
            if self.char in string.whitespace:
                self.next_char()
                continue
            self.token += self.char
            while True:
                self.next_char()
                if self.char in string.whitespace + "<":
                    break
                self.token += self.char
            if self.token.startswith("<!--"):
                self.parse_comment()
            elif self.token.startswith("</" + tag.name):
                self.next_char()
                break
            elif self.token.startswith("<"):
                if len(self.token) == 1:
                    self.next_char()
                    continue
                tag.elements.append(self.parse_tag())
            else:
                tag.elements.append(self.token)
            self.token = ""


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

    def __str__(self):
        s = "<" + self.name
        for key in self.attributes:
            s += " " + key + "=" + self.attributes[key]
        s += ">"
        s += ' '.join([str(element) for element in self.elements])
        s += "</" + self.name + ">"
        return s


def parse_xml(filename):
    return XmlParser(filename).data

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        parser = XmlParser(sys.argv[1])
        [print(parser.data[k]) for k in parser.data]


