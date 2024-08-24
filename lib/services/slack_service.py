import requests

from lib.models import UserInfo


class SlackService:
    def __init__(self, token: str):
        self.token = token

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        api_url = "https://slack.com/api/users.info"
        query_params = {"user": user_id, "include_locale": True}
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        try:
            # async with httpx.AsyncClient() as client:
            response = requests.post(url=api_url, headers=headers, params=query_params)
            response_json = response.json()
            user = response_json.get("user", None)
            return UserInfo.model_validate(user)
        except Exception:
            print("could not parse")
            return None
