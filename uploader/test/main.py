from uploader import DeviceFarm, GroupLoader, LayerLoader, ModelLoader
import random
from datetime import datetime

def group_post_test():
    device = DeviceFarm.AVOCADO
    latency = random.random()
    date =  datetime.now()
    GroupLoader().set_group(device, latency, date)

def group_get_test():
    return GroupLoader().get_groups()

def get_mobilenet():
    modelname = 'mobilenet'
    framework = 'tflite'
    input_shape =[(1,3,224,224)]
    device = DeviceFarm.AVOCADO
    commit = 'abcdef'
    groupid = group_get_test()[0]['group']
    return modelname, framework, input_shape, device, commit, groupid

def get_conv2d():
    groupid = group_get_test()[0]['group']
    if random.random() > 0.5:
        ker = random.randint(2,4)
    else:
        ker = 3
    attr = {"kernel_size" : (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.AVOCADO
    input_shape = [(1,2,3,4)]
    opcode = 'Conv2D'
    commit = 'abcdef'    
    return groupid, attr, device, input_shape, opcode, commit

def model_post_test():
    modelname, framework, input_shape, device, commit, groupid = get_mobilenet()
    latency = random.random()
    date = datetime.now()
    ModelLoader(modelname, framework, input_shape, device, commit, groupid).upload_model(date, latency)

def model_get_all_test():
    modelname, framework, input_shape, device, commit, groupid = get_mobilenet()
    print(ModelLoader(modelname, framework, input_shape, device, commit, groupid).get_latency())

def model_get_all_result_test():
    modelname, framework, input_shape, device, commit, groupid = get_mobilenet()
    print(ModelLoader(modelname, framework, input_shape, device, None, groupid).get_all_result())

def layer_post_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    if random.random() < 0.5:
        optim_param = {'unroll' : list(random.randint(1,2) for _ in range(3)), 
                    'vector' : list(random.randint(1,2) for _ in range(3))}
    else:
        optim_param = {'unroll': (2, 2, 1),
                    'vector': (1, 2, 2)}
    latency = random.random()
    date = datetime.now()
    LayerLoader(attr, input_shape, opcode, device, commit,groupid).upload_layer(optim_param,
                               latency, date, )

def layer_get_group_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    print(LayerLoader(attr, input_shape, opcode, device, commit, groupid).get_group())

def layer_set_optim_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    LayerLoader(attr, input_shape, opcode, device, commit,groupid).set_optim()

def layer_get_optim_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    print(LayerLoader(attr, input_shape, opcode, device, commit,groupid).get_optim())

def layer_get_profiles_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    print(LayerLoader(attr, input_shape, opcode, device, commit,groupid).get_profiles())

def layer_init_latency_test():
    groupid, attr, device, input_shape, opcode, commit = get_conv2d()
    optim_param = {'unroll': (2, 2, 1),
                    'vector': (1, 2, 2)}
    LayerLoader(attr, input_shape, opcode, device, commit, groupid).initialize_latency(optim_param)

if __name__ == "__main__":
    # GroupDB test
    # group_post_test()
    import time
    print("GET GROUP")
    group_get_test()
    print("UPLOAD LAYER")
    layer_post_test()
    print("GET GROUP REPR")
    layer_get_group_test()
    print("SET OPTIM")
    layer_set_optim_test()
    print("GET OPTIM")
    layer_get_optim_test()
    print("ALL PROFILES")
    layer_get_profiles_test()
    print("INIT")
    layer_init_latency_test()
    print("SET OPTIM")
    layer_set_optim_test()
    print("GET GROUP REPR")
    layer_get_group_test()
    print("GET OPTIM")
    layer_get_optim_test()
    print("ALL PROFILES")
    layer_get_profiles_test()
    print("Model post")
    model_post_test()
    print("Get Model")
    model_get_all_test()
    print("GET ALL RESULT")
    model_get_all_result_test()