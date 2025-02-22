# openlibrary/core/recommendation_engine.py

import web

def get_user_reading_history(user_id):
    """
    Fetches the user's reading history.
    For now, return a dummy list.
    """
    # Dummy reading history (ensure these are strings)
    return ["/books/OL100M", "/books/OL200M", "/books/OL300M"]

def get_empty_user_reading_history(user_id):
    """
    For now, return a dummy list.
    """
    return []

def get_recommendations(user_id):
    """
    Return the user's reading history as recommendations.
    Ensure every element is a string.
    """
    recs = get_user_reading_history(user_id)
    # If any element might be a tuple, convert it to a string:
    return recs

def get_empty_recommendations(user_id):
    """
    Return the user's reading history as recommendations.
    Ensure every element is a string.
    """
    empty_recs = get_empty_user_reading_history(user_id)
    # If any element might be a tuple, convert it to a string:
    return empty_recs
