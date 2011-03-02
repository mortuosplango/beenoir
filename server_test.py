from actor_http_server import *

actors = []

actors.append(StringPathActor("GET", "/", "Index Page<br /><ul><li><a href='/count'>/count</a></li><li><a href='ballasd'>404</a></li></ul>"))

counter = 0
def count_up(actor, handler):
    global counter
    counter = counter + 1
    return str(counter)

actors.append(StringFuncPathActor("GET", "/count", count_up))

actors.append(StaticFilesActor("web/", "/static/"))

run(actors)
