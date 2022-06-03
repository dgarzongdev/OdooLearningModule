from odoo import fields, models

class PropertyTag(models.Model):
    _name = "property.tag"
    _description = "Property's Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('unique_name', 'unique(name)','The name should be unique.')
    ]