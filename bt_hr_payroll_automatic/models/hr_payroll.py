# -*- coding: utf-8 -*-
###############################################################################
#
#    BroadTech IT Solutions Pvt Ltd
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
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

from odoo import api, fields, models,tools, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    @api.model
    def _cron_generate_batches_generate_payslips(self):
        payslip_employee_pool = self.env['hr.payslip.employees']
        if self.env['account.journal'].search([('type', '=', 'general')]):
            today = datetime.today()
            start_date = datetime(today.year, today.month, 1)
            if today.month == 12:
                next_month = 1
                year = today.year + 1
            else:
                next_month = today.month + 1
                year = today.year
            next_month_start_day = datetime(year, next_month, 1)
            end_date = next_month_start_day - relativedelta(days=1)
            batch_name = 'Payslip Batch for ' + calendar.month_name[today.month] + ' - ' + str(today.year)
            payslip_batch_vals = {
                'date_start': start_date,
                'date_end': end_date,
                'name': batch_name
                }
            payslip_batch = self.create(payslip_batch_vals)
            employee_objs = self.env['hr.employee'].search([])
            employee_ids = []
            for employee in employee_objs:
                employee_ids.append(employee.id)
            ctx = dict(self.env.context) or {}
            ctx.update({
                'active_model': 'hr.payslip.run', 
                'journal_id': payslip_batch.journal_id and payslip_batch.journal_id.id,
                'active_ids': [payslip_batch.id],
                'active_id': payslip_batch.id
                })
            payslip_employee_obj = payslip_employee_pool.with_context(ctx).create({'employee_ids': [(6, 0, employee_ids)]})
            payslip_employee_obj.compute_sheet()
        
    def action_send_payslips(self):
        self.ensure_one()
        template = self.env.ref('bt_hr_payroll_automatic.payslip_mail_template', False)
        ctx = dict(self.env.context) or {}
        for payslip in self.slip_ids:
            email_to = ''
            if payslip.employee_id.work_email:
                email_to = payslip.employee_id.work_email
            elif payslip.employee_id.user_id and payslip.employee_id.user_id.partner_id and payslip.employee_id.user_id.partner_id.email:
                email_to = payslip.employee_id.user_id.partner_id.email
            if email_to:
                start_date = payslip.date_from
                start_date = datetime.strptime(str(payslip.date_from), DF).date()
                start_date_format = start_date.strftime("%m/%d/%Y")
                end_date = datetime.strptime(str(payslip.date_to), DF).date()
                end_date_format = end_date.strftime("%m/%d/%Y")
                ctx.update({'email_to': email_to, 'start_date': start_date_format, 'end_date': end_date_format})
                template.with_context(ctx).send_mail(payslip.id, force_send=True, raise_exception=True)
        

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

