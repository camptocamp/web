# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.cache import ormcache
from odoo.tools.safe_eval import safe_eval


class M2xCreateEditOption(models.Model):
    _name = "m2x.create.edit.option"
    _description = 'Manage Options "Create/Edit" For Fields'

    ir_model_field_id = fields.Many2one(
        "ir.model.fields",
        domain=[("ttype", "in", ("many2many", "many2one"))],
        ondelete="cascade",
        required=True,
        string="Field",
    )

    ir_model_field_name = fields.Char(
        compute="_compute_ir_model_field_name",
        store=True,
        string="Field Name",
    )

    ir_model_id = fields.Many2one(
        "ir.model",
        ondelete="cascade",
        required=True,
        string="Model",
    )

    ir_model_name = fields.Char(
        compute="_compute_ir_model_name",
        inverse="_inverse_ir_model_name",
        store=True,
        string="Model Name",
    )

    option = fields.Selection(
        [
            ("all", "Remove all"),
            ("create", 'Remove "Create"'),
            ("create_edit", 'Remove "Create and Edit"'),
        ],
        default="all",
        required=True,
        string="Option",
    )

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super().create(vals_list)

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    def unlink(self):
        self.clear_caches()
        return super().unlink()

    @api.depends("ir_model_field_id")
    def _compute_ir_model_field_name(self):
        for opt in self:
            opt.ir_model_field_name = opt.ir_model_field_id.name

    @api.depends("ir_model_id")
    def _compute_ir_model_name(self):
        for opt in self:
            opt.ir_model_name = opt.ir_model_id.model

    def _inverse_ir_model_name(self):
        ir_model_obj = self.env["ir.model"]
        for opt in self:
            opt.ir_model_id = ir_model_obj.search(
                [("model", "=", opt.ir_model_name)], limit=1
            )

    @api.constrains("ir_model_name", "ir_model_field_name")
    def _check_model_and_field_names(self):
        env = self.env
        for opt in self:
            mname, fname = opt.ir_model_name, opt.ir_model_field_name
            if mname not in env:
                raise ValidationError(_("'%s' is not a valid model!") % mname)
            elif fname not in env[mname]:
                raise ValidationError(
                    _("'%s' is not a valid field for model '%s'!") % (fname, mname)
                )

    @api.constrains("ir_model_name", "ir_model_field_name")
    def _check_field_model_uniqueness(self):
        for opt in self:
            mname, fname = opt.ir_model_name, opt.ir_model_field_name
            # ``search_count`` makes it faster
            if (
                self.search_count(
                    [("ir_model_name", "=", mname), ("ir_model_field_name", "=", fname)]
                )
                > 1
            ):
                raise ValidationError(
                    _("There is already an option for field '%s' in '%s'!")
                    % (fname, mname)
                )

    @api.model
    def apply(self, node, model_name):
        """Reads ``node`` options attribute and updates it.

        NB: if the option is already set within the ``node`` ``options``
        attribute, then no action is taken (UI modifications have priority:
        do not override an option that's already set within the ``ir.ui.view``
        record architecture).
        """
        opt = self.get(model_name, node.attrib["name"]).option
        if opt:
            node_options = node.attrib.get("options") or {}
            if isinstance(node_options, str):
                node_options = safe_eval(node_options, self.env.context) or {}
            keys = {"create", "create_edit"} if opt == "all" else {opt}
            for key in keys.difference(node_options):
                node_options[key] = False
            node.set("options", str(node_options))

    @api.model
    def get(self, model_name, field_name):
        """Returns specific option for ``field_name`` in ``model_name``

        :param str model_name: technical model name (i.e. "sale.order")
        :param str field_name: technical field name (i.e. "partner_id")
        """
        return self.browse(self._get(model_name, field_name))

    @api.model
    @ormcache("model_name", "field_name")
    def _get(self, model_name, field_name):
        """Inner implementation of ``get``.
        Results are cached for faster computations, therefore an ID is
        returned (see :class:`ormcache` documentation); :meth:`get`
        will then convert it to a proper record.

        :param str model_name: technical model name (i.e. "sale.order")
        :param str field_name: technical field name (i.e. "partner_id")
        """
        # `_check_field_model_uniqueness()` grants uniqueness
        dom = [
            ("ir_model_name", "=", model_name),
            ("ir_model_field_name", "=", field_name),
        ]
        return self.search(dom, limit=1).id
