class HTMLPage:
    def __init__(self, title, content):
        self.content = content
        self.title = title
        self.head = ""
    
    def __str__(self):
        try:
            return self.template_string("simple")%(self.title, self.head, self.content)
        except BaseException as e:
            return "Problem creating HTML Page: \n" + str(e)
    
    def template_string(self, template):
        fp = open("web/templates/" + str(template) + ".html", "r")
        return fp.read()

class ShortErrorHTMLPage(HTMLPage):
    def __init__(self, error):
        HTMLPage.__init__("Fehler!", self.template_string("error")%(error))