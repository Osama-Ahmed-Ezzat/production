# -*- encoding: utf-8 -*-
##############################################################################
#
#    Openies Dynamic List Module for Odoo
#    Copyright (C) 2016 Openies Services(http://www.openies.com).
#    @author Openies Services <contact@openies.com>
#
#    It is forbidden to publish, distribute, sublicense,
#    or sell copies of the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.


#
##############################################################################
from openerp import models, fields, api


class THView(models.Model):

    _name = "th.fields"
    _description = "TH Fields"

    view_id = fields.Many2one("ir.ui.view", "View")
    th_list_text = fields.Text("TH List")
    user_id = fields.Many2one("res.users", 'User')

    @api.model
    def has_access(self):
        if self.env.user.has_group('th_dynamic_list.group_dynamic_list'):
            return True
        return False
