from enum import Enum
import enum
from uploader import DeviceFarm
    
ssh_addr_map = {
    DeviceFarm.AVOCADO : "avocado.enerzai.com"
}
ssh_port_map = {
    DeviceFarm.AVOCADO : 22
}

arch_map = {
    DeviceFarm.AVOCADO : "AMD64"
}