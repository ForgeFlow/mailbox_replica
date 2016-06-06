{
    'name' : 'Mail keep recipients',
    'version' : '1.0.0',
    'author' : 'Eficent',
    'category' : 'Social Network',
    'website' : 'www.eficent.com',
    'description': """
Allows to store recipients of the mail. When they are being sent. If the
send process fails, after re-trying to send the recipients will be included
in the notification again.
    """,
    'depends' : ['mail'],
    'data':[
        'views/mail_mail_view.xml',
    ],
    'installable': True
}
