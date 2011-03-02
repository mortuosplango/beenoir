from actor_http_server import *

actors = []

actors.append(StringPathActor("GET", "/", "Index Page<br /><ul><a href='/count'>/count</a></li></ul>"))

counter = 0
def count_up(actor, handler):
    global counter
    counter = counter + 1
    return str(counter)

actors.append(StringFuncPathActor("GET", "/count", count_up))

run(actors)
