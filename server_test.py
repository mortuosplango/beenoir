import server

actors = []

actors.append(server.StringPathActor("GET", "/", lambda s, h: "Index Page<br /><ul><a href='/count'>/count</a></li></ul>"))

counter = 0
def count_up(actor, handler):
    global counter
    counter = counter + 1
    return str(counter)

actors.append(server.StringPathActor("GET", "/count", count_up))

server.run(actors)
