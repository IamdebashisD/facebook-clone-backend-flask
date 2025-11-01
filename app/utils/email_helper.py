def send_welcome_message(user_email: str, user_name: str):
    from flask_mail import Message
    from app import mail    # lazy import inside the function
    
    msg = Message(
        subject= "welcoem to Our App!",
        recipients= [user_email],
        body= f"Hi {user_name},\n\nWelcome to our app! We're glad to have you 🎉"
    )
    mail.send(msg)