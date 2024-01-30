import json

class Player:
    def __init__(self,username,password):
        if len(username) < 4 or len(username) > 14:
            raise ValueError("username must be at least 4 characters and not more than 14 characters")
        if len(password) < 10 or len(password) > 20:
            raise ValueError("password must be ar least 10 characters and not more than 20 characters")
        self.username = username
        self.password = password
        self.games_played = 0
        self.total_score = 0


    def to_dict(self):
        return {"username": self.username, "password": self.password,"games_played": self.games_played,"total_score": self.total_score}    

    def to_json(self):
        return json.dumps({"username": self.username, "password": self.password,"games_played": self.games_played,"total_score": self.total_score})    
    def input_from_dict(self,dict):
        self.username = dict['username']
        self.password = dict['password']
        
    def is_valid(self):
        if len(self.username) < 4 or len(self.username) > 14:
            raise ValueError("username must be at least 4 characters and not more than 14 characters ")
        if len(self.password) < 10 or len(self.password) > 20:
            raise ValueError("password must be ar least 10 characters and not more than 20 characters")
        return True