from ws4py.client.threadedclient import WebSocketClient


class testClient(WebSocketClient):
    def received_message(self, message):
        print(message)

if __name__ == "__main__":
    try:
        ws = testClient("ws://127.0.0.1:8080/ws")
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()