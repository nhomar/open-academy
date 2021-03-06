# -*- coding: utf-8 -*-

from datetime import timedelta
from openerp import models, fields, api, _
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

    @api.multi
    def copy(self, default=None):
        default = dict(default or {},
                       name='%s (copy)' % self.name)
        return super(Course, self).copy(default=default)

class Session(models.Model):
    _name = 'session'

    name = fields.Char()
    active = fields.Boolean(default=True)
    instructor = fields.Many2one('res.partner')
    course = fields.Many2one('course')
    start_date = fields.Date(default=lambda self: fields.datetime.now())
    end_date = fields.Date(compute='_compute_end_date',
                           inverse='_set_end_date', store=True,)
    duration = fields.Float(help="Duration in days")
    seats = fields.Integer()
    attendees = fields.Many2many('res.partner', 'session_id', 'partner_id')
    percentage_seats_taken = fields.Float(compute="_compute_perc_seats_taken", store=True)
    total_seats_taken = fields.Integer(compute="_compute_perc_seats_taken", store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('done', 'Done')], default="draft", required=True)

#     value = fields.Integer()
#
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue
            # Add duration to start_date,
            # but: Monday  5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates
            # but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1

    @api.depends('attendees', 'seats')
    def _compute_perc_seats_taken(self):
        for record in self:
            if record.seats:
                record.percentage_seats_taken = round(float(len(record.attendees)) / record.seats * 100.00, 2)
                record.total_seats_taken = len(record.attendees)
            else:
                record.percentage_seats_taken = 0.00
                record.total_seats_taken = 0

    @api.onchange('seats', 'duration', 'attendees')
    def _onchange_seats(self):
        if self.duration < 0:
            return {'warning': {
                    'title': _('Invalid Duration Value'),
                    'message': _('Duration must be a positive value.')
                }
            }
        if self.seats < 0:
            return {'warning': {
                    'title': _('Invalid Seats Value'),
                    'message': _('Seats must be a positive value.')
                }
            }
        if self.percentage_seats_taken > 100.0:
            return {'warning': {
                    'title': _('No more attendees'),
                    'message': _('You can not have more attendees than seats availables.')
                }
            }

    @api.constrains('instructor', 'attendees')
    def _check_instructor(self):
        for record in self:
            for att in record.attendees:
                if att == record.instructor:
                    raise ValidationError(_("Intructor can not be an attendee, please remove the partner %s from attendees list") % record.instructor.display_name)

    @api.multi
    def set_draft(self):
        for record in self:
            record.state = 'draft'

    @api.multi
    def set_confirmed(self):
        for record in self:
            record.state = 'confirmed'

    @api.multi
    def set_done(self):
        for record in self:
            record.state = 'done'
