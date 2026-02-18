from pathlib import Path

from chandisvrp.instances.serialization import load_instance, save_instance
from chandisvrp.types import Customer, Instance


def test_instance_save_load(tmp_path: Path) -> None:
    inst = Instance(
        "1.0",
        "abc",
        "Chandigarh",
        0,
        [Customer(1, 2, 3, 60, 0, 1000, "residential")],
        2,
        20,
    )
    p = tmp_path / "inst.json"
    save_instance(inst, p)
    loaded = load_instance(p)
    assert loaded.instance_id == "abc"
    assert loaded.customers[0].demand == 3
