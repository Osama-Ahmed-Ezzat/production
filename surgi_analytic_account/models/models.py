from odoo import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson",)
    salesteam_id = fields.Many2one(comodel_name="crm.team", string="Sales Team",)
    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line",)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_id = fields.Many2one(comodel_name="product.lines", string="Product Line",)

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_check = fields.Boolean(string="Check",  )

    # @api.onchange('is_check')
    def compute_analytic_account(self):

        analytic_account_obj=self.env['account.analytic.account'].search([('user_id','=',self.invoice_user_id.id)])

        for line in self.invoice_line_ids:
            print("11111111111111111111111111111111")
            if analytic_account_obj:
                for rec in analytic_account_obj:
                    print("2222222222222222222222222222222222222")
                    if line.product_id.product_id==rec.product_id:
                        print("33333333333333333333333333333")
                        line.analytic_account_id=rec.id
                        self.is_check=True

                    elif line.product_id.product_id==rec.product_id:
                        line.analytic_account_id =False
                        self.is_check = False
            else:
                line.analytic_account_id = False
                self.is_check = False



