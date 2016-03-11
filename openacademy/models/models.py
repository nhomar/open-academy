# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class Course(models.Model):
    _name = 'course'

    name = fields.Char()
    description = fields.Text()
    responsible = fields.Many2one('res.users')
    sessions = fields.One2many('session', 'course')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The name of the course must be unique'),
        ('name_desc_check', 'CHECK(name <> description)', 'The name and the description must be differents')
    ]

class Session(models.Model):
    _name = 'session'

    name = fields.Char()
    active = fields.Boolean(default=True)
    instructor = fields.Many2one('res.partner')
    course = fields.Many2one('course')
    start_date = fields.Date(default=lambda self: fields.datetime.now())
    duration = fields.Float(help="Duration in days")
    seats = fields.Integer()
    attendees = fields.Many2many('res.partner', 'session_id', 'partner_id')
    percentage_seats_taken = fields.Float(compute="_compute_perc_seats_taken", store=True)

#     value = fields.Integer()
#
    @api.depends('attendees', 'seats')
    def _compute_perc_seats_taken(self):
        for record in self:
            if record.seats:
                record.percentage_seats_taken = float(len(record.attendees)) / record.seats * 100.00
            else:
                record.percentage_seats_taken = 0.00

    @api.onchange('seats', 'duration', 'attendees')
    def _onchange_seats(self):
        if self.duration < 0:
            return {'warning': {
                    'title': 'Invalid Duration Value',
                    'message': 'Duration must be a positive value.'
                }
            }
        if self.seats < 0:
            return {'warning': {
                    'title': 'Invalid Seats Value',
                    'message': 'Seats must be a postive value.'
                }
            }
        if self.percentage_seats_taken > 100.0:
            return {'warning': {
                    'title': 'No more attendees',
                    'message': 'You can not have more attendees than seats availables.'
                }
            }

    @api.constrains('instructor', 'attendees')
    def _check_instructor(self):
        for record in self:
            for att in record.attendees:
                if att == record.instructor:
                    raise ValidationError("Intructor can not be an attendee, please remove the partner %s from attendees list" % record.instructor.display_name)
