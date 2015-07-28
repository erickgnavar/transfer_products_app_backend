# coding: utf-8

from openerp import models, fields, api


class TransferProductHistory(models.Model):

    _name = 'transfer.product.history'

    product_id = fields.Many2one('product.product', required=True)
    origin_id = fields.Many2one('stock.location', required=True)
    destination_id = fields.Many2one('stock.location', required=True)
    picking_id = fields.Many2one('stock.picking', required=True)
    user_id = fields.Many2one('res.users', required=True)

    @api.model
    def make_transfer(self, product_id, origin_id, destination_id):
        db_stock_picking = self.env['stock.picking']
        db_product = self.env['product.product']
        _product = db_product.browse(product_id)
        picking = db_stock_picking.create({
            'partner_id': _product.seller_ids[0].name.id,
            'picking_type_id': 1,
            'move_lines': [
                (0, False, {
                    'product_id': product_id,
                    'product_uom': _product.uom_id.id,
                    'product_uom_qty': 1,
                    'name': _product.name,
                    'location_id': origin_id,
                    'location_dest_id': destination_id
                })
            ]
        })
        self.create({
            'user_id': self.env.user.id,
            'product_id': product_id,
            'origin_id': origin_id,
            'destination_id': destination_id,
            'picking_id': picking.id
        })
        return {
            'status': 'ok'
        }
