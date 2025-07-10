from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Session(models.Model):
    _name = "academy.session"
    _description = "Academy Session"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "summary"

    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
    )
    start_date = fields.Date(tracking=True)
    duration = fields.Float(tracking=True)
    seats = fields.Integer(
        string="Number Of Seats",
        tracking=True,
    )
    course_id = fields.Many2one(
        comodel_name="academy.course",
        tracking=True,
    )
    taken_seats = fields.Float(
        string="Seats",
        compute="_compute_taken_seats",
        tracking=True,
        store=True,
    )
    attendee_ids = fields.Many2many(
        comodel_name="res.partner",
        tracking=True,
    )
    free_seats = fields.Integer(
        compute="_compute_free_seats",
        tracking=True,
        store=True,
    )
    is_user_already_registered = fields.Boolean(
        compute="_compute_is_user_already_registered",
        tracking=True,
        store=True,
    )
    summary = fields.Char(
        compute="_compute_summary",
        tracking=True,
        store=True
    )
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        related="course_id.responsible_id",
        tracking=True,
    )
    remaining_days = fields.Integer(compute="_compute_remaining_days")
    active = fields.Boolean(default=True)

    def _compute_remaining_days(self):
        today = fields.Date.today()
        for rec in self:
            if rec.start_date and rec.start_date < today:
                rec.remaining_days = 0
            elif rec.start_date:
                rec.remaining_days = (rec.start_date - today).days
            else:
                rec.remaining_days = 0

    @api.depends("name", "responsible_id", "responsible_id.name", "seats")
    def _compute_summary(self):
        for rec in self:
            rec.summary = f"{rec.name or ''} - {rec.responsible_id.name or 'No Responsible'} ({rec.seats} seats)"

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

    @api.depends("attendee_ids")
    def _compute_is_user_already_registered(self):
        for rec in self:
            rec.is_user_already_registered = rec.attendee_ids.filtered(lambda s: s == self.env.user.partner_id)

    @api.depends("seats", "attendee_ids")
    def _compute_taken_seats(self):
        for rec in self:
            if rec.seats != 0:
                rec.taken_seats = 100 * len(rec.attendee_ids) / rec.seats
            else:
                rec.taken_seats = 0.0

    @api.depends("seats", "attendee_ids")
    def _compute_free_seats(self):
        for rec in self:
            if rec.seats > 0 and rec.seats > len(rec.attendee_ids):
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
