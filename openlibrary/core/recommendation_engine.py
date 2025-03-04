# openlibrary/core/recommendation_engine.py

import requests
import web
from openlibrary.core.bookshelves import Bookshelves
   
def get_authors_from_user_reading_history(user_id):
    """
    The comments were AI generated.

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
    author_keys = set()  # Using a set to avoid duplicates

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

        for work in logged_books.docs:
            work_key = work.get("key")
            if not work_key:
                continue

            # Query Open Library's Solr search to fetch work_key
            solr_url = f"http://localhost:8080/search.json?q=books/{work_key}"
            response = requests.get(solr_url)

            if response.status_code == 200:
                solr_data = response.json()
                docs = solr_data.get("docs", [])

                for doc in docs:
                    author_key_list = doc.get("author_key", [])
                    for author_key in author_key_list:
                        author_keys.add(author_key)  # Add unique author keys
            else:
                print(f"Failed to fetch data for {work_key}")

    return list(author_keys)  # Convert set back to list for final return

def get_books_in_user_shelves(user_id):
    """
    Fetches all books from the user's 'Want to Read', 'Currently Reading',
    and 'Already Read' shelves.

    Returns a set of work keys representing the books in the user's shelves.
    """
    user = web.ctx.site.get(f'/people/{user_id}')
    if not user:
        return set()

    shelves = ['Want to Read', 'Currently Reading', 'Already Read']
    user_books = set()

    for shelf in shelves:
        shelf_id = Bookshelves.PRESET_BOOKSHELVES.get(shelf)
        if not shelf_id:
            continue

        logged_books = Bookshelves.get_users_logged_books(
            user.get_username(),
            bookshelf_id=shelf_id,
            page=1,
            limit=1000,
            sort="created desc"
        )

        for work in logged_books.docs:
            work_key = work.get("key")
            if work_key:
                user_books.add(work_key)

    return user_books

def get_subjects(user_id):
    """
    The comments were genrated by AI
    Fetches the user's reading history by aggregating logged books
    from the 'Want to Read', 'Currently Reading', and 'Already Read' shelves.
    
    Returns a set of subjects that represent the user's reading history.
    """
    # Get the user object from the site
    user = web.ctx.site.get(f'/people/{user_id}')
    if not user:
        return set()

    # The shelves to include in the reading history
    shelves = ['Want to Read', 'Currently Reading', 'Already Read']
    subject_keys = set()  # Using a set to avoid duplicates

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

        for work in logged_books.docs:
            work_key = work.get("key")
            if not work_key:
                continue

            # Query Open Library's Solr search to fetch subjects for the work_key
            solr_url = f"http://localhost:8080/search.json?q=/{work_key}&fields=subject"
            response = requests.get(solr_url)

            try:
                # Ensure the response is not empty and is in JSON format
                if response.status_code == 200 and response.content.strip():
                    data = response.json()
                    # Initialize subject_keys as an empty set
                    subject_keys = set()
                    # Extract subjects if available
                    if 'docs' in data and isinstance(data['docs'], list):
                        for doc in data['docs']:
                            subjects = doc.get('subject', [])

                            # This block of code lines 147-153 was generated by AI to fix subject etxraction from JSON
                            # Ensure subjects are hashable before adding to the set
                            if isinstance(subjects, list):
                                for subject in subjects:
                                    if isinstance(subject, str):
                                        subject_keys.add(subject.lower().replace(" ", "_"))
                            elif isinstance(subjects, str):
                                subject_keys.add(subjects.lower().replace(" ", "_"))

            except json.JSONDecodeError:
                print(f"JSON decoding failed for work_key '{work_key}' ")

    return subject_keys

    
def new_recommendations(user_id):
    """
    The comments were generated by AI.

    Fetches recommendations based on a predefined list of authors.

    Returns a list of work keys as strings that represent recommended works.
    """
    user_books = get_books_in_user_shelves(user_id)
    author_list = get_authors_from_user_reading_history(user_id)
    subject_list = get_subjects(user_id)


    recommendations = set()

    for author_id in author_list:
        author_works_url = f'http://localhost:8080/authors/{author_id}/works.json'
        response = requests.get(author_works_url)
        if response.status_code == 200:
            works_data = response.json()
            for work in works_data.get('entries', []):
                work_key = work.get('key')
                if work_key and work_key not in user_books:
                    recommendations.add(work_key)
        else:
            print(f"Failed to fetch works for author {author_id}")
    
    for subject in subject_list:
        subject_url = f'http://localhost:8080/subjects/{subject}.json'
        response = requests.get(subject_url)
        if response.status_code == 200:
            works_data = response.json()
            for work in works_data.get('works', []):
                work_key = work.get('key')
                if work_key and work_key not in user_books:
                    recommendations.add(work_key)
        else:
            print(f"Failed to fetch works for subject {subject}") 
    
    return list(recommendations)

def get_recommendations(user_id):
    """
    The code and comments were genereted by AI 

    Fetches recommendations for a user and retrieves book details.
    """
    work_keys = new_recommendations(user_id) # Ensure it's always a list
    #todo
    #subject_keys = get_books_subjects(user_id)
    # merge work_keys and subjecct_keys?

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