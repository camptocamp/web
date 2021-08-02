# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.cache import ormcache
from odoo.tools.safe_eval import safe_eval


class M2xCreateEditOption(models.Model):
    _name = "m2x.create.edit.option"
    _description = "Manage Options 'Create/Edit' For Fields"

    ir_model_field_id = fields.Many2one(
        "ir.model.fields",
        domain=[("ttype", "in", ("many2many", "many2one"))],
        ondelete="cascade",
        required=True,
        string="Field",
    )

    ir_model_field_name = fields.Char(
        related="ir_model_field_id.name",
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

    option_create = fields.Selection(
        [
            ("none", "Do nothing"),
            ("set_true", "Add"),
            ("force_true", "Force Add"),
            ("set_false", "Remove"),
            ("force_false", "Force Remove"),
        ],
        default="set_false",
        help="Defines behaviour for 'Create' option:\n"
        "* Do nothing: nothing is done\n"
        "* Add/Remove: option 'Create' is set to True/False only if not"
        " already present in view definition\n"
        "* Force Add/Remove: option 'Create' is always set to True/False,"
        " overriding any pre-existing option",
        required=True,
        string="Create Option",
    )

    option_create_edit = fields.Selection(
        [
            ("none", "Do nothing"),
            ("set_true", "Add"),
            ("force_true", "Force Add"),
            ("set_false", "Remove"),
            ("force_false", "Force Remove"),
        ],
        default="set_false",
        help="Defines behaviour for 'Create & Edit' option:\n"
        "* Do nothing: nothing is done\n"
        "* Add/Remove: option 'Create & Edit' is set to True/False only if not"
        " already present in view definition\n"
        "* Force Add/Remove: option 'Create & Edit' is always set to"
        " True/False, overriding any pre-existing option",
        required=True,
        string="Create & Edit Option",
    )

    @api.model_create_multi
    def create(self, vals_list):
        type(self)._get.clear_cache(self.browse())
        return super().create(vals_list)

    def write(self, vals):
        type(self)._get.clear_cache(self.browse())
        return super().write(vals)

    def unlink(self):
        type(self)._get.clear_cache(self.browse())
        return super().unlink()

    @api.depends("ir_model_id")
    def _compute_ir_model_name(self):
        for opt in self:
            opt.ir_model_name = opt.ir_model_id.model

    def _inverse_ir_model_name(self):
        getter = self.env["ir.model"]._get
        for opt in self:
            # This also works as a constrain: if ``ir_model_name`` is not a
            # valid model name, then ``ir_model_id`` will be emptied, but it's
            # a required field!
            opt.ir_model_id = getter(opt.ir_model_name)

    @api.constrains("ir_model_id", "ir_model_field_id")
    def _check_field_in_model(self):
        for opt in self:
            if opt.ir_model_field_id.model_id != opt.ir_model_id:
                mname = opt.ir_model_name
                fname = opt.ir_model_field_name
                msg = _("'%s' is not a valid field for model '%s'!")
                raise ValidationError(msg % (fname, mname))

    @api.constrains("ir_model_name", "ir_model_field_name")
    def _check_field_model_uniqueness(self):
        # ``search_count`` makes it faster
        sc = self.search_count
        fnames = ("ir_model_name", "ir_model_field_name")
        for data in self.read(fnames):
            dom = [(k, "=", v) for k, v in data.items() if k != "id"]
            if sc(dom) > 1:
                raise ValidationError(
                    _("There is already an option for field '%s' in '%s'!")
                    % (data["ir_model_field_name"], data["ir_model_name"])
                )

    @api.constrains("ir_model_field_id")
    def _check_field_type(self):
        ttypes = ("many2many", "many2one")
        if any(o.ir_model_field_id.ttype not in ttypes for o in self):
            msg = _("Only Many2many and Many2one fields can be chosen!")
            raise ValidationError(msg)

    def _apply_options(self, node):
        """Applies options ``self`` to ``node``"""
        self.ensure_one()
        options = node.attrib.get("options") or {}
        if isinstance(options, str):
            options = safe_eval(options, dict(self.env.context or [])) or {}
        for k in ("create", "create_edit"):
            opt = self["option_%s" % k]
            if opt == "none":
                continue
            mode, val = opt.split("_")
            if mode == "force" or k not in options:
                options[k] = val == "true"
        node.set("options", str(options))

    @api.model
    def get(self, model_name, field_name):
        """Returns specific record for ``field_name`` in ``model_name``

        :param str model_name: technical model name (i.e. "sale.order")
        :param str field_name: technical field name (i.e. "partner_id")
        """
        return self.browse(self._get(model_name, field_name))

    @api.model
    @ormcache("model_name", "field_name")
    def _get(self, model_name, field_name):
        """Inner implementation of ``get``.
        An ID is returned to allow caching (see :class:`ormcache`); :meth:`get`
        will then convert it to a proper record.

        :param str model_name: technical model name (i.e. "sale.order")
        :param str field_name: technical field name (i.e. "partner_id")
        """
        dom = [
            ("ir_model_name", "=", model_name),
            ("ir_model_field_name", "=", field_name),
        ]
        # `_check_field_model_uniqueness()` grants uniqueness if existing
        return self.search(dom, limit=1).id
