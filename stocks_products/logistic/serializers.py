from rest_framework import serializers
from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    #stock = serializers.IntegerField(required=False)
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'products', 'positions']
    # настройте сериализатор для склада

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)
        for x in positions:
            # # product = Product.objects.filter(id=x['product']).order_by('-id').first()
            # if not product:
            #     continue
            StockProduct.objects.create(
                stock=stock,
                product=x['product'],
                price=x['price'],
                quantity=x['quantity']
            )


        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')
        new_ids = {x['product'].id:x['product'].id for x in positions} # [2, 3] {2:2:, 3:3:}
        old_ids_for_del = {x.id:x.id for x in instance.products.all()} # {1:1, 2:2, 3:3}



        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)
        for x in positions:
            if x['product'].id in old_ids_for_del:
                # delete
                old_ids_for_del.pop(x['product'].id)

            obj, created = StockProduct.objects.update_or_create({
                'stock': stock,
                'product' : x['product'],
                             'price' : x['price'],
                                          'quantity': x['quantity']
            },
            stock=stock, product=x['product'] # select from where stock product
            )
            obj:StockProduct

        StockProduct.objects.filter(stock=stock, product_id__in=list(old_ids_for_del)).delete()

        return stock
