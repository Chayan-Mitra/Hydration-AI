import time

class HydrationLogic:
    def __init__(self, interval=3600):
        self.interval = interval

        self.last_cycle_time = time.time()
        self.sip_count = 0
        self.required_sips = 3

        self.status = "WAITING ⏳"
        self.active = False

        self.history = []  # 🔥 for graph

    def start_cycle(self):
        self.active = True
        self.sip_count = 0
        self.status = "DRINK WATER 💧"

    def register_sip(self):
        if not self.active:
            return

        self.sip_count += 1

        # 🔥 store data for graph
        self.history.append((time.time(), self.sip_count))

        if self.sip_count >= self.required_sips:
            self.active = False
            self.last_cycle_time = time.time()
            self.status = "GOOD JOB 😎 (SLEEP MODE)"
        else:
            self.status = f"SIP {self.sip_count}/{self.required_sips}"

    def update(self):
        if not self.active:
            elapsed = time.time() - self.last_cycle_time

            if elapsed > self.interval:
                self.start_cycle()
                return "WAKE"

        return None

    def get_remaining_time(self):
        elapsed = time.time() - self.last_cycle_time
        return max(0, int(self.interval - elapsed))