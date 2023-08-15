class PlayerAlreadyInGameException(Exception):
    ...


class PlayerNotInGameException(Exception):
    ...


class GameNotFoundException(Exception):
    ...


class GameFullException(Exception):
    ...


class NoActiveSessionException(Exception):
    ...


class NotEnoughPlayersException(Exception):
    ...
