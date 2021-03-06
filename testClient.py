from ws4py.client.threadedclient import WebSocketClient
import json


class TestClient(WebSocketClient):
    def opened(self):
        msg = {
            "module": "system",
            "command": "get_modules",
            "data": {}
        }
        # self.send(json.dumps(msg, ensure_ascii=False))
        msg["module"] = "weather"
        msg["command"] = "get_weather"
        # self.send(json.dumps(msg, ensure_ascii=False))
        msg["module"] = "notes"
        msg["command"] = "remove_note"
        msg["data"] = {'id': 1}
        self.send(json.dumps(msg, ensure_ascii=False))
        msg["command"] = "get_notes"
        self.send(json.dumps(msg, ensure_ascii=False))

    def received_message(self, message):
        print(message)

if __name__ == "__main__":
    try:
        ws = TestClient("ws://127.0.0.1:8080/ws")
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()