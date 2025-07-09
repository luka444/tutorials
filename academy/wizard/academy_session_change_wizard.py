from odoo import fields, models


class AcademySessionChangeWizard(models.TransientModel):
    _name = "academy.session.change.wizard"
    _description = "Academy Session Change Wizard"

    course_id = fields.Many2one(comodel_name="academy.course")

    def action_apply(self):
        records = self.env.context.get("active_ids")
        for_change_records = self.env["academy.session"].browse(records)
        for_change_records.write({"course_id": self.course_id.id})
            

