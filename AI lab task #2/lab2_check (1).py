"""Lab 2 - Part C: Checks and the noisy-sequence edge case.

Run: python lab2_check.py
"""
from lab2_percepts import ClassroomAgent
from lab2_model import StatefulClassroomAgent


def check_reflex():
    agent = ClassroomAgent()
    percepts = [(29, True), (29, True), (20, True),
                (26, True), (19, True), (29, False)]
    expected = ["COOL", "COOL", "IDLE", "IDLE", "WARM", "ECO"]
    got = [agent.act(*p) for p in percepts]
    assert got == expected, (got, expected)
    print("PASS reflex agent matches expected modes:", got)


def check_stateful():
    agent = StatefulClassroomAgent()
    percepts = [(29, True), (29, True), (20, True),
                (26, True), (19, True), (29, False), (15, False)]
    expected = [("COOL", True), ("COOL", False), ("IDLE", True),
                ("IDLE", False), ("WARM", True), ("ECO", True),
                ("ECO", False)]
    got = [agent.act(*p) for p in percepts]
    assert got == expected, (got, expected)
    print("PASS stateful agent targets and command flags are correct")


def noisy_edge_case():
    """Sensor noise around 26 C: remembering the last mode is NOT hysteresis."""
    agent = StatefulClassroomAgent()
    noisy = [26.2, 25.8, 26.3, 25.7, 26.4, 25.9]
    print("\nEdge case - noisy readings around 26 C (room occupied)")
    print(f"{'step':<5}{'temp':<7}{'target':<7}outcome")
    commands = 0
    for step, t in enumerate(noisy, 1):
        target, send = agent.act(t, True)
        commands += send
        print(f"{step:<5}{t:<7}{target:<7}{'SEND COMMAND' if send else 'no command'}")
    print(f"Commands sent: {commands} out of {len(noisy)} readings")
    return commands


if __name__ == "__main__":
    check_reflex()
    check_stateful()
    noisy_edge_case()
