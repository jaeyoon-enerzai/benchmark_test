from models.layer import LayerDB
from utils import make_query_dict

def get_or_create_layer(opcode, attr, input_shape, device, commit, commitdate):
    # find if a layer exists or not
    querydict = make_query_dict(attr, "attr")
    querydict['input_shape'] = input_shape
    querydict['opcode'] = opcode
    querydict['device'] = device

    layer = LayerDB.objects(**querydict)
    if len(layer) == 0:
        layer = LayerDB(opcode=opcode, device=device, input_shape = input_shape)
        for k_, v_ in attr.items():
            layer.attr[k_] = v_
        layer.save()
    elif len(layer) == 1:
        layer = layer[0]
    else:
        raise RuntimeError("Layer must be unique but there are more than one")
    return layer