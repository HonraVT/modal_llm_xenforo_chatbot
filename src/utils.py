from datetime import datetime, timedelta


def get_last_answered(post_id: str, data: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted([item for item in data if int(item['post_id']) > int(post_id)], key=lambda x: int(x['post_id']))


def is_newer_than_x_minutes(timestamp: str, minutes=10) -> bool:
    dt = datetime.fromtimestamp(int(timestamp))
    now = datetime.now()
    diff = now - dt
    return diff <= timedelta(minutes=minutes)


def format_reply(user, post_id, member_id, text, response):
    return f'[QUOTE="{user}, post: {post_id}, member: {member_id}"]\n{text}[/QUOTE]\n{response}'
