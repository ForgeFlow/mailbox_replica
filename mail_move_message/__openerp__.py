{
    'name' : 'Mail relocation',
    'version' : '1.0.2',
    'author' : 'IT-Projects LLC, Ivan Yelizariev',
    'category' : 'Social Network',
    'website' : 'https://yelizariev.github.io',
    'depends' : ['mail', 'web_polymorphic_selection'],
    'images': ['images/inbox.png'],
    'data':[
        'mail_move_message_views.xml',
        'data/mail_move_message_data.xml',
        ],
    'js': [
        'static/src/js/mail_move_message.js',
    ],
    'css': [
        'static/src/css/mail_move_message.css',
    ],
    'qweb': [
        'static/src/xml/mail_move_message_main.xml',
    ],
    'installable': True
}
