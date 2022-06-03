from odoo import fields, models, api

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property's Type"
    _order = "name"

    name = fields.Char(required=True)

    property_ids = fields.One2many("estate.property", "property_type_id", string="Property")

    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many("property.offer", "property_type_id", string="Offers")

    offer_count = fields.Integer(compute="_number_offers")

    sql_constraints = [
        ('unique_name', 'unique(name)','The name should be unique.')
    ]
    @api.depends("offer_ids", "offer_count")
    def _number_offers(self):
        self.offer_count = len(self.offer_ids)
