from odoo import fields, models, api, exceptions


class stock_quant_inherit_wizard(models.Model):
    _inherit = 'stock.quant'

    price_unit = fields.Float(string="Unit Price")
    u_p_usd = fields.Float(string="U. Price in USD")