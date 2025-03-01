# openlibrary/core/recommendation_engine.py

import requests
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

def new_recommendations(user_id):
    """
    Fetches recommendations based on a predefined list of authors.

    Returns a list of work keys as strings that represent recommended works.
    """
    author_list = ['OL22098A']  # List of author IDs
    recommendations = []

    for author_id in author_list:
        # Fetch works by the author
        author_works_url = f'http://localhost:8080/authors/{author_id}/works.json'
        response = requests.get(author_works_url)
        if response.status_code == 200:
            works_data = response.json()
            for work in works_data.get('entries', []):
                work_key = work.get('key')
                if work_key:
                    recommendations.append(work_key)
        else:
            print(f"Failed to fetch works for author {author_id}")

    return recommendations

def get_recommendations(user_id):
    """
    Fetches recommendations for a user and retrieves book details.
    """
    work_keys = new_recommendations(user_id) # Ensure it's always a list
    recommendations = []

    for key in work_keys:
        work = web.ctx.site.get(key)
        if not work:
            continue  # Skip if metadata retrieval fails

        # Safe extraction of author name
        author_keys = [a.author.key for a in work.get('authors', [])]

        # Safe extraction of cover
        covers = work.get('covers', [])
        cover = covers[0] if covers else None

        # Extract work ID safely
        work_id = key.split('/')[-1] if key else "Unknown"

        recommendations.append({
            "key": key,
            "title": work.get('title', 'Unknown Title'),
            "author": [a.name for a in web.ctx.site.get_many(author_keys)],
            "cover": cover,
            "work_id": work_id,
        })

    return recommendations

"""
def get_recommendations(user_id):   
    #Fetches recommendations based on the most logged books instead of only the user's reading history.
    # Get the most logged books (popular books among all users)
    most_logged = Bookshelves.most_logged_books(limit=10, sort_by_count=True, fetch=True)

    recommendations = []

    for book in most_logged:
        work_id = book.get('work_id')
        key = f"/works/OL{work_id}W"
        work = web.ctx.site.get(key)

        if not work:
            continue  

        # Safe extraction of author name
        author_keys = [a.author.key for a in work.get('authors', [])]

        # Safe extraction of cover
        covers = work.get('covers', [])
        cover = covers[0] if covers else None

        recommendations.append({
            "key": key,
            "title": work.get('title', 'Unknown Title'),
            "author": [a.name for a in web.ctx.site.get_many(author_keys)],
            "cover": cover,
            "work_id": work_id,
        })

    return recommendations
"""