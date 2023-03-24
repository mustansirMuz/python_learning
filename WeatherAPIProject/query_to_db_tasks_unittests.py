import unittest

import query_to_db_tasks


class TestTasks(unittest.TestCase):
    def test_task1(self):
        self.assertEqual(
            query_to_db_tasks.get_hottest_day("karachi", 14),
            {
                "highest_peak_temp_datetime": "2023-04-04 14:00:00",
                "highest_peak_temp": 32.5,
            },
        )
        self.assertEqual(
            query_to_db_tasks.get_hottest_day("karachi", 5),
            {
                "highest_peak_temp_datetime": "2023-03-26 13:00:00",
                "highest_peak_temp": 31.6,
            },
        )
        self.assertEqual(
            query_to_db_tasks.get_hottest_day("lahore", 14),
            {
                "highest_peak_temp_datetime": "2023-03-30 14:00:00",
                "highest_peak_temp": 38.0,
            },
        )
        self.assertEqual(
            query_to_db_tasks.get_hottest_day("lahore", 5),
            {
                "highest_peak_temp_datetime": "2023-03-29 14:00:00",
                "highest_peak_temp": 36.1,
            },
        )
        with self.assertRaises(Exception):
            query_to_db_tasks.get_hottest_day("dummy_city", 14)
            query_to_db_tasks.get_hottest_day("karachi", -5)

    def test_task2(self):
        self.assertEqual(
            query_to_db_tasks.get_second_most_humid_city(),
            {"second_most_humid_city": "Islamabad", "humidity_percent": 45.66},
        )

    def test_task3(self):
        self.assertEqual(
            query_to_db_tasks.get_lowest_average_daily_temp_difference(5),
            {"city": "Karachi", "average_daily_temperature_difference": 5.98},
        )
        self.assertEqual(
            query_to_db_tasks.get_lowest_average_daily_temp_difference(14),
            {"city": "Karachi", "average_daily_temperature_difference": 6.25},
        )
        with self.assertRaises(Exception):
            query_to_db_tasks.get_lowest_average_daily_temp_difference(0)
            query_to_db_tasks.get_lowest_average_daily_temp_difference(-8)

    def test_task4(self):
        self.assertEqual(
            query_to_db_tasks.get_day_with_highest_daily_temp_difference("karachi"),
            {
                "date_with_highest_temperature_difference": "2023-03-26 00:00:00",
                "highest_temperate": 31.6,
                "lowest_temperature": 22.8,
            },
        )
        self.assertEqual(
            query_to_db_tasks.get_day_with_highest_daily_temp_difference("lahore"),
            {
                "date_with_highest_temperature_difference": "2023-03-30 00:00:00",
                "highest_temperate": 38.0,
                "lowest_temperature": 20.1,
            },
        )
        self.assertEqual(
            query_to_db_tasks.get_day_with_highest_daily_temp_difference("islamabad"),
            {
                "date_with_highest_temperature_difference": "2023-03-26 00:00:00",
                "highest_temperate": 28.2,
                "lowest_temperature": 10.2,
            },
        )
        with self.assertRaises(Exception):
            query_to_db_tasks.get_day_with_highest_daily_temp_difference("dummy city")


if __name__ == "__main__":
    unittest.main()
