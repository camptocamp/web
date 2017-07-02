# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class WebEnvironmentRibbonBackend(models.AbstractModel):

    _name = 'web.environment.ribbon.backend'
    _description = 'Web Environment Ribbon Backend'

    @api.model
    def _prepare_ribbon_format_vals(self):
        return {
            'db_name': self.env.cr.dbname,
        }

    @api.model
    def _prepare_ribbon_name(self):
        name_tmpl = self.env['ir.config_parameter'].get_param('ribbon.name')
        vals = self._prepare_ribbon_format_vals()
        return name_tmpl.format(**vals)

    @api.model
    def get_environment_ribbon(self):
        """
        This method returns the ribbon data from ir config parameters
        :return: dictionary
        """
        ir_config_model = self.env['ir.config_parameter']
        name = self._prepare_ribbon_name()
        return {
            'name': name,
            'color': ir_config_model.get_param('ribbon.color'),
            'background_color': ir_config_model.get_param(
                'ribbon.background.color'),
        }
