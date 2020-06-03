# -*- coding: utf-8 -*---------
###############################################################################
#
#    BroadTech IT Solutions Pvt Ltd
#    Copyright (C) 2020 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Automatic Payroll Generation',
    'version': '0.1',
    'category': 'Generic Modules/Human Resources',
    'license': 'LGPL-3',
    'summary': 'Automatic Payroll Generation',
    'description': """
      This module adds features for auto generating payslip batch for each month and sending payslips from payslip batches.
           """,
    'author' : 'BroadTech IT Solutions Pvt Ltd',
    'website' : 'http://www.broadtech-innovations.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['om_hr_payroll_account', 'mail'],
    'data': [
        'data/payroll_customization_data.xml',
        'views/hr_payroll_view.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
