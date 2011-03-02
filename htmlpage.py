TEMPLATE_DIR = 'web/templates/'

class HTMLPage:
    
    def __init__(self, title="", content=""):
        self.content = content
        self.title = title
        self.head = ""
    
    def __str__(self):
        return self.template_string('simple')%{
            'title': self.title,
            'header': self.head, 
            'content': self.content
        }
    
    def template_string(self, template):
        with open('%s%s.html'%(TEMPLATE_DIR, template), "r") as fp:
            ret = fp.read()
        return ret

class ShortErrorHTMLPage(HTMLPage):
    def __init__(self, error, title='Error!'):
        HTMLPage.__init__(self, title, self.template_string('error')%{
            'heading': title,
            'text': error
        })

class HTTP404ErrorHTMLPage(ShortErrorHTMLPage):
    def __init__(self, file):
        ShortErrorHTMLPage.__init__(self, self.template_string('404')%{'file': file}, 'HTTP 404')

# some test print outs

if __name__ == '__main__':
    print '--- ShortErrorHTMLPage ---'
    print ShortErrorHTMLPage('This is a test error!')
    print '\n\n'
    print '---- HTTP404ErrorHTMLPage ---'
    print HTTP404ErrorHTMLPage('/does/not/exist')