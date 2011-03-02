from actor_http_server import *

actors = []

actors.append(StringPathActor("GET", "/", "Index Page<br /><ul><li><a href='/count'>/count</a></li><li><a href='ballasd'>404</a></li><li><a href='google'>google redirect</a></li></ul>"))

counter = 0
def count_up(actor, handler):
    global counter
    counter = counter + 1
    return str(counter)

actors.append(StringFuncPathActor("GET", "/count", count_up))
actors.append(PathActor("GET", "/google", lambda a,h: h.send_redirect("http://www.google.de")))

actors.append(StaticFilesActor("/static/", "web/"))

run(actors)
