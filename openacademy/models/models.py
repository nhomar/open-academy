# -*- coding: utf-8 -*-

from openerp import models, fields

class Course(models.Model):
    _name = 'course'

    name = fields.Char()
    description = fields.Text()
    responsible = fields.Many2one('res.users')
    sessions = fields.One2many('session', 'course')

class Session(models.Model):
    _name = 'session'

    name = fields.Char()
    instructor = fields.Many2one('res.partner')
    course = fields.Many2one('course')
    start_date = fields.Date()
    duration = fields.Float(help="Duration in days")
    seats = fields.Integer()

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
