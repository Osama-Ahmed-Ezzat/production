from collections import OrderedDict
from pprint import pprint

from odoo import api, fields, models


class product_compination_template_group_surgi(models.Model):
    _name = 'product.compination.groups.surgi'
    _description = 'make relation between compination and the groups in the product_template'

    def get_groups(self):
        self._cr.execute("select product_group from product_template where product_group!= '' group by product_group")
        groups = self._cr.fetchall()
        groupdata = []
        for rec in groups:
            x = rec[0]
            x
            groupdata.append((str(rec[0]), str(rec[0])))
            pass
        return groupdata

    pass

    product_group = fields.Selection(get_groups, string="Group name")
    # product_group = fields.Selection([("1","1"),("2","2")], string="Group name")
    product_quantity = fields.Float(string="Quantity")
    product_compination_id = fields.Many2one('product.compination.surgi')
    default_product = fields.Many2one('product.product', string="Default Product")
    pass


# class product_compination_relation(models.Model):
#     _description = "Make Relation With Products table"
#     _inherit = "product.product"
#     compinations_id=fields.Many2one("product.compination.surgi")

class product_compination_surgi(models.Model):
    _name = 'product.compination.surgi'
    _description = "Create product from other products"

    def get_products(self):
        return self.env['product.product'].search([])

    name = fields.Char(string="Title", required=True)
    priority = fields.Integer("Priority")
    main_product = fields.Many2one('product.template', string="Default Product")
    group_ids = fields.One2many('product.compination.groups.surgi', string="Products Group",
                                inverse_name="product_compination_id")

    move_id = fields.Many2one('product.compination.movement.surgi')
    pass


class product_compination_account_move_surgi(models.Model):
    _name = 'product.compination.movement.surgi'
    _description = 'insert data that will got from invoice page'
    # _inherits = {'account.move': 'move_id'}
    # comination_id=fields.One2many('product.compination.surgi',inverse_name='move_id')
    compunation_count = fields.Integer(string="Quantity")
    compunation_name = fields.Char(string="Name")
    compination_move = fields.Many2one("account.move")
    compination_main_product=fields.Char(string="Product")


class product_items_move_surgi(models.Model):
    _name = 'product.item.movement.surgi'
    _description = 'the items that will not have compunation will be listed here'
    _inherits = {'account.move': 'move_id'}
    # product_template_id=fields.One2many('product.product')
    product_count = fields.Integer(string="Quantity")
    product_name = fields.Char(string="Name")
    move_id = fields.Many2one("account.move", readonly='false')


class account_move(models.Model):
    _inherit = 'account.move'
    cominations_id = fields.One2many("product.compination.movement.surgi", string="Compinations",
                                     inverse_name="compination_move")
    items_move_id = fields.One2many('product.item.movement.surgi', string="Products", inverse_name="move_id")

    # @api.onchange('invoice_line_ids')
    def changed_line_ids(self):
        products = {} # will hold products and there quantities
        groups = [] # will hold groups found in those products
        for rec in self:
            moveid = rec.ids[0]# the current move id
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    if line.pro_group != '' and line.pro_group != 'unknown':#check if the product have group
                        if line.pro_group in products.keys():
                            products[line.pro_group]['totalq'] += line.quantity
                        else:
                            groups.append(line.pro_group)
                            products[line.pro_group] = {
                                'totalq': line.quantity,
                                'products': line.product_id.id,
                                'pro_name':line.product_id.name
                            }
                    else: # in not have group
                        if line.product_id.name in products.keys():
                            products[line.product_id.name]['totalq'] += line.quantity
                        else:
                            groups.append(line.product_id.name)
                            products[line.product_id.name] = {
                                'totalq': line.quantity,
                                'products': line.product_id.id,
                                'pro_name': line.product_id.name
                            }

                    pass

                compinations = self.env['product.compination.groups.surgi'].search([('product_group', 'in', groups)]) #check which compination is exist in the products

                compions = {}

                for v in compinations:

                    self._cr.execute(
                        "select product_group from product_compination_groups_surgi where product_compination_id=%d" % v.product_compination_id.id)
                    current = self._cr.fetchall()
                    co = {}
                    for c in current:
                        co[c[0]] = 1

                    if co.keys() <= products.keys():
                        if v.product_compination_id.id in compions.keys():
                            compions[v.product_compination_id.id]['groups'].update({
                                v.product_group: {'group': v.product_group,
                                                  'quantity': v.product_quantity,
                                                  }})

                        else:
                            compions[v.product_compination_id.id] = \
                                {
                                    'id': v.product_compination_id.id,
                                    'name': v.product_compination_id.name,
                                    'priority': v.product_compination_id.priority,
                                    'mainproduct':v.product_compination_id.main_product.name,
                                    'groups': {
                                        v.product_group: {'group': v.product_group,
                                                          'quantity': v.product_quantity,
                                                          }

                                    },
                                    'q': 0
                                }

                    pass
                res = sorted(compions.items(), key=lambda x: x[1]['priority']) #order compinations
                products2 = products.copy() # make copy of products
                for comp in res:
                    accepted = True
                    itemsno = -1
                    for k in comp[1]['groups']:
                        if k != False:
                            if products[k]['totalq'] < comp[1]['groups'][k]['quantity']:
                                accepted = False
                                break
                            else:
                                cx = int(products[k]['totalq'] / comp[1]['groups'][k]['quantity'])
                                if itemsno == -1 or itemsno > cx:
                                    itemsno = cx

                    if accepted:
                        for k in comp[1]['groups']:
                            q1 = comp[1]['groups'][k]['quantity'] * itemsno
                            products[k]['totalq'] -= q1
                            pass
                    comp[1]['q'] = itemsno

                res
                print(products)
                # compinations_items = [(5,)]
                compinations_items = []
                self._cr.execute("delete from product_compination_movement_surgi where compination_move =%d" % moveid)
                for r in res:
                    if r[1]['q'] > 0:
                        self.env["product.compination.movement.surgi"].create(
                            {
                                'compunation_count': r[1]['q'],
                                'compunation_name': r[1]['name'],
                                'compination_move': moveid,
                                'compination_main_product':r[1]['mainproduct']
                            }
                        )

                self._cr.execute("delete from product_item_movement_surgi where move_id =%d" % moveid)
                for p in products:
                    if products[p]['totalq'] > 0:
                        print(p)
                        self._cr.execute(
                            'insert into product_item_movement_surgi  (product_count,move_id,product_name) values (%d,%d,%s)  ' % (
                                products[p]['totalq'], moveid, "'" + str(products[p]['pro_name']) + "'"))

        pass

    def create_compined(self, data):
        lines = self.invoice_line_ids
        products = {}
        for p in data['line_ids']:
            x = p
            if p[2]['product_id']:
                self._cr.execute(
                    "select product_template.product_group from product_product join product_template on product_product.product_tmpl_id=product_template.id where product_product.id=%d" %
                    p[2]['product_id'])
                product_group = self._cr.fetchall()
                if product_group[0][0] in products:
                    products[product_group[0][0]]['totalq'] += p[2]['quantity']
                    if products[product_group[0][0]]['products'][0] == p[2]['product_id']:
                        products[product_group[0][0]]['products'][0] += p[2]['quantity']
                    else:
                        products[product_group[0][0]]['products'].append(p[2]['product_id'], p[2]['quantity'])

                else:
                    products[product_group[0][0]] = {
                        'totalq': p[2]['quantity'],
                        'products': [
                            p[2]['product_id'], p[2]['quantity']
                        ]
                    }
                pass
            pass
        compinations = self.env['product.compination.surgi'].search([])
        compion = []

        for v in compinations:
            compion.append({
                'id': v.id,
                'name': v.name,
                'priority': v.priority,
                'groups': self.get_groups(v.group_ids)
            })

        print("f")

        # need=[d for d in products[1] if d['product_id'] != False]
        print("1")
        pass

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(account_move, self).create(vals_list)
    #     self.changed_line_ids()
    #     return res
    #     pass
    #
    # @api.model
    # def action_post(self, values):
    #     record = super(account_move, self).create(values)
    #     print(values)
    #     self.changed_line_ids()
    #     print("ff")
    #     return record
    #     pass
    #
    # # @api.model
    # def write(self, vals):
    #     res = super(account_move, self).write(vals)
    #     self.changed_line_ids()
    #     return res
    #     pass


class account_move_line_inhert(models.Model):
    _name = "account.move.line"
    _inherit = "account.move.line"
    pro_group = fields.Char(string="my new Group", related="product_id.product_tmpl_id.product_group")

    def get_compined(self):
        self.compined_products = self.pro_group
        pass

    compined_products = fields.Char(compute='get_compined')
    # groupx=fields.Char(string="My new group",related='pro_tem.product_group')
    pass
