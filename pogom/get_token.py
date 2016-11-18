
        self.route("/get_token", methods=['GET'])(self.get_token)

    def get_token(self):
        token = Token.get_match(datetime.utcnow()-timedelta(minutes=30))
        return token.token