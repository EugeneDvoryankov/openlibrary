import pytest
from openlibrary.core.recommendation_engine import get_recommendations

def test_get_recommendations_returns_user_history(monkeypatch):
    # Dummy data to simulate a user's reading history.
    dummy_reading_history = ['OL100M', 'OL200M', 'OL300M']

    # A mock function that simulates fetching a user's reading history.
    def mock_get_user_reading_history(user_id):
        assert user_id == 'test_user'
        return dummy_reading_history

    # Monkey-patch the function in recommendation engine that should fetch user data.
    monkeypatch.setattr(
        'openlibrary.core.recommendation_engine.get_user_reading_history',
        mock_get_user_reading_history
    )

    # Now, when get_recommendations is called, it should internally call my mock.
    recs = get_recommendations('test_user')

    # For this test, I assume that the simplest behavior is to return the user's reading history.
    assert recs == dummy_reading_history
