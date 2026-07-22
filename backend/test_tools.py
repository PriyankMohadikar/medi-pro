import chat_services
from database import get_session_factory, get_engine
from config import load_settings

settings = load_settings()
engine = get_engine(settings)
SessionFactory = get_session_factory(engine)
db = SessionFactory()

try:
    print(chat_services.get_market_average(db, test_name="CBC"))
except Exception as e:
    print(f"Error: {e}")
