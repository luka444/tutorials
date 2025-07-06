from odoo import api, fields, models


class Session(models.Model):
    _name = "academy.session"
    _description = "Academy Session"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Title", required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2))
    seats = fields.Integer(string="Number Of Seats")
    course_id = fields.Many2one(comodel_name="academy.course")
    taken_seats = fields.Float(
        string="Seats",
        compute="_compute_taken_seats",
    )

    api.depends("seats")
    def _compute_taken_seats(self):
        for rec in self:
            rec.taken_seats = 0.0