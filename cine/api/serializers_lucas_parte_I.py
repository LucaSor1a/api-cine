from django.core import serializers


def serializacion_de_objetos(objetos):
    JSONSerializer = serializers.get_serializer("json")
    json_serializer = JSONSerializer()
    json_serializer.serialize(objetos)
    data = json_serializer.getvalue()
    return data
