from app.db import get_connection
from datetime import datetime

def get_or_create_conversation(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Try to find existing private chat with these 2 users
    query = """
        SELECT cp1.conversation_id
        FROM conversation_participants cp1
        JOIN conversation_participants cp2 ON cp1.conversation_id = cp2.conversation_id
        JOIN conversations c ON c.conversation_id = cp1.conversation_id
        WHERE cp1.user_id = %s AND cp2.user_id = %s AND c.is_group = 0
        LIMIT 1
    """
    cursor.execute(query, (user1_id, user2_id))
    result = cursor.fetchone()

    if result:
        cursor.close()
        conn.close()
        return result[0]

    # Create new conversation (private chat)
    insert_convo = """
        INSERT INTO conversations (room_name, is_group) VALUES (%s, 0)
    """
    cursor.execute(insert_convo, (f"chat_{user1_id}_{user2_id}",))
    conversation_id = cursor.lastrowid

    # Add both users to conversation_participants
    insert_participants = """
        INSERT INTO conversation_participants (conversation_id, user_id) VALUES (%s, %s), (%s, %s)
    """
    cursor.execute(insert_participants, (conversation_id, user1_id, conversation_id, user2_id))
    conn.commit()

    cursor.close()
    conn.close()
    return conversation_id

def create_message(data):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO messages (
            conversation_id,
            sender_id,
            receiver_id,
            message,  -- ✅ FIXED
            status,
            timestamp,
            message_type,
            is_private_message
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        data["conversation_id"],
        data["sender_id"],
        data["receiver_id"],
        data["content"],  # still named content in code, but maps to DB 'message'
        data.get("status", "sent"),
        datetime.now(),
        "chat",
        0
    )
    cursor.execute(query, values)
    conn.commit()
    message_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return message_id


def update_message_status(message_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE messages SET status = %s WHERE message_id = %s"
    cursor.execute(query, (status, message_id))
    conn.commit()
    cursor.close()
    conn.close()



def mark_message_seen(message_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE messages SET status = 'seen' WHERE message_id = %s"
    cursor.execute(query, (message_id,))
    conn.commit()
    cursor.close()
    conn.close()
