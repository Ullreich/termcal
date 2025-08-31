from textual_serve.server import Server
server = Server("python -m week_prototype ETH_timetable.ics 16.9.2024")
server.serve()
