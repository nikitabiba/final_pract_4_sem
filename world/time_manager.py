class TimeManager:
    def __init__(self, ticks_per_phase, phases=['morning', 'day', 'evening', 'night'], current_phase='morning', tick_counter=0):
        self.current_phase = current_phase
        self.tick_counter = tick_counter
        self.ticks_per_phase = ticks_per_phase
        self.phases = phases

    def advance_time(self):
        self.tick_counter += 1
        if self.tick_counter >= self.ticks_per_phase:
            self.tick_counter = 0
            self.current_phase = self.phases[(self.phases.index(self.current_phase) + 1) % len(self.phases)]
