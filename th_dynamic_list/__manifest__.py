# -*- coding: utf-8 -*-
# Part of Heliconia Solutions Pvt. Ltd. See LICENSE file for copyright and licensing details.
{
    'name': 'Dynamic List',
    'version': '12.0.1.1.0',
    'author': "Heliconia Solutions Pvt. Ltd.",
    'category': 'Tools',
    'website': 'https://tech.heliconia.in/',
    # 'live_test_url':'http://bit.ly/2OWb5nZ',
    'summary': 'Arrange any List view on the fly for odoo v12',
    'description': """
        Arrange any List view on the fly without any technical knowledge.
    """,
    'depends': ['web'],
    'price': 111.00,
    'currency': 'EUR',
    'license': 'OPL-1',
    'data': [
        "security/ir.model.access.csv",
        "security/groups.xml",
        'views/dynamic_list_view.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/dynamic_list.xml'],
    'images': ['static/description/th_dynamic_list_banner.png'],
}