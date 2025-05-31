async def handle_chat(body):
    user_input = body.get("text", "")
    return {"reply": f"You said: {user_input}"}
