from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_web_m2x_options(self):
        opts = ['web_m2x_options.create', 'web_m2x_options.create_edit',
                'web_m2x_options.limit', 'web_m2x_options.search_more',
                'web_m2x_options.m2o_dialog', 'web_m2x_options.field_limit_entries',
                'web_m2x_options.m2o_search_delay',]
        return {
            res["key"]: res["value"] for res in self.sudo().search_read(
                [['key', 'in', opts]], ["key", "value"])
        }
