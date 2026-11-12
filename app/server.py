
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from app.missions import (
    get_missions,
    get_mission,
    create_mission,
    delete_mission
)


class MissionHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):

        response = json.dumps(data).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()

        self.wfile.write(response)

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/missions":

            return self.send_json(
                200,
                get_missions()
            )

        if path.startswith("/missions/"):

            try:
                mission_id = int(path.rsplit("/", 1)[1])

            except ValueError:

                return self.send_json(
                    400,
                    {"error": "Invalid mission ID"}
                )

            mission = get_mission(mission_id)

            if mission is None:

                return self.send_json(
                    404,
                    {"error": "Mission not found"}
                )

            return self.send_json(
                200,
                mission
            )

        return self.send_json(
            404,
            {"error": "Endpoint not found"}
        )

    def do_POST(self):

        if urlparse(self.path).path != "/missions":

            return self.send_json(
                404,
                {"error": "Endpoint not found"}
            )

        try:

            length = int(
                self.headers.get("Content-Length", "0")
            )

            if length > 100000:

                return self.send_json(
                    413,
                    {"error": "Request too large"}
                )

            data = json.loads(
                self.rfile.read(length)
            )

            mission = create_mission(
                data.get("name", ""),
                data.get("description", ""),
                data.get("priority", "medium")
            )

            return self.send_json(
                201,
                mission
            )

        except (ValueError, json.JSONDecodeError) as error:

            return self.send_json(
                400,
                {"error": str(error)}
            )

    def do_DELETE(self):

        try:

            mission_id = int(
                urlparse(self.path).path.rsplit("/", 1)[1]
            )

        except (ValueError, IndexError):

            return self.send_json(
                400,
                {"error": "Invalid mission ID"}
            )

        if delete_mission(mission_id):

            return self.send_json(
                200,
                {"message": "Mission deleted"}
            )

        return self.send_json(
            404,
            {"error": "Mission not found"}
        )


if __name__ == "__main__":

    server = HTTPServer(
        ("127.0.0.1", 8000),
        MissionHandler
    )

    print("SpaceRescue running on port 8000")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("Server stopped")

    finally:
        server.server_close()
