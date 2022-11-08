from collections import defaultdict
from random import choice
import json
import os
import unittest
from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from tap_tester import menagerie, runner
from tap_tester.logger import LOGGER
from datetime import datetime as dt
from datetime import timedelta
from base import GA4Base


class GA4AllFieldsTest(AllFieldsTest, GA4Base):
    """GA4 all fields test implementation """


    fields = None


    @staticmethod
    def name():
        return "tt_ga4_all_fields"


    def streams_to_test(self):
        # testing all streams creates massive quota issues
        custom_id = self.custom_reports_names_to_ids()['Test Report 1']
        return {
            custom_id
        }


    def streams_to_selected_fields(self):
        if not self.fields:
            self.fields = self.select_random_fields()
        return {
            "Test Report 1": self.fields
        }


    def get_field_exclusions(self):
        field_exclusions = {'DIMENSION': {}, 'METRIC': {}}
        for field in self.schema['metadata']:
            behavior = field['metadata'].get('behavior')

            if field['breadcrumb'] == [] or (behavior != 'DIMENSION' and behavior != 'METRIC'):
                continue

            field_name = field['breadcrumb'][1]
            field_exclusions[behavior][field_name] = set(field['metadata'].get('fieldExclusions'))

        return field_exclusions


    def select_random_fields(self):
        all_field_exclusions = set()
        selected_dimensions = set()
        selected_metrics = set()

        field_exclusions = self.get_field_exclusions()

        # date is always selected, include its field_exclusions
        all_field_exclusions.update(field_exclusions['DIMENSION']['date'])
        all_field_exclusions.update('date')

        all_dimensions = list(field_exclusions['DIMENSION'].keys())
        all_metrics = list(field_exclusions['METRIC'].keys())

        # select fewer dimensions to increase chance of replicating data
        while len(selected_dimensions) < 4 or len(selected_metrics) < 10:
            random_dimension = choice(all_dimensions)
            random_metric = choice(all_metrics)

            if random_dimension not in all_field_exclusions and random_dimension not in selected_dimensions and len(selected_dimensions) < 8:
                selected_dimensions.add(random_dimension)
                all_field_exclusions.update(field_exclusions['DIMENSION'][random_dimension])

            if random_metric not in all_field_exclusions and random_metric not in selected_metrics and len(selected_metrics) < 10:
                selected_metrics.add(random_metric)
                all_field_exclusions.update(field_exclusions['METRIC'][random_metric])

            #TODO check if there are no possible dimensions/metrics left
            #     this may not be an issue depending on how widespread
            #     field exclusions actaully are

        return selected_dimensions | selected_metrics


    ##########################################################################
    ### Overridden Methods
    ##########################################################################


    # Removes assertion that each stream syncs records
    # No guarantee random selection will sync records
    def run_and_verify_sync_mode(self, conn_id):
        """
        Run a sync job and make sure it exited properly.
        Return a dictionary with keys of streams synced
        and values of records synced for each stream
        """
        # Run a sync job using orchestrator
        sync_job_name = runner.run_sync_mode(self, conn_id)

        # Verify tap and target exit codes
        exit_status = menagerie.get_exit_status(conn_id, sync_job_name)
        menagerie.verify_sync_exit_status(self, exit_status, sync_job_name)

        sync_record_count = runner.examine_target_output_file(
             self, conn_id, self.expected_stream_names(), self.expected_primary_keys())
        LOGGER.info("total replicated row count: %s", sum(sync_record_count.values()))

        return sync_record_count


    ##########################################################################
    ### Tests To Skip
    ##########################################################################


    @unittest.skip("Random selection doesn't always sync records")
    def test_all_streams_sync_records(self):
        pass


    def __init__(self, test_run):
        super().__init__(test_run)
