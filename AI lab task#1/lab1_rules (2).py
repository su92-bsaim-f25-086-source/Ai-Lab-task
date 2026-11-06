"""Lab 1 - Task 2: transparent rule-based scholarship screening.

All thresholds below are SYNTHETIC LAB ASSUMPTIONS, not real policy.
Review = flag for a human reviewer, NOT an award decision.

Rules (all must be true for "Review"):
  1. score >= 70                      (kept from the lab manual)
  2. documents_complete is True       (kept from the lab manual)
  3. attendance >= 75                 (new condition: attendance_ok)
  4. no_disciplinary_flag is True     (new condition: clean_record)
"""

SCORE_MIN = 70
ATTENDANCE_MIN = 75


def rule_based(score, documents_complete, attendance, no_disciplinary_flag):
    """Return (decision, reason). Reason names the first failed rule."""
    if score < SCORE_MIN:
        return "Hold", f"score {score} < {SCORE_MIN}"
    if not documents_complete:
        return "Hold", "documents incomplete"
    if attendance < ATTENDANCE_MIN:
        return "Hold", f"attendance {attendance}% < {ATTENDANCE_MIN}%"
    if not no_disciplinary_flag:
        return "Hold", "disciplinary flag present"
    return "Review", "all rules satisfied"


# (name, score, documents_complete, attendance, no_disciplinary_flag, expected)
TESTS = [
    ("pass_case", 82, True, 90, True, "Review"),
    ("fail_attendance", 85, True, 60, True, "Hold"),
    ("fail_clean_record", 88, True, 92, False, "Hold"),
    ("boundary_case", 70, True, 75, True, "Review"),
]


def main():
    all_ok = True
    for name, score, docs, att, clean, expected in TESTS:
        actual, reason = rule_based(score, docs, att, clean)
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"Case: {name}")
        print(f"  Input   : score={score}, docs_complete={docs}, "
              f"attendance={att}, no_disciplinary_flag={clean}")
        print(f"  Expected: {expected}")
        print(f"  Actual  : {actual}")
        print(f"  Reason  : {reason}")
        print(f"  Result  : {'PASS' if ok else 'FAIL'}")
        print()
    print("All 4 tests passed" if all_ok else "Some tests FAILED")


if __name__ == "__main__":
    main()
