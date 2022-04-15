from odoo import fields, models


class IrActionsActWindowClose(models.Model):
    _name = "ir.actions.act_view_reload"
    _description = "Action View Reload"
    _inherit = "ir.actions.actions"
    _table = "ir_actions"

    type = fields.Char(default="ir.actions.act_view_reload")

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {
            # 'effect' is not a real field of ir.actions.act_window_close but is
            # used to display the rainbowman
            "effect"
        }
