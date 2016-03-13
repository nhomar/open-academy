# -*- coding: utf-8 -*-

from openerp import models, fields, api

class CreateAttendees(models.TransientModel):
    _name = "create.attendee"

    session_ids = fields.Many2many('session', default= lambda self: self._context.get('active_ids'))
    attendee_ids = fields.Many2many('res.partner')

    @api.multi
    def add_attendees(self):
        for session in self.session_ids:
            session.attendees |= self.attendee_ids
