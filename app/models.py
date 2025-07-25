from datetime import datetime

class URLMapping:
    def __init__(self, original_url, short_code):
        self.original_url = original_url
        self.short_code = short_code
        self.clicks = 0
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "original_url": self.original_url,
            "short_code": self.short_code,
            "clicks": self.clicks,
            "created_at": self.created_at
        }
