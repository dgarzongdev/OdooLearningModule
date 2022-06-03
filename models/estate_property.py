from odoo import fields, models
from copy import copy
from email.policy import default
from hashlib import new
from os import unlink
from pkg_resources import require
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class PropertyModel(models.Model):
    _name = "estate.property"
    _description = "Test Model"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    # The default availability date is in 3 months
    date_availability = fields.Date(date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(
        readonly=True,
        copy=False,
        compute="_enable_offer"
    )
    # The default number of bedrooms is 2
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[('north', 'North'), ('south', 'South'),
                   ('east', 'East'), ('west', 'West')],
        help="List of tuples"
    )
    # This field allows de visualization of the data in the interface
    # active= fields.Boolean(True)
    state = fields.Selection(
        string='Type',
        selection=[
            ('new', 'New'),
            ('offer', 'Offer'),
            ('received', 'Received'),
            ('accepted', 'Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        help="List of tuples",
        default='new'
    )

    buyer = fields.Char(string="Buyer", copy=False)
    property_type_id = fields.Many2one("property.type", string="Property Type")
    sales_person_id = fields.Many2one(
        "res.users", index=True, tracking=True, default=lambda self: self.env.user)
    tag_ids = fields.Many2many("property.tag", string="Tag")
    offer_ids = fields.One2many(
        "property.offer", "property_id", string="Offers")

    total_area = fields.Float(compute="_compute_total")

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    best_offer = fields.Float(compute="_best_offer", store=True)

    @api.depends("offer_ids.price")
    def _best_offer(self):
        for record in self:
            if len(record.offer_ids.mapped('price')) != 0:
                # prices = record.offer_ids.mapped('price')
                # record.best_offer = max(prices)
                record.best_offer = max(record.offer_ids.mapped('price'))
            else:
                record.best_offer = 0

    @api.onchange("garden", "garden_area", "garden_orientation")
    def _garden_checked(self):
        if self.garden:
            self.garden_area = 100
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def set_sold(self):
        if self.state == "canceled":
            # return {
            #     'effect': {
            #         'fadeout': 'slow',
            #         'message': 'A canceled property cannot be set as sold'
            #     }
            # }
            raise AccessError("A canceled property cannot be set as sold.")
        else:
            for record in self:
                record.state = "sold"

    def set_canceled(self):
        if self.state == "sold":
            # return {
            #     'effect': {
            #         'fadeout': 'slow',
            #         'message': 'A sold property cannot be set as canceled'
            #     }
            # }
            raise AccessError("A sold property cannot be set as canceled")
        else:
            for record in self:
                record.state = "canceled"
            return True

    buyer = fields.Char(default="")

    @api.depends("offer_ids.price")
    def _enable_offer(self):
        for record in self:
            if len(record.offer_ids.mapped('status')) != 0:
                aux = 0
                for offer in record.offer_ids:
                    if offer.status == 'acepted':
                        aux = offer.price
                        record.buyer = offer.partner_id.name
                    else:
                        record.selling_price = 0
                record.selling_price = aux
            else:
                record.selling_price = 0

    _sql_constraints = [
        ('check_price', 'CHECK(expected_price >= 0)',
         'The price should be positive.'), ('check_selling_price', 'CHECK(selling_price >= 0)',
         'The price should be positive.'),
    ]

    # Prevent deletion of a property if its state is not ‘New’ or ‘Canceled’
    # @api.model
    # def ondelete(self, state):
    #     if state not in ['new', 'canceled']:
    #         raise ValidationError("This property cannot be deleted")


class InheritedModel(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "sales_person_id", string="Offers")