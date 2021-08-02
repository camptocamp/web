# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def postprocess(self, node, current_node_path, editable, name_manager):
        res = super().postprocess(node, current_node_path, editable, name_manager)
        if node.tag == "field":
            self.env["m2x.create.edit.option"].apply(node, name_manager.Model._name)
        return res
