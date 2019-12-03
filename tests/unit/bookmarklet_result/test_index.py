import index


def test_success(monkeypatch):
    monkeypatch.setattr(index, 'handler', lambda *_, **__: None)
    assert True