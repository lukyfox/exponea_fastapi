from typing import List
import datetime


class Response:
    def __init__(self, time=-1, status='', message=''):
        self.response = {
            'time': time,
            'status': status,
            'message': message,
            'created': datetime.datetime.now(),
        }

    def set_time(self, time: int):
        self.response['time'] = time

    def get_time(self) -> int:
        return self.response['time']

    def set_status(self, status: str):
        self.response['status'] = status

    def get_status(self) -> str:
        return self.response['status']

    def set_message(self, message: str):
        self.response['message'] = message

    def get_message(self) -> str:
        return self.response['message']

    def as_dict(self):
        return dict(self.response)