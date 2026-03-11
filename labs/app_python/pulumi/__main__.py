import pulumi
import pulumi_yandex as yandex

network = yandex.VpcNetwork("lab-network")

subnet = yandex.VpcSubnet(
    "lab-subnet",
    network_id=network.id,
    zone="ru-central1-a",
    v4_cidr_blocks=["10.0.0.0/24"]
)

vm = yandex.ComputeInstance(
    "lab-vm",
    resources={
        "cores": 2,
        "memory": 1,
        "core_fraction": 20
    },
    boot_disk={
        "initialize_params": {
            "image_id": "fd80qm01ah03dkqb14lc",
            "size": 30
        }
    },
    network_interfaces=[{
        "subnet_id": subnet.id,
        "nat": True
    }]
)

pulumi.export("public_ip", vm.network_interfaces[0].nat_ip_address)