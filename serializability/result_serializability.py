from schedule.schedule import Schedule


class ResultSerializability:
    """
    Class used to check result serializability of a schedule.

    For checking result serializability of a schedule, we should consider all permutations of transactions and their
    final result in database. If any of them have same effect on database as given schedule, then given schedule is
    serializable based on result equivalence criteria.
    """

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.serializability_checked = False
        self.serializable_permutation = None
        self.is_serializable = False

    def is_result_serializable(self) -> bool:
        self.serializability_checked = True

        self.is_serializable = False

        return self.is_serializable

    def get_serializable_schedule(self):
        if not self.serializability_checked:
            raise ValueError("Check serializability before getting serializable schedule")
        if not self.is_serializable:
            raise ValueError("Schedule is not result serializable")

        pass
