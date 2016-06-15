{
    'name' : 'Mail create partner',
    'version' : '7.0.1.0.0',
    'author' : 'Eficent Business and IT Consulting Services S.L.',
    'category' : 'Social Network',
    'website' : 'http://www.eficent.com',
    'depends' : ['mail'],
    'data':[
        'views/mail_create_partner_view.xml',
        'views/mail_create_partner_assets.xml',
        ],
    'js': [
        'static/src/js/mail_create_partner.js',
    ],
    'css': [
        'static/src/css/mail_create_partner.css',
    ],
    'qweb': [
        'static/src/xml/mail_create_partner_main.xml',
    ],
    'installable': True
}
