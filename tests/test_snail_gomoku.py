from snail_gomoku import __version__
from snail_gomoku.gomoku_game import GameConfig, new_game, _has_five

def test_version():
    assert __version__ == '0.1.0'


def test_has_five():
    conf1 = GameConfig(15)
    g1 = new_game(conf1)
    assert not _has_five(g1.data[0])

    g1.data[0, 0, 0] = 1
    g1.data[0, 0, 1] = 1
    g1.data[0, 0, 2] = 1
    g1.data[0, 0, 3] = 1
    g1.data[0, 0, 4] = 1

    assert _has_five(g1.data[0])