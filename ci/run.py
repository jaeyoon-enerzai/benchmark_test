# optimium import
import argparse
import os
import subprocess
import datetime
from pathlib import Path
import git
import random
from uploader import DeviceFarm, GroupLoader, LayerLoader, ModelLoader
from table import create_table_header

def get_group(device : DeviceFarm, target_arch, SSH_PORT, SSH_ADDR):
    if target_arch.lower() in ("i386", "amd64", "x86_64", "x64"):
        arch = "x86_64"
    elif target_arch.lower() in ("aarch64", "arm64", "hexagon"):
        arch = "aarch64"
    else:
        raise ValueError("target arch must be one of i386, AMD64, x86_64, x64, aarch64, arm64, hexagon but got ", target_arch)
    
    repeat = 1000
    warmup = 300
    num_threads = 1
    USER_DIR = f"/home/optima-remote"
    tflitepath = Path(__file__).parent / "glob/face_detection_short_range.tflite"
    os.system(f"scp -P {SSH_PORT} {tflitepath}  optima-remote@{SSH_ADDR}:{USER_DIR}")
    try:
        result = subprocess.run(
            f"ssh -p {SSH_PORT} optima-remote@{SSH_ADDR} bash run_benchmark.sh --arch {arch} --tfl_model {tflitepath.name} "
            + "--run_tflite "
            + f"--repeat {repeat} --warmup {warmup} --num_threads {num_threads}",
            shell=True,
            check=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=repeat*3 #timeout for benchmark profiling
        )
        output = result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Benchmark error: {e}")
        raise e
    except subprocess.TimeoutExpired as te:
        print(f"Benchmark Timeout: \n - STDERR: {te.stderr}\n - STDOUT: {te.stdout}\n\n")
        raise e
        
    temp = output.split("Summary")[1]
    tfl_time = temp.split("TFLite")[1].split(" us")[0].split(" ")[-1]
    tfl_time = float(tfl_time)
    resp = GroupLoader().set_group(device, tfl_time, datetime.datetime.now())
    group = resp['group']
    return group

def get_commit4layer(opcode, attr, device, input_shape, group, monitor_files, repo_location):
    repo = git.Repo(repo_location)
    tosee = 10
    # compare the most latest top 10 commits
    layer = LayerLoader(attr, input_shape, opcode, device, None, datetime.datetime.now(), group)
    curcommit = repo.commit()
    prevcommits = layer.get_commits()
    
    basecommit = None
    for commit, _ in prevcommits['commits'][:tosee]:
        diff = curcommit.diff(repo.commit(commit))
        diff_occur = False
        for each_diff in diff:
            a_path_diff =  Path(repo_location) / each_diff.a_path in monitor_files
            b_path_diff =  Path(repo_location) / each_diff.b_path in monitor_files
            if a_path_diff or b_path_diff:
                # change exists from this commit and thus find another commit
                diff_occur = True
                break
        if diff_occur is False:
            basecommit = commit
            break
    if basecommit is None:
        return curcommit.hexsha, curcommit.committed_datetime, True
    else:
        return basecommit, datetime.datetime.now(), False # anytime - it wouldn't be used

def get_optims(opcode, attr, device, input_shape, group, commit, commitdate, newcommit):
    if newcommit:
        # find the latest commit
        layer = LayerLoader(attr, input_shape, opcode, device, None, datetime.datetime.now(), group)
        prevcommits = layer.get_commits()
        if len(prevcommits['commits']) > 0:
            commit, commitdate = prevcommits['commits'][0]
    return LayerLoader(attr, input_shape, opcode, device, commit, commitdate, group).get_all_optim()

def load_profile(opcode, attr, device, input_shape, group, commit, commitdate, newcommit):
    if newcommit:
        return []
    else:
        return LayerLoader(attr, input_shape, opcode, device, commit, commitdate, group).get_profiles()

def upload_latency(opcode, attr, device, input_shape, group, commit, commitdate, date, latency):
    LayerLoader(attr, input_shape, opcode, device, commit, commitdate, group).upload_layer(optim_param,
                               latency, date, )    

def cleanup(opcode, attr, device, input_shape, group, commit, commitdate):
    LayerLoader(attr, input_shape, opcode, device, commit, commitdate, group).set_optim()

def get_best_optim(opcode, attr, device, input_shape, group, commit, commitdate, newcommit):
    if newcommit:
        raise RuntimeError("Tuning should be done in advance but it isn't")
    else:
        return LayerLoader(attr, input_shape, opcode, device, commit, commitdate, group).get_optim()

def upload_model_latency(modelname, framework, input_shape, device, commit, group, date, latency):
    ModelLoader(modelname, framework, input_shape, device, commit, group).upload_model(date, latency)

def _tuning_scenario(device):
    from device import ssh_addr_map, ssh_port_map, arch_map
    # 1. Set group
    group = get_group(device, arch_map[device], ssh_port_map[device], ssh_addr_map[device])
    
    # Pick Layer or Model
    if random.random() > 0.5:
        ker = random.randint(2,4)
    else:
        ker = 3
    attr = {"kernel_size" : (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.AVOCADO
    input_shape = [(1,2,3,4)]
    opcode = 'CONV2D'

    from diff_match import diff_to_monitor
    # 2. Get commit
    commit, commitdate, newcommit = get_commit4layer(opcode, attr, device, input_shape, group, diff_to_monitor[opcode], str(Path(__file__).parent.parent))
    
    # 3. Load profile
    profile_result = load_profile(opcode, attr, device, input_shape, group, commit, commitdate, newcommit)
    print("profile result : ")
    print(profile_result)
    
    # 4. Insert existing optim into search space
    optims = get_optims(opcode, attr, device, input_shape, group, commit, commitdate, newcommit)
    print("optims : ")
    print(optims)
    
    
    if random.random() < 0.5:
        optim_param = {'unroll' : list(random.randint(1,3) for _ in range(3)), 
                    'vector' : list(random.randint(1,3) for _ in range(3))}
    else:
        optim_param = {'unroll': (2, 2, 1),
                    'vector': (1, 2, 2)}
    # 5. measure latency
    latency = random.random()
    date = datetime.datetime.now()
    print("uploading : ")
    print(optim_param, latency)

    # 6. upload latency
    upload_latency(opcode, attr, device, input_shape, group, commit, commitdate, date, latency)
    
    # 7. cleanup
    cleanup(opcode, attr, device, input_shape, group, commit, commitdate)   
    

if __name__ == '__main__':
    # main 부분은 바뀔 것 - optimium script와 함께 config도 사용하면서
    ### Tuning logic ###
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', required=True)
    parser.add_argument("--tuning", action="store_true", default=False)
    args = parser.parse_args()
    from device import ssh_addr_map, ssh_port_map, arch_map
    device = getattr(DeviceFarm, args.device.upper())
    
    if args.tuning:
        _tuning_scenario(device)
    
    ### CI logic ###
    # 1. Set group
    group = get_group(device, arch_map[device], ssh_port_map[device], ssh_addr_map[device])
    
    # Pick Layer or Model
    if random.random() > 0.5:
        ker = random.randint(2,4)
    else:
        ker = 3
    attr = {"kernel_size" : (ker, ker), 'stride': (1,1), 'padding': (0,0,0,0)}
    device = DeviceFarm.AVOCADO
    input_shape = [(1,2,3,4)]
    opcode = 'CONV2D'
    
    # for each layer in model (2~3)
    from diff_match import diff_to_monitor
    # 2. Get commit
    commit, commitdate, newcommit = get_commit4layer(opcode, attr, device, input_shape, group, diff_to_monitor[opcode], '/home/yoo/enerzai_github/benchmark_test')
    
    # 3. Get best optim
    best_optim = get_best_optim(opcode, attr, device, input_shape, group, commit, commitdate, newcommit)   
    print('Best optim : ', best_optim)
      
    modelname = 'mobilenet'
    framework = 'tflite'
    input_shape =[(1,3,224,224)]
    # 4. measure latency
    latency = random.random()
    date = datetime.datetime.now()
    upload_model_latency(modelname, framework, input_shape, device, commit, group, date, latency)
    
    content, strnum_list = create_table_header(commit, commit, commit)
    with open(Path(__file__).parent / '../ciout/result.md', 'w') as f:
        f.write(content)