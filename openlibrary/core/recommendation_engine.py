# openlibrary/core/recommendation_engine.py

import web
from openlibrary.core.bookshelves import Bookshelves

def get_user_reading_history(user_id):
    """
    Fetches the user's reading history by aggregating logged books
    from the 'Want to Read', 'Currently Reading', and 'Already Read' shelves.
    
    Returns a list of work or book keys as strings that represent the user's reading history.
    """
    # Get the user object from the site
    user = web.ctx.site.get(f'/people/{user_id}')
    if not user:
        return []

    # The shelves that will be included in the reading history.
    # These names  correspond to the ones in Bookshelves.PRESET_BOOKSHELVES mapping.
    shelves = ['Want to Read', 'Currently Reading', 'Already Read']
    history = []

    for shelf in shelves:
        shelf_id = Bookshelves.PRESET_BOOKSHELVES.get(shelf)
        if not shelf_id:
            continue

        # Fetch all logged books from this shelf
        logged_books = Bookshelves.get_users_logged_books(
            user.get_username(),
            bookshelf_id=shelf_id,
            page=1,
            limit=1000,
            sort="created desc"
        )

        # Append the key for each book in the reading history
        for work in logged_books.docs:
            key = work.get('key')
            if key:
                history.append(key)
    
    return history

def get_recommendations(user_id):
    """
    Fetches recommendations for a user and retrieves book details.
    """
    work_keys = get_user_reading_history(user_id) or []  # Ensure it's always a list
    recommendations = []

    for key in work_keys:
        work = web.ctx.site.get(key)
        if not work:
            continue  # Skip if metadata retrieval fails

        # Safe extraction of author name
        author_list = work.get('authors', [])
        author = author_list[0].get('name', 'Unknown Author') if author_list else 'Unknown Author'

        # Safe extraction of cover
        covers = work.get('covers', [])
        cover = covers[0] if covers else None

        # Extract work ID safely
        work_id = key.split('/')[-1] if key else "Unknown"

        recommendations.append({
            "key": key,
            "title": work.get('title', 'Unknown Title'),
            "author": author,
            "cover": cover,
            "work_id": work_id,
        })

    return recommendations