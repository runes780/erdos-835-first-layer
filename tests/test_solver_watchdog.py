import unittest

from src.solver_watchdog import (
    LogSummary,
    choose_followup_labels,
    decide_next_action,
    parse_log_text,
)


class SolverWatchdogTests(unittest.TestCase):
    def test_parse_log_text_extracts_status_and_last_conflict(self):
        summary = parse_log_text(
            "portfolio_extra_6h_luby200.log",
            "\n".join(
                [
                    "c #Conflicts:    1000 | #Constraints:     702976",
                    "c #Conflicts:    2500 | #Constraints:     704476",
                    "s UNKNOWN",
                ]
            ),
            size_bytes=123,
            modified_time="2026-06-01 01:00:00",
        )

        self.assertEqual(summary.label, "luby200")
        self.assertEqual(summary.status, "s UNKNOWN")
        self.assertEqual(summary.conflicts, 2500)
        self.assertEqual(summary.constraints, 704476)

    def test_choose_followup_labels_keeps_fastest_and_adds_combo_variants(self):
        summaries = [
            LogSummary(label="count0", path="a", status="", conflicts=4_000, constraints=1),
            LogSummary(label="lubybase15", path="b", status="", conflicts=7_000, constraints=1),
            LogSummary(label="luby200", path="c", status="", conflicts=5_000, constraints=1),
        ]

        labels = choose_followup_labels(summaries, max_jobs=4)

        self.assertEqual(labels[:2], ["lubybase15", "luby200"])
        self.assertEqual(len(labels), 4)
        self.assertIn("count0_luby50", labels)

    def test_decide_next_action_waits_while_solver_processes_are_running(self):
        action = decide_next_action(
            summaries=[],
            running_process_count=3,
            completed_followups=0,
            max_followups=1,
            followup_enabled=True,
        )

        self.assertEqual(action, "wait")

    def test_decide_next_action_launches_once_after_unknown_timeout(self):
        summaries = [
            LogSummary(label="baseline", path="a", status="s UNKNOWN", conflicts=1, constraints=1)
        ]

        action = decide_next_action(
            summaries=summaries,
            running_process_count=0,
            completed_followups=0,
            max_followups=1,
            followup_enabled=True,
        )

        self.assertEqual(action, "launch_followup")

    def test_decide_next_action_stops_on_solver_result(self):
        summaries = [
            LogSummary(label="baseline", path="a", status="s SATISFIABLE", conflicts=1, constraints=1)
        ]

        action = decide_next_action(
            summaries=summaries,
            running_process_count=0,
            completed_followups=0,
            max_followups=1,
            followup_enabled=True,
        )

        self.assertEqual(action, "stop_result")


if __name__ == "__main__":
    unittest.main()
