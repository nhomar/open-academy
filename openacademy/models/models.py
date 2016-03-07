# -*- coding: utf-8 -*-

from openerp import models, fields

class Course(models.Model):
    _name = 'course'

    name = fields.Char()
    description = fields.Text()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
