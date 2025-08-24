import socketio
from services.chat_service import save_message
from services.user_service import get_user_from_token

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print(f"Socket connected: {sid}")

@sio.on('join_room')
async def join_room(sid, data):
    room = data.get('trip_id')
    if room:
        # --- FIX IS HERE ---
        # You must await an asynchronous function call.
        await sio.enter_room(sid, room) 
        print(f"SID {sid} joined room {room}")

@sio.on('send_message')
async def send_message(sid, data):
    trip_id = data.get('trip_id')
    message_text = data.get('message')
    token = data.get('token')

    if not all([trip_id, message_text, token]):
        return

    user = await get_user_from_token(token)
    if not user:
        return
    
    user_id_str = str(user['_id'])
    saved_message = await save_message(trip_id, user_id_str, message_text)
    
    if saved_message:
        await sio.emit('receive_message', saved_message, room=trip_id)

@sio.event
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")