# openlibrary/views/recommendations.py

from openlibrary.core.recommendation_engine import get_recommendations

class Recommendations:
    def GET(self):
        # Use a dummy user ID for now
        user__id = "dummy_user"
        recs = get_recommendations(user_id)

        # Reeturn a simple text response (I will switch to a template later)
        return "Your recommendations: "