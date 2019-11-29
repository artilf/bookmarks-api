import pytest


@pytest.fixture(scope='function', autouse=True)
def global_environment(monkeypatch):
    environments = {
        'AWS_ENV': 'production',
        'BOOKMARKS_USER_ID': 'C345859B-0C0F-45FA-AFF9-C480E34F0F36'
    }
    for k, v in environments.items():
        monkeypatch.setenv(k, v)
