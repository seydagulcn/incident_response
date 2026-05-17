import unittest
from logic import calculate_mttr, calculate_mttd, calculate_mtbf, format_hours, is_valid_incident, get_severity_label

class TestCalculateMttr(unittest.TestCase):

    def test_valid_mttr(self):
        result = calculate_mttr("2026-05-01T08:00", "2026-05-01T10:00")
        self.assertEqual(result, 2.0)

    def test_resolved_before_detected(self):
        result = calculate_mttr("2026-05-01T10:00", "2026-05-01T08:00")
        self.assertIsNone(result)

    def test_missing_resolved_at(self):
        result = calculate_mttr("2026-05-01T08:00", None)
        self.assertIsNone(result)

    def test_missing_detected_at(self):
        result = calculate_mttr(None, "2026-05-01T10:00")
        self.assertIsNone(result)


class TestCalculateMttd(unittest.TestCase):

    def test_valid_mttd(self):
        result = calculate_mttd("2026-05-01T08:00", "2026-05-01T09:30")
        self.assertEqual(result, 1.5)

    def test_detected_before_started(self):
        result = calculate_mttd("2026-05-01T10:00", "2026-05-01T08:00")
        self.assertIsNone(result)

    def test_missing_started_at(self):
        result = calculate_mttd(None, "2026-05-01T09:00")
        self.assertIsNone(result)

    def test_same_time(self):
        result = calculate_mttd("2026-05-01T08:00", "2026-05-01T08:00")
        self.assertEqual(result, 0.0)


class TestCalculateMtbf(unittest.TestCase):

    def test_valid_mtbf(self):
        result = calculate_mtbf(["2026-05-01T08:00", "2026-05-03T08:00", "2026-05-05T08:00"])
        self.assertEqual(result, 48.0)

    def test_single_incident(self):
        result = calculate_mtbf(["2026-05-01T08:00"])
        self.assertIsNone(result)

    def test_empty_list(self):
        result = calculate_mtbf([])
        self.assertIsNone(result)


class TestFormatHours(unittest.TestCase):

    def test_none_returns_na(self):
        self.assertEqual(format_hours(None), "N/A")

    def test_whole_hours(self):
        self.assertEqual(format_hours(2.0), "2h 0m")

    def test_hours_and_minutes(self):
        self.assertEqual(format_hours(1.5), "1h 30m")

    def test_zero(self):
        self.assertEqual(format_hours(0), "0h 0m")


class TestGetSeverityLabel(unittest.TestCase):

    def test_low(self):
        self.assertEqual(get_severity_label("low"), "Low")

    def test_critical(self):
        self.assertEqual(get_severity_label("critical"), "Critical")

    def test_unknown(self):
        self.assertEqual(get_severity_label("extreme"), "Unknown")

    def test_uppercase_input(self):
        self.assertEqual(get_severity_label("HIGH"), "High")


class TestIsValidIncident(unittest.TestCase):

    def test_valid_incident(self):
        valid, msg = is_valid_incident("DDoS Attack", "DDoS", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertTrue(valid)

    def test_empty_title(self):
        valid, msg = is_valid_incident("", "DDoS", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)

    def test_title_too_short(self):
        valid, msg = is_valid_incident("AB", "DDoS", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)

    def test_title_too_long(self):
        valid, msg = is_valid_incident("A" * 101, "DDoS", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)

    def test_invalid_incident_type(self):
        valid, msg = is_valid_incident("Test Incident", "Hacking", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)

    def test_detected_before_started(self):
        valid, msg = is_valid_incident("Test Incident", "DDoS", "2026-05-01T10:00", "2026-05-01T08:00")
        self.assertFalse(valid)

    def test_invalid_date_format(self):
        valid, msg = is_valid_incident("Test Incident", "DDoS", "01-05-2026", "02-05-2026")
        self.assertFalse(valid)

    def test_invalid_characters_in_title(self):
        valid, msg = is_valid_incident("Test@Incident!", "DDoS", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)

    def test_missing_fields(self):
        valid, msg = is_valid_incident("Test Incident", "", "2026-05-01T08:00", "2026-05-01T09:00")
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()