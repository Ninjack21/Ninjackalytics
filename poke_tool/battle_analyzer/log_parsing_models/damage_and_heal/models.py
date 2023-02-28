class Hazards:
    @staticmethod
    def check_hazards(check_string):
        hazards = ["Stealth Rock", "Spikes", "G-Max Steelsurge"]
        for haz in hazards:
            if haz in check_string:
                return True
        return False


class Statuses:
    @staticmethod
    def check_statuses(check_string):
        statuses = ["psn", "brn"]
        for status in statuses:
            if status in check_string:
                return True
        return False
