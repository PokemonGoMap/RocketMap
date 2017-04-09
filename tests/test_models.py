import unittest
import datetime
import logging

from pogom import models

logging.basicConfig(format='%(asctime)s [%(threadName)16s][%(module)14s]'
                           '[%(levelname)8s] %(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def add_query_entry(query, encounter_id, day, hour, minute, second):
    query.append({
        'encounter_id': encounter_id,
        'scan_time': datetime.datetime(2017, 1, day, hour, minute, second)
    })


def get_spawnpoint():
    sp = {
        'id': '1',
        'latitude': 0,
        'longitude': 0,
        'last_scanned': None,  # Null value used as new flag
        'kind': 'hhhs',
        'links': '????',
        'missed_count': 0,
        'latest_seen': 0,
        'earliest_unseen': None
    }

    models.SpawnpointDetectionData.set_default_earliest_unseen(sp)

    return sp


class ModelsTest(unittest.TestCase):
    def test_classify_hhhs(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 14:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)

        add_query_entry(query, '2', 11, 19, 0, 0)
        add_query_entry(query, '2', 11, 19, 14, 59)

        add_query_entry(query, '3', 11, 20, 0, 0)
        add_query_entry(query, '3', 11, 20, 14, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hhhs')
        self.assertEqual(sp['links'], 'hhh?')
        self.assertEqual(sp['latest_seen'], 14 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'], 14 * 60)

    def test_classify_hhss(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 29:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)
        add_query_entry(query, '1', 11, 18, 29, 59)

        add_query_entry(query, '2', 11, 19, 0, 0)
        add_query_entry(query, '2', 11, 19, 14, 59)
        add_query_entry(query, '2', 11, 19, 29, 59)

        add_query_entry(query, '3', 11, 20, 0, 0)
        add_query_entry(query, '3', 11, 20, 14, 59)
        add_query_entry(query, '3', 11, 20, 29, 59)

        sp['earliest_unseen'] = 0

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hhss')
        self.assertEqual(sp['links'], 'hh??')
        self.assertEqual(sp['latest_seen'], 29 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_hsss(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 44:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)
        add_query_entry(query, '1', 11, 18, 29, 59)
        add_query_entry(query, '1', 11, 18, 44, 59)

        add_query_entry(query, '2', 11, 19, 0, 0)
        add_query_entry(query, '2', 11, 19, 14, 59)
        add_query_entry(query, '2', 11, 19, 29, 59)
        add_query_entry(query, '2', 11, 19, 44, 59)

        add_query_entry(query, '3', 11, 20, 0, 0)
        add_query_entry(query, '3', 11, 20, 14, 59)
        add_query_entry(query, '3', 11, 20, 29, 59)
        add_query_entry(query, '3', 11, 20, 44, 59)

        sp['earliest_unseen'] = 0

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hsss')
        self.assertEqual(sp['links'], 'h???')
        self.assertEqual(sp['latest_seen'], 44 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_hshs(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 14:59, then
        from 30:00 to 44:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)
        add_query_entry(query, '1', 11, 18, 30, 00)
        add_query_entry(query, '1', 11, 18, 44, 59)

        add_query_entry(query, '2', 11, 19, 0, 0)
        add_query_entry(query, '2', 11, 19, 14, 59)
        add_query_entry(query, '2', 11, 19, 30, 00)
        add_query_entry(query, '2', 11, 19, 44, 59)

        add_query_entry(query, '3', 11, 20, 0, 0)
        add_query_entry(query, '3', 11, 20, 14, 59)
        add_query_entry(query, '3', 11, 20, 30, 00)
        add_query_entry(query, '3', 11, 20, 44, 59)

        sp['latest_seen'] = 44 * 60 + 59
        sp['earliest_unseen'] = 15 * 60

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hshs')
        self.assertEqual(sp['links'], 'h?h?')
        self.assertEqual(sp['latest_seen'], 44 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_1x60_1(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 58:59
        """
        sp = get_spawnpoint()

        query = []

        for minute in range(0, 59, 14):
            add_query_entry(query, '1', 11, 18, minute, 0)
        add_query_entry(query, '1', 11, 18, 58, 59)

        for minute in range(0, 59, 14):
            add_query_entry(query, '2', 11, 19, minute, 0)
        add_query_entry(query, '2', 11, 19, 58, 59)

        add_query_entry(query, '3', 11, 20, 0, 0)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['latest_seen'], 3600 - 61)
        self.assertEqual(sp['earliest_unseen'], 0)
        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')

    def test_classify_1x60_2(self):
        """
        Test a more difficult one where different spawnpoints overlap different
        times
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)

        add_query_entry(query, '2', 11, 19, 15, 0)
        add_query_entry(query, '2', 11, 19, 29, 59)

        add_query_entry(query, '3', 11, 20, 30, 0)
        add_query_entry(query, '3', 11, 20, 44, 59)

        add_query_entry(query, '4', 11, 21, 45, 0)
        add_query_entry(query, '4', 11, 21, 58, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 3600 - 61)
        self.assertEqual(sp['earliest_unseen'], 0)

    def test_classify_1x60_3(self):
        """
        Test a difficult one where different spawnpoints overlap different
        times
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 12, 59)
        add_query_entry(query, '1', 11, 18, 18, 59)
        add_query_entry(query, '1', 11, 18, 55, 59)

        add_query_entry(query, '2', 11, 20, 30, 0)
        add_query_entry(query, '2', 11, 20, 46, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 55 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'], 0)

    def test_classify_1x60_4(self):
        """
        Real life scenario.
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 19, 14, 07)
        add_query_entry(query, '1', 11, 19, 36, 55)
        add_query_entry(query, '1', 11, 19, 48, 54)
        add_query_entry(query, '1', 11, 20, 00, 36)
        add_query_entry(query, '2', 11, 20, 24, 32)
        add_query_entry(query, '2', 11, 20, 26, 51)
        add_query_entry(query, '2', 11, 20, 26, 51)
        add_query_entry(query, '2', 11, 20, 29, 29)
        add_query_entry(query, '2', 11, 20, 38, 33)
        add_query_entry(query, '2', 11, 20, 39, 23)
        add_query_entry(query, '2', 11, 20, 49, 58)
        add_query_entry(query, '2', 11, 21, 01, 48)
        add_query_entry(query, '2', 11, 21, 02, 39)

        # this should be the latest time (latest_seen)
        add_query_entry(query, '3', 12, 16, 11, 21)
        # this should be the earliest time (earliest_unseen)
        add_query_entry(query, '4', 12, 16, 13, 41)
        add_query_entry(query, '4', 12, 16, 21, 21)
        add_query_entry(query, '4', 12, 16, 23, 42)
        add_query_entry(query, '5', 12, 20, 20, 52)
        add_query_entry(query, '5', 12, 20, 21, 02)
        add_query_entry(query, '5', 12, 20, 30, 54)
        add_query_entry(query, '5', 12, 20, 31, 03)
        add_query_entry(query, '5', 12, 20, 42, 52)
        add_query_entry(query, '5', 12, 20, 42, 54)
        add_query_entry(query, '5', 12, 20, 43, 02)
        add_query_entry(query, '5', 12, 20, 48, 16)
        add_query_entry(query, '5', 12, 20, 54, 53)
        add_query_entry(query, '5', 12, 20, 54, 54)
        add_query_entry(query, '5', 12, 20, 55, 04)
        add_query_entry(query, '5', 12, 21, 01, 48)
        add_query_entry(query, '5', 12, 21, 05, 51)
        add_query_entry(query, '5', 12, 21, 06, 53)
        add_query_entry(query, '5', 12, 21, 07, 02)

        earliest, latest = (models.SpawnpointDetectionData
                            .get_earliest_and_latest_time(query))
        self.assertEqual(earliest, 13 * 60 + 41)
        self.assertEqual(latest, 3600 + 11 * 60 + 21)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 11 * 60 + 21)
        self.assertEqual(sp['earliest_unseen'], 13 * 60 + 41)

    def test_classify_1x60_5(self):
        """
        Real life scenario.
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 19, 14, 07)
        add_query_entry(query, '1', 11, 19, 24, 07)
        add_query_entry(query, '1', 11, 19, 34, 07)
        add_query_entry(query, '1', 11, 19, 44, 07)
        add_query_entry(query, '1', 11, 19, 58, 36)
        add_query_entry(query, '2', 11, 20, 24, 32)
        add_query_entry(query, '2', 11, 20, 34, 32)
        add_query_entry(query, '2', 11, 20, 44, 32)
        add_query_entry(query, '2', 11, 20, 58, 39)

        # this should be the latest time (latest_seen)
        add_query_entry(query, '3', 12, 16, 01, 21)
        # this should be the earliest time (earliest_unseen)
        add_query_entry(query, '4', 12, 16, 03, 41)
        add_query_entry(query, '4', 12, 16, 13, 42)
        add_query_entry(query, '4', 12, 16, 23, 42)
        add_query_entry(query, '5', 12, 20, 20, 52)
        add_query_entry(query, '5', 12, 20, 30, 52)
        add_query_entry(query, '5', 12, 20, 40, 52)
        add_query_entry(query, '5', 12, 20, 59, 02)

        earliest, latest = (models.SpawnpointDetectionData
                            .get_earliest_and_latest_time(query))
        self.assertEqual(earliest, 3 * 60 + 41)
        self.assertEqual(latest, 3600 + 1 * 60 + 21)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], latest % 3600)
        self.assertEqual(sp['earliest_unseen'], earliest % 3600)

    def test_classify_1x60_6(self):
        """
        Test a difficult one where different spawnpoints overlap different
        times
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 11, 18, 0, 0)
        add_query_entry(query, '1', 11, 18, 14, 59)
        add_query_entry(query, '2', 11, 19, 15, 0)
        add_query_entry(query, '2', 11, 19, 29, 59)
        add_query_entry(query, '3', 11, 20, 30, 0)
        add_query_entry(query, '3', 11, 20, 44, 59)
        add_query_entry(query, '4', 11, 20, 55, 0)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 44 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'], 55 * 60)
