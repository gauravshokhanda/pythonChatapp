from fastapi import APIRouter, HTTPException
from app.db import get_connection

router = APIRouter()

@router.get("/partners/{user_id}", tags=["Chat"])
def get_chat_partners(user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT DISTINCT u.user_id, u.username, u.email
    FROM users u
    JOIN messages m ON (u.user_id = m.sender_id OR u.user_id = m.receiver_id)
    WHERE (m.sender_id = %s OR m.receiver_id = %s)
    AND u.user_id != %s
    """
    cursor.execute(query, (user_id, user_id, user_id))
    partners = cursor.fetchall()

    cursor.close()
    conn.close()
    return partners

@router.get("/conversation/{user1_id}/{user2_id}", tags=["Chat"])
def get_conversation(user1_id: int, user2_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
       OR (sender_id = %s AND receiver_id = %s)
    ORDER BY timestamp ASC
    """
    cursor.execute(query, (user1_id, user2_id, user2_id, user1_id))
    messages = cursor.fetchall()

    cursor.close()
    conn.close()
    return messages
