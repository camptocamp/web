# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from ..install.mte.sales import set_sale_conditions_MTE
from ..install.mts.sales import set_sale_conditions_MTS


@anthem.log
def main(ctx):
    set_sale_conditions_MTE(ctx)
    set_sale_conditions_MTS(ctx)
