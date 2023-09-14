class UserException(Exception):
    def as_error_response(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "message": str(self),
        }


class PlayerAlreadyInGameException(UserException):
    def __init__(self, game_id: str):
        super().__init__(f"Already in a game with ID: {game_id}")


class PlayerNotInGameException(UserException):
    def __init__(self):
        super().__init__("Not in a game")


class GameNotFoundException(UserException):
    def __init__(self, game_id: str):
        super().__init__(f"No game found with ID: {game_id}")


class NotPlayerTurnException(UserException):
    def __init__(self):
        super().__init__("Not the current player's turn")


class GameFullException(UserException):
    def __init__(self, game_id: str):
        super().__init__(f"Game {game_id} is full")


class NoActiveSessionException(UserException):
    def __init__(self):
        super().__init__("No active session found")


class NotEnoughPlayersException(UserException):
    def __init__(self, game_id: str):
        super().__init__(f"Not enough players in the game with ID: {game_id}")
