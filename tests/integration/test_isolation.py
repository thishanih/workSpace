from pymongo.database import Database


def test_test_database_starts_without_existing_user_data(database: Database) -> None:
    assert database["users"].count_documents({}) == 0
    assert database["todos"].count_documents({}) == 0
    assert database["comments"].count_documents({}) == 0
    assert database["activities"].count_documents({}) == 0
    assert database["refresh_tokens"].count_documents({}) == 0
