from textual_serve.server import Server
server = Server("python -m main ETH_timetable.ics 16.9.2024")
server.serve()
