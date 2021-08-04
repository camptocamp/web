# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    m2x_create_edit_option_ids = fields.One2many(
        "m2x.create.edit.option",
        "ir_model_id",
    )

    def button_empty(self):
        for ir_model in self:
            ir_model._empty_m2x_create_edit_option()

    def button_fill(self):
        for ir_model in self:
            ir_model._fill_m2x_create_edit_option()

    def _empty_m2x_create_edit_option(self):
        """Removes every option for model ``self``"""
        self.ensure_one()
        self.m2x_create_edit_option_ids.unlink()

    def _fill_m2x_create_edit_option(self):
        """Adds every missing field option for model ``self``"""
        self.ensure_one()
        existing = self.m2x_create_edit_option_ids.mapped("ir_model_field_id")
        valid = self.field_id.filtered(lambda f: f.ttype.startswith("many2"))
        vals = [(0, 0, {"ir_model_field_id": f.id}) for f in valid - existing]
        self.write({"m2x_create_edit_option_ids": vals})
