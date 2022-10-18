"""
Setup expectations for test sub classes
Run discovery for as a prerequisite for most tests
"""
import os
import uuid
from datetime import datetime as dt
from datetime import timedelta

from tap_tester import connections, menagerie, runner, LOGGER
from tap_tester.base_suite_tests.base_case import BaseCase


class GA4Base(BaseCase):
    """
    Setup expectations for test sub classes.
    Metadata describing streams.

    A bunch of shared methods that are used in tap-tester tests.
    Shared tap-specific methods (as needed).
    """
    HASHED_KEYS = "default-hashed-keys"
    REPLICATION_KEY_FORMAT = "%Y-%m-%dT00:00:00.000000Z"

    start_date = ""

    @staticmethod
    def tap_name():
        """The name of the tap"""
        return "tap-ga4"

    @staticmethod
    def get_type():
        """the expected url route ending"""
        return "platform.ga4"

    def get_properties(self, original: bool = True):
        """Configuration properties required for the tap."""
        return_value = {
            'start_date': (dt.utcnow() - timedelta(days=3)).strftime(self.START_DATE_FORMAT),
            'property_id': os.getenv('TAP_GA4_PROPERTY_ID'),
            'account_id': '659787',
            'oauth_client_id': os.getenv('TAP_GA4_CLIENT_ID'),
            'user_id': os.getenv('TAP_GA4_USER_ID'), # TODO what is?  should orca handle this?
            'report_definitions': [
                {"id": str(uuid.uuid4()), "name": "Test Report 1"},
                {"id": str(uuid.uuid4()), "name": "Test Report 2"},
            ]
        }
        if original:
            return return_value

        return_value["start_date"] = self.start_date
        return return_value

    @staticmethod
    def get_credentials():
        return {
            'oauth_client_secret': os.getenv('TAP_GA4_CLIENT_SECRET'),
            'access_token': os.getenv('TAP_GA4_ACCESS_TOKEN'),
            'refresh_token': os.getenv('TAP_GA4_REFRESH_TOKEN'),
        }

    def expected_metadata(self):
        """The expected streams and metadata about the streams"""
        default_expectations = {
            self.HASHED_KEYS: { # TODO also sorted dimensions and values...
                'account_id',
                'property_id',
                # 'end_date',
            },
            self.PRIMARY_KEYS: {"_sdc_record_hash"},
            self.REPLICATION_METHOD: self.INCREMENTAL,
            self.REPLICATION_KEYS: {"date"},
            self.RESPECTS_START_DATE: True,
        }

        return {
            'Test Report 1': default_expectations, # TODO stitch QA generated, necessary?
            'Test Report 2': {      # TODO stitch QA generated, necessary?
                self.HASHED_KEYS: { # TODO also sorted dimensions and values...
                    'account_id',
                    'property_id',
                },
                self.PRIMARY_KEYS: {"_sdc_record_hash"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
                self.REPLICATION_KEYS: {"date"},
                self.RESPECTS_START_DATE: False,
            },
            'content_group_report': default_expectations,
            'demographic_region_report': default_expectations,
            'demographic_age_report': default_expectations,
            'traffic_acq_session_source_and_medium_report': default_expectations,
            'conversions_report': {
                self.HASHED_KEYS: { # TODO also sorted dimensions and values...
                    'account_id',
                    'property_id',
                },
                self.PRIMARY_KEYS: {"_sdc_record_hash"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
                self.REPLICATION_KEYS: {"date"},
                self.RESPECTS_START_DATE: True, # Updating here does not change tap behavior
            },
            'traffic_acq_session_source_platform_report': default_expectations,
            'tech_screen_resolution_report': default_expectations,
            'demographic_interests_report': default_expectations,
            'tech_operating_system_report': default_expectations,
            'ecommerce_purchases_item_category_4_report': default_expectations,
            'demographic_city_report': default_expectations,
            'demographic_gender_report': default_expectations,
            'events_report': default_expectations,
            'traffic_acq_session_source_report': default_expectations,
            'publisher_ads_ad_format_report': default_expectations,
            'traffic_acq_session_medium_report': default_expectations,
            'tech_browser_report': default_expectations,
            'publisher_ads_ad_source_report': default_expectations,
            'traffic_acq_session_campaign_report': default_expectations,
            'user_acq_first_user_google_ads_ad_group_name_report': default_expectations,
            'demographic_language_report': default_expectations,
            'tech_os_with_version_report': default_expectations,
            'ecommerce_purchases_item_category_3_report': default_expectations,
            'user_acq_first_user_source_and_medium_report': default_expectations,
            'ecommerce_purchases_item_name_report': default_expectations,
            'tech_os_version_report': default_expectations,
            'pages_title_and_screen_class_report': default_expectations,
            'tech_device_category_report': default_expectations,
            'tech_platform_report': default_expectations,
            'demographic_country_report': default_expectations,
            'ecommerce_purchases_item_category_5_report': default_expectations,
            'user_acq_first_user_source_platform_report': default_expectations,
            'tech_device_model_report': default_expectations,
            'publisher_ads_page_path_report': default_expectations,
            'user_acq_first_user_google_ads_network_type_report': default_expectations,
            'user_acq_first_user_source_report': default_expectations,
            'pages_path_report': default_expectations,
            'pages_title_and_screen_name_report': default_expectations,
            'ecommerce_purchases_item_category_2_report': default_expectations,
            'ecommerce_purchases_item_id_report': default_expectations,
            'publisher_ads_ad_unit_report': default_expectations,
            'tech_platform_and_device_category_report': default_expectations,
            'user_acq_first_user_campaign_report': default_expectations,
            'ecommerce_purchases_item_brand_report': default_expectations,
            'traffic_acq_session_default_channel_grouping_report': default_expectations,
            'ecommerce_purchases_item_category_1_report': default_expectations,
            'tech_app_version_report': default_expectations,
            'user_acq_first_user_medium_report': default_expectations,
            'ecommerce_purchases_item_category_combined_report': default_expectations,
            # TODO what predefined are we supporting?
        }

    def expected_hashed_keys(self):
        """
        return a dictionary with key of table name
        and value as a set of hashed key fields used to form the primary key
        """
        return {table: properties.get(self.HASHED_KEYS, set())
                for table, properties
                in self.expected_metadata().items()}

    def expected_automatic_fields(self):
        auto_fields = {}
        for k, v in self.expected_metadata().items():
            auto_fields[k] = v.get(self.PRIMARY_KEYS, set()) | v.get(self.REPLICATION_KEYS, set()) \
                | v.get(self.HASHED_KEYS, set())

        return auto_fields

    @classmethod
    def setUpClass(cls):
        super().setUpClass(logging="Ensuring environment variables are sourced.")
        missing_envs = [
            x for x in [
                'TAP_GA4_PROPERTY_ID',
                'TAP_GA4_CLIENT_SECRET',
                'TAP_GA4_CLIENT_ID',
                'TAP_GA4_ACCESS_TOKEN',
                'TAP_GA4_REFRESH_TOKEN',
                'TAP_GA4_USER_ID',
            ] if os.getenv(x) is None
        ]

        if len(missing_envs) != 0:
            raise Exception("Missing environment variables: {}".format(missing_envs))

    ##########################################################################
    ### Tap Specific Methods
    ##########################################################################

    @staticmethod
    def expected_default_fields():
        """

        TODO setup a standard custom report to start iterating through tests
        TODO need to determine how to cover all metrics and dimensions via custom reports.
        TODO need to determine if there are any specific combinations that need to be covered
             (combinations that may later be used as pre-defiined reports?)

        GA4 NOTES:
          Segment are based on dimensions and metrics
           - Users: People interact with your property (e.g., your website or app)
           - Sessions: Interactions by a single user are grouped into sessions.
           - Hits: Interactions during a session are referred to as hits. Hits include interactions like pageviews, events, and transactions.

          Dimensions are data attributes like City, Browser, PAGE, etc.

          Metrics are quantitative measures like Clicks, Sessions, Pages per Session, etc.



        NOTE: See method in tap-google-analytics/tests/base.py
        """
        return {
            "Test Report 1": {'date',
                              'city',
                              'browser',
                              'bounceRate',
                              'checkouts'},
            "Test Report 2": {'source',
                              'streamId',
                              'conversions'},
        }

    @staticmethod
    def expected_pagination_fields(): # TODO does this apply?
        return {
            "Test Report 1" : set(),
            "Audience Overview": {
                "ga:users", "ga:newUsers", "ga:sessions", "ga:sessionsPerUser", "ga:pageviews",
                "ga:pageviewsPerSession", "ga:sessionDuration", "ga:bounceRate", "ga:date",
                # "ga:pageviews",
            },
            "Audience Geo Location": set(),
            "Audience Technology": set(),
            "Acquisition Overview": set(),
            "Behavior Overview": set(),
            "Ecommerce Overview": set(),
        }

    def custom_reports_names_to_ids(self): # TODO does this apply?
        report_definitions =self.get_properties()['report_definitions']
        name_to_id_map = {
            definition.get('name'): definition.get('id')
            for definition in report_definitions
        }

        return name_to_id_map

    # TODO this will apply but not yet. And the standard list will likely be different
    # @staticmethod
    # def is_custom_report(stream):
    #     standard_reports = {
    #         "Audience Overview",
    #         "Audience Geo Location",
    #         "Audience Technology",
    #         "Acquisition Overview",
    #         "Behavior Overview",
    #         "Ecommerce Overview",
    #     }
    #     return stream not in standard_reports

    @staticmethod
    def custom_report_minimum_valid_field_selection():
        """
        The uncommented dimensions and metrics are sufficient for the current test suite.
        In the future consider mixing up the selection to increase test covereage.
        See TODO header at top of file.
        """
        return {
            'Test Report 1': {
                #"ga:sessions",  # Metric
                "ga:avgSessionDuration",  # Metric
                "ga:bounceRate",  # Metric
                "ga:users",  # Metric
                # "ga:pagesPerSession",  # Metric
                "ga:avgTimeOnPage",  # Metric
                "ga:bounces",  # Metric
                "ga:hits",  # Metric
                "ga:sessionDuration",  # Metric
                "ga:newUsers",  # Metric
                "ga:deviceCategory",  # Dimension
                # "ga:eventAction",  # Dimension
                "ga:date",  # Dimension
                # "ga:eventLabel",  # Dimension
                # "ga:eventCategory"  # Dimension
            },
        }


    @staticmethod
    def select_all_streams_and_fields(conn_id, catalogs, select_all_fields: bool = True):
        """Select all streams and all fields within streams"""
        for catalog in catalogs:
            schema = menagerie.get_annotated_schema(conn_id, catalog['stream_id'])

            non_selected_properties = []
            if not select_all_fields:
                # get a list of all properties so that none are selected
                non_selected_properties = schema.get('annotated-schema', {}).get(
                    'properties', {}).keys()

            connections.select_catalog_and_fields_via_metadata(
                conn_id, catalog, schema, [], non_selected_properties)


    def perform_and_verify_table_and_field_selection(self,
                                                     conn_id,
                                                     test_catalogs,
                                                     select_all_fields=True):
        """
        Perform table and field selection based off of the streams to select
        set and field selection parameters.
        Verify this results in the expected streams selected and all or no
        fields selected for those streams.
        TODO update to account for field exclusions
        """

        # Select all available fields or select no fields from all testable streams
        self.select_all_streams_and_fields(
            conn_id=conn_id, catalogs=test_catalogs, select_all_fields=select_all_fields
        )

        catalogs = menagerie.get_catalogs(conn_id)

        # Ensure our selection affects the catalog
        expected_selected = [tc.get('stream_name') for tc in test_catalogs]
        for cat in catalogs:
            catalog_entry = menagerie.get_annotated_schema(conn_id, cat['stream_id'])

            # Verify all testable streams are selected
            selected = catalog_entry.get('annotated-schema').get('selected')
            print("Validating selection on {}: {}".format(cat['stream_name'], selected))
            if cat['stream_name'] not in expected_selected:
                self.assertFalse(selected, msg="Stream selected, but not testable.")
                continue # Skip remaining assertions if we aren't selecting this stream
            self.assertTrue(selected, msg="Stream not selected.")

            if select_all_fields:
                # Verify all fields within each selected stream are selected
                for field, field_props in catalog_entry.get('annotated-schema').get('properties').items():
                    field_selected = field_props.get('selected')
                    print("\tValidating selection on {}.{}: {}".format(
                        cat['stream_name'], field, field_selected))
                    self.assertTrue(field_selected, msg="Field not selected.")
            else:
                # Verify only automatic fields are selected
                expected_automatic_fields = self.expected_automatic_fields().get(cat['stream_name'])
                selected_fields = self.get_selected_fields_from_metadata(catalog_entry['metadata'])
                self.assertEqual(expected_automatic_fields, selected_fields)
