# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    product_substance_ids = fields.Many2many(
        'product.substance',
        string='Substances',
    )
    product_substance_mesure_ids = fields.One2many(
        'product.substance.mesure',
        'task_id',
        string='Substance Mesure',
    )
