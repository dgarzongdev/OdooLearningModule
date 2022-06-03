from datetime import date
from odoo.exceptions import AccessError, ValidationError
from odoo import fields, models, api

class PropertyOffer(models.Model):
    _name = "property.offer"
    _description = "Property's Offer"
    _order = "price desc"

    price = fields.Float(required=True)
    status = fields.Selection(
        string='Status',
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        help="List of tuples",
        copy=False,
        default=''
    )

    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(related='property_id.property_type_id')


    validity = fields.Integer(default=7, required=True)
    date_deadline = fields.Date(inverse='_inverse_deadline', required=True)

    @api.depends("date_deadline", "validity")
    def _inverse_deadline(self):
        today = date.today()
        for record in self:
            if record.date_deadline:
                lead_date = fields.Date.from_string(record.date_deadline)
                if lead_date >= today:
                    record.validity = (record.date_deadline - today).days
                else:
                    record.date_deadline = today
                    record.validity = 0


    def set_acepted(self):
        if self.property_id.offer_ids.mapped('status').__contains__('acepted'):
            raise AccessError("Just one offer acepted please")
        else:
            self.status = 'acepted'

    def set_refused(self):
        self.status = 'refused'
        self.property_id.buyer = ''

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)','The price should be positive.')
    ]


    @api.constrains('price')
    def _check_offer(self):
        if self.property_id.expected_price > (self.price * 0.9):
            raise ValidationError("The price cannot be lower than 90% of the expected price.")

    # @api.model
    # def create(self, vals):
    #     self.env['estate.property'].browse(vals['property_id']).state()
    #     res = super(PropertyOffer, self).create(vals)
    #     return res