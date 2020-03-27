from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field cannot be left blank!"
    )
    parser.add_argument(
        "store_id",
        type=int,
        required=True,
        help="Every item needs a store_id"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return { "item" : item.json() }, 200
        return {"message": "Item not found"}, 404

    def post(self, name):
        if ItemModel.find_by_name(name) is not None:
            return {"message": "An item with name '{}' already exists".format(name)}, 400

        data = Item.parser.parse_args()
        
        item = ItemModel(name, data["price"], data["store_id"])

        try:
            item.save_to_db()
        except Exception as e:
            return {"error": "An error occured while inserting: {}".format(str(e))}, 500

        return {"item": item.json()}, 201

    def delete(self, name):

        try:
            item = ItemModel.find_by_name(name)
            if item:
                item.delete_from_db()
        except Exception as e:
            return {"error": str(e)}, 500

        return {"message": "item deleted"}, 200

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)
        
        if item is None:
            item = ItemModel(name, data["price"], data["store_id"]) 
        else:
            item.price = data["price"]
            item.store_id = data["store_id"]
        
        item.save_to_db()
        
        return {"item": item.json()}, 200


class ItemList(Resource):
    def get(self):
        item_list = [item.json() for item in ItemModel.query.all()]
        return {"items": item_list}
