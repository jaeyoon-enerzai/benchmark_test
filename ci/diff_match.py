from pathlib import Path

diff_to_monitor = {
    "CONV2D" : [Path(__file__).parent.parent / "ci/monitor/a.txt"],
    "LINEAR" : [Path(__file__).parent.parent / "ci/monitor/b.txt"]
}