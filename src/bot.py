from time import sleep

from src.db_handler import BotDB
from src.forum_scraper import ForumScraper
from src.modal_cli import receive_data
from src.secret import URL, COOKIE, LOGGING_ENABLED, MAX_HISTORY
from src.utils import get_last_answered, is_newer_than_x_minutes, format_reply


def first_run(production=True):
    db = BotDB("bot_db.json" if production else "test_db.json")
    fs = ForumScraper(URL, COOKIE, production)
    alerts = fs.get_alerts()
    if alerts:
        db.set_last_mention(alerts[-1]["id"])


def main(production=True):
    db = BotDB("bot_db.json" if production else "test_db.json")
    try:
        fs = ForumScraper(URL, COOKIE, production)
        bot_name = fs.my_name

        last_mention = db.get_last_mention()
        new_alerts = get_last_answered(last_mention, fs.get_alerts())
        if new_alerts and LOGGING_ENABLED:
            print(new_alerts)

        for alert in new_alerts:
            alert_type, alert_id = alert.values()
            author, author_name, timestamp, thread, quote, text = fs.get_post(alert_id)
            text = text.replace(f"@{bot_name}", "").strip()
            quote = quote.replace(f"@{bot_name}", "").strip()

            if not any([quote, text]):
                continue

            p_format = text if alert_type == "quoted" else f"{quote}\n{text}"
            # print(p_format)

            user_history = db.get_user(author)

            if user_history:
                user, history, db_timestamp = user_history

                if alert_type == "quoted" and \
                        is_newer_than_x_minutes(db_timestamp) and \
                        len(history) <= MAX_HISTORY:
                    # prepare response with history update history.
                    response = receive_data(p_format, history)
                    db.update_history(author, response, timestamp)
                else:
                    # else prepare response and erase/replace history.
                    response = receive_data(p_format)
                    db.update_history(author, response, timestamp, erase=True)
                # reply
                fs.reply(thread, format_reply(author_name, alert_id, author, text, response[1]))
                # print(thread, format_reply(author_name, alert_id, author, text, response[1]))

            else:
                # reply without history if user not exists in db.
                response = receive_data(p_format)
                db.add_user(author, response, timestamp)
                fs.reply(thread, format_reply(author_name, alert_id, author, text, response[1]))
                # print(thread, format_reply(author_name, alert_id, author, text, response[1]))

            db.set_last_mention(alert_id)
            sleep(20)

    except Exception:
        raise
