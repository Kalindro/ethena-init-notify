import requests


class PushbulletClient:
    @staticmethod
    def send_message(api_token, message):
        headers = {
            "Access-Token": api_token,
            "Content-Type": "application/json"
        }
        data = {
            "type": "note",
            "title": "Notification",
            "body": message
        }
        response = requests.post("https://api.pushbullet.com/v2/pushes", headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Pushbullet error: {response.text}")
