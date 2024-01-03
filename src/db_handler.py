from tinydb import TinyDB, Query
from tinydb.operations import add


class BotDB:
    def __init__(self, db_name="user_db.json"):
        self.db = TinyDB(db_name)
        self.users_table = self.db.table("users")
        self.last_mention_table = self.db.table("last_mention")

        if not self.last_mention_table.contains(Query().post_id.exists()):
            self.last_mention_table.insert({"post_id": "0"})

    def add_user(self, user: str, history: list[str], timestamp: str) -> None:
        self.users_table.insert({"user": user, "history": [history], "timestamp": timestamp})

    def get_user(self, user: str) -> tuple[str, list[list[str]], str] | None:
        result = self.users_table.get(Query().user == user)
        if result:
            return result["user"], result["history"], result["timestamp"]
        return None

    def update_history(self, user: str, history: list[str], timestamp: str, erase: None | bool = False) -> None:
        query_user = Query().user == user
        if erase:
            self.users_table.update({"history": [history], "timestamp": timestamp}, query_user)
        else:
            self.users_table.update(add('history', [history]), query_user)

    def delete_user(self, user: str) -> None:
        self.users_table.remove(Query().user == user)

    def set_last_mention(self, post_id: str) -> None:
        self.last_mention_table.update({"post_id": post_id})

    def get_last_mention(self) -> str:
        last_mention = self.last_mention_table.get(Query().post_id.exists())
        return last_mention["post_id"]
