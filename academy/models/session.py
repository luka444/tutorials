from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Session(models.Model):
    _name = "academy.session"
    _description = "Academy Session"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Title",
        required=True,
    )
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2))
    seats = fields.Integer(string="Number Of Seats")
    course_id = fields.Many2one(comodel_name="academy.course")
    taken_seats = fields.Float(
        string="Seats",
        compute="_compute_taken_seats",
    )
    attendee_ids = fields.Many2many(comodel_name="res.partner")
    free_seats = fields.Integer(compute="_compute_free_seats")
    is_user_already_registered = fields.Boolean(compute="_compute_is_user_already_registered")

    def action_change_course(self):
        return {
            "name": "Change Course",
            "type": "ir.actions.act_window",
            "res_model": "academy.session.change.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"active_ids": self.ids},
        }

    def action_register(self):
        current_user = self.env.user.partner_id
        if current_user in self.attendee_ids:
            raise ValidationError("You are already registered for this session")
        if len(self.attendee_ids) >= self.seats:
            raise ValidationError("Seats are full")
        self.attendee_ids += current_user

    def _compute_is_user_already_registered(self):
        for rec in self:
            rec.is_user_already_registered = rec.attendee_ids.filtered(lambda s: s == self.env.user.partner_id)

    def _compute_taken_seats(self):
        for rec in self:
            if rec.seats != 0:
                rec.taken_seats = 100 * len(rec.attendee_ids) / rec.seats
            else:
                rec.taken_seats = 0.0

    def _compute_free_seats(self):
        for rec in self:
            if rec.seats > 0:
                rec.free_seats = rec.seats - len(rec.attendee_ids)
            else:
                rec.free_seats = 0

    @api.onchange("seats")
    def _onchange_seats(self):
        if self.seats < 0:
            return {
                "warning": {
                    "title": "Invalid Seats",
                    "message": "Number of seats cannot be negative",
                }
            }
