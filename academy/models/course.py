from odoo import fields, models


class Course(models.Model):
    _name = "academy.course"
    _description = "Academy Course"
    _inherit = ['mail.thread', 'mail.activity.mixin']
   
    name = fields.Char(sting="Title", required=True)
    description = fields.Text()
    responsible_id = fields.Many2one(comodel_name="res.users", tracking=True)
    session_ids = fields.One2many(
        comodel_name="academy.session",
        inverse_name="course_id",
    )