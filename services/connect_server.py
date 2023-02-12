import requests
from pyrogram import Client
from pyrogram.raw.functions.contacts import ResolveUsername

api_id = 12552206
api_hash = "a374231734920c72574a978e3d6d867d"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

class ValentinesService:
    limit = 5
    base_url = "http://localhost:8000/api/"

    def check_connect(self):
        response = requests.get(f"{self.base_url}ping/")
        response.raise_for_status()

    def get_my_valentines(self, user_data):
        query_params = dict(recipient=user_data['recipient'])
        response = requests.get(f"{self.base_url}valentines/", query_params)
        response.raise_for_status()
        return response.json()

    def patch_valentines(self, valentine_id):
        validate_wallet_data = {'status': True}
        response = requests.patch(f"{self.base_url}valentines/{valentine_id}/", json=validate_wallet_data)
        response.raise_for_status()
        return response.json()

    def post_valentines(self, valentine_data):
        validate_wallet_data = {
            'sender': valentine_data['sender'],
            'recipient': valentine_data['recipient'],
            'is_publish': valentine_data['is_publish'],
            'text': valentine_data['text'],
            'file_id': valentine_data['file_id'],
        }
        response = requests.post(f"{self.base_url}valentines/", json=validate_wallet_data)
        response.raise_for_status()
        return response.json()

    def get_user_data(self, username):
        with app:
            r = app.invoke(ResolveUsername(username=username))
            return r



valentines_service = ValentinesService()