from odoo import api, fields, models


class Course(models.Model):
    _name = "academy.course"
    _description = "Academy Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "summary"
   
    name = fields.Char(
        sting="Title",
        required=True,
        tracking=True,
    )
    description = fields.Text(tracking=True)
    responsible_id = fields.Many2one(
        comodel_name="res.users",
        tracking=True,
    )
    session_ids = fields.One2many(
        comodel_name="academy.session",
        inverse_name="course_id",
        tracking=True,
    )
    summary = fields.Char(
        compute="_compute_summary",
        tracking=True,
        store=True,
    )

    @api.depends("name", "responsible_id", "responsible_id.name")
    def _compute_summary(self):
        for rec in self:
            rec.summary = f"{rec.name or ''} - {rec.responsible_id.name or 'No Responsible'}"

    def action_open_sessions(self):
        return {
            "name": "Sessions",
            "type": "ir.actions.act_window",
            "res_model": "academy.session",
            "view_mode": "list",
            "domain": [("course_id", "=", self.id)],
            "context": {"default_course_id": self.id},
        }
