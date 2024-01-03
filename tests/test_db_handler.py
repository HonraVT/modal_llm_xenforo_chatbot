import unittest
from src.db_handler import BotDB

"""ChatGPT generated"""


class TestBotDB(unittest.TestCase):
    def setUp(self):
        self.db = BotDB(db_name="test_user_db.json")

    def tearDown(self):
        user = "test_user"

        self.db.delete_user(user)
        # Clean up any resources if needed after each test
        pass

    def test_add_user(self):
        user = "test_user"
        history = ["action1", "action2"]
        timestamp = "23423422342"

        self.db.add_user(user, history, timestamp)
        result = self.db.get_user(user)

        self.assertEqual(result[0], user)
        self.assertEqual(result[1], [history])
        self.assertEqual(result[2], timestamp)

    def test_update_history(self):
        user = "test_user"

        history1 = ["action1", "action2"]
        history2 = ["action3", "action4"]
        timestamp = "23423422342"

        self.db.add_user(user, history1, timestamp)
        self.db.update_history(user, history2, timestamp)
        result = self.db.get_user(user)

        self.assertIn(result[1], [history1, history2])

    def test_update_history_erase(self):
        user = "test_user"
        history = ["action5", "action6"]
        timestamp = "23423422342"

        self.db.add_user(user, ["action1", "action2"], timestamp)
        self.db.update_history(user, history, timestamp, erase=True)
        result = self.db.get_user(user)

        self.assertEqual(result[1], [history])
        self.assertEqual(result[2], timestamp)

    def test_delete_user(self):
        user = "test_user"
        history = ["action1", "action2"]
        timestamp = "23423422342"

        self.db.add_user(user, history, timestamp)
        self.db.delete_user(user)
        result = self.db.get_user(user)

        self.assertIsNone(result)

    def test_set_get_last_mention(self):
        post_id = "12345"

        self.db.set_last_mention(post_id)
        result = self.db.get_last_mention()

        self.assertEqual(result, post_id)


if __name__ == '__main__':
    unittest.main()
