from datetime import datetime, timedelta


def get_last_answered(last_answered: str, list_of_posts: list) -> list:
    item_index = next((i for i, d in enumerate(list_of_posts) if d["id"] == last_answered), None)
    if item_index is None:
        return list_of_posts
    return list_of_posts[item_index + 1:]


def is_newer_than_x_minutes(timestamp: str, minutes=10) -> bool:
    dt = datetime.fromtimestamp(int(timestamp))
    now = datetime.now()
    diff = now - dt
    return diff <= timedelta(minutes=minutes)


def format_reply(user, post_id, member_id, text, response):
    return f'[QUOTE="{user}, post: {post_id}, member: {member_id}"]\n{text}[/QUOTE]\n{response}'
