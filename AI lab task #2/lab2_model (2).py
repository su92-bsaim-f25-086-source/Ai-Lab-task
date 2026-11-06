"""Lab 2 - Part B: Stateful classroom agent.

Keeps the SAME thresholds and occupancy priority as the reflex agent, but
remembers the previous target mode and returns (target, send_command).
A command is sent only when the target mode changes.
Run: python lab2_model.py
"""


class StatefulClassroomAgent:
    def __init__(self):
        self.previous_mode = None   # nothing commanded yet

    def decide(self, temp, occupied):
        """Same policy as the reflex agent."""
        if not occupied:
            return "ECO"
        if temp > 26:
            return "COOL"
        if temp < 20:
            return "WARM"
        return "IDLE"

    def act(self, temp, occupied):
        target = self.decide(temp, occupied)
        send_command = target != self.previous_mode
        self.previous_mode = target
        return target, send_command


if __name__ == "__main__":
    agent = StatefulClassroomAgent()
    percepts = [
        (29, True),    # first percept -> COOL, command sent
        (29, True),    # repeated percept -> COOL, no command
        (20, True),    # boundary 20 -> IDLE (transition)
        (26, True),    # boundary 26 -> IDLE, no command
        (19, True),    # transition -> WARM
        (29, False),   # empty room -> ECO (priority over temperature)
        (15, False),   # still empty -> ECO, no command
    ]
    print(f"{'step':<5}{'prev mode':<11}{'percept':<14}{'target':<8}outcome")
    for step, percept in enumerate(percepts, 1):
        prev = agent.previous_mode
        target, send = agent.act(*percept)
        outcome = "SEND COMMAND" if send else "no command"
        print(f"{step:<5}{str(prev):<11}{str(percept):<14}{target:<8}{outcome}")
