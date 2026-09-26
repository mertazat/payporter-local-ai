from datetime import datetime


class APIService:
    def __init__(self):
        self.requests = []
        self.rate_limits = {}

    def log_request(self, user_id, endpoint, method):
        request = {
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }

        self.requests.append(request)
        return {"message": "Request logged successfully"}

    def set_rate_limit(self, user_id, limit=100):
        self.rate_limits[user_id] = {
            "limit": limit,
            "used": 0
        }

        return {
            "user_id": user_id,
            "limit": limit
        }

    def check_rate_limit(self, user_id):
        data = self.rate_limits.get(user_id)

        if not data:
            return {"allowed": True}

        if data["used"] >= data["limit"]:
            return {
                "allowed": False,
                "error": "Rate limit exceeded"
            }

        data["used"] += 1
        return {
            "allowed": True,
            "remaining": data["limit"] - data["used"]
        }

    def get_request_history(self, user_id):
        return [
            request
            for request in self.requests
            if request["user_id"] == user_id
        ]
