from flask_mail import Mail, Message

def send_reward_email(receiver, sender):
    msg = Message( 'Congrats! Reward Recieved', sender='noreply@cerner.com', recipients=[receiver.email] )
    msg.body = f'''You have recieved appreciation/reward. Please visit the below link for details:


'''+ sender
    mail.send(msg)