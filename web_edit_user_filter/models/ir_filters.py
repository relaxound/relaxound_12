# Copyright 2019 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrFilters(models.Model):
    _inherit = 'ir.filters'

    facet = fields.Text()

    @api.model
    # @api.multi
    def get_filters(self, model, action_id=None):
        res = super(IrFilters,self).get_filters(model, action_id)
        ids = map(lambda f: f['id'], res)
        # Browse filters that are in res
        filters = self.browse(ids)
        import pdb;
        pdb.set_trace()
        for i, res_filter in enumerate(res):
            # Add the field 'facet' to the result
            res[i]['facet'] = filters.filtered(
                lambda f: f.id == res_filter['id']
            ).facet
            print("res[i]['facet']------->",res[i]['facet'])
            print("###########################################")
            print("res----->",res)
            return res
        # return res_filter['id']


    class Edit(models.Model):
        _inherit = 'sale.order'

        edit1 = fields.Char()

