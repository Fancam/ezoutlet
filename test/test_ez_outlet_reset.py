# Copyright (C) 2015 Schweitzer Engineering Laboratories, Inc.
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.

import unittest
import urllib2

import pytest

try:
    import unittest.mock as mock
except ImportError:
    # mock is required as an extras_require:
    # noinspection PyPackageRequirements
    import mock

from ezoutlet import ez_outlet_reset

EXIT_CODE_ERR = 1
EXIT_CODE_PARSER_ERR = 2
EZ_OUTLET_RESET_DEFAULT_WAIT_TIME = ez_outlet_reset.EzOutletReset.DEFAULT_WAIT_TIME

sample_url = 'DEAD STRINGS TELL NO TALES'


# Suppress since PyCharm doesn't recognize @mock.patch.object
# noinspection PyUnresolvedReferences
@mock.patch.object(ez_outlet_reset, '_get_url', return_value=sample_url)
@mock.patch('ezoutlet.ez_outlet_reset.urllib2')
@mock.patch('ezoutlet.ez_outlet_reset.time')
class TestEzOutletReset(unittest.TestCase):
    """
    EzOutletReset.post_fail is basically all side-effects, so its test is
    rather heavy in mocks.
    """
    expected_response_contents = ez_outlet_reset.EzOutletReset.EXPECTED_RESPONSE_CONTENTS

    def setup_method(self, _):
        self.hostname = '12.34.56.78'
        self.dut_reset_delay = 12.34
        self.reset_delay = 3.21
        self.timeout = 11.12
        self.uut = ez_outlet_reset.EzOutletReset(hostname=self.hostname,
                                                 timeout=self.timeout)

    def configure_mock_urllib2(self, mock_urllib2):
        mock_urllib2.configure_mock(
                **{'urlopen.return_value': mock.MagicMock(
                        **{'read.return_value': self.expected_response_contents})})

    def test_reset_get(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns expected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: ez_outlet_reset._get_url is called using the IP address with ez_outlet_reset.RESET_URL_PATH.
         and: urllib2.urlopen(ez_outlet_reset._get_url's result, timeout) is called.
        """
        _ = mock_time

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                       ez_outlet_reset_interval=self.reset_delay)

        # Then
        mock_get_url.assert_called_with(self.hostname, ez_outlet_reset.EzOutletReset.RESET_URL_PATH)
        mock_urllib2.urlopen.assert_called_once_with(sample_url, timeout=self.timeout)

    def test_reset_result(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns expected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: expected_response_contents is returned.
        """
        _ = mock_time
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        result = self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                                ez_outlet_reset_interval=self.reset_delay)

        # Then
        self.assertEqual(self.expected_response_contents, result)

    def test_reset_sleep(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns expected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: time.sleep(dut_reset_delay + reset_delay) is called.
        """
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                       ez_outlet_reset_interval=self.reset_delay)

        # Then
        mock_time.sleep.assert_called_once_with(self.dut_reset_delay + self.reset_delay)


# Suppress since PyCharm doesn't recognize @mock.patch.object
# noinspection PyUnresolvedReferences
@mock.patch.object(ez_outlet_reset, '_get_url', return_value=sample_url)
@mock.patch('ezoutlet.ez_outlet_reset.urllib2')
@mock.patch('ezoutlet.ez_outlet_reset.time')
class TestEzOutletResetNoResponse(unittest.TestCase):
    """
    EzOutletReset.post_fail is basically all side-effects, so its test is
    rather heavy in mocks.
    """

    def setup_method(self, _):
        self.hostname = '12.34.56.78'
        self.dut_reset_delay = 12.34
        self.reset_delay = 3.21
        self.timeout = 11.12
        self.uut = ez_outlet_reset.EzOutletReset(hostname=self.hostname,
                                                 timeout=self.timeout)

    def configure_mock_urllib2(self, mock_urllib2):
        mock_urllib2.configure_mock(**{'urlopen.side_effect': urllib2.URLError("Dummy reason")})
        mock_urllib2.URLError = urllib2.URLError  # Restore mocked-away URLError

    def test_reset_no_response_get(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured to raise urllib2.URLError on urlopen.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: ez_outlet_reset._get_url is called using the IP address with ez_outlet_reset.RESET_URL_PATH.
         and: urllib2.urlopen(ez_outlet_reset._get_url's result, timeout) is called.
        """
        _ = mock_time

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        try:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)
        except ez_outlet_reset.EzOutletResetError:
            pass  # exception tested elsewhere

        # Then
        mock_get_url.assert_called_with(self.hostname, ez_outlet_reset.EzOutletReset.RESET_URL_PATH)
        mock_urllib2.urlopen.assert_called_once_with(sample_url, timeout=self.timeout)

    def test_reset_no_response_raise(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured to raise urllib2.URLError on urlopen.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: reset() raises ez_outlet_reset.EzOutletResetError, e.
         and: e.message == ez_outlet_reset.EzOutletReset.NO_RESPONSE_MSG.format(timeout).
        """
        _ = mock_time
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        with self.assertRaises(ez_outlet_reset.EzOutletResetError) as e:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)

        # Then
        self.assertEqual(e.exception.message,
                         ez_outlet_reset.EzOutletReset.NO_RESPONSE_MSG.format(self.timeout))

    def test_reset_no_response_no_sleep(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured to raise urllib2.URLError on urlopen.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: time.sleep(dut_reset_delay + reset_delay) is _not_ called.
        """
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        try:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)
        except ez_outlet_reset.EzOutletResetError:
            pass  # exception tested elsewhere

        # Then
        mock_time.sleep.assert_not_called()


# Suppress since PyCharm doesn't recognize @mock.patch.object
# noinspection PyUnresolvedReferences
@mock.patch.object(ez_outlet_reset, '_get_url', return_value=sample_url)
@mock.patch('ezoutlet.ez_outlet_reset.urllib2')
@mock.patch('ezoutlet.ez_outlet_reset.time')
class TestEzOutletResetUnexpectedResponse(unittest.TestCase):
    """
    EzOutletReset.post_fail is basically all side-effects, so its test is
    rather heavy in mocks.
    """

    def setup_method(self, _):
        self.unexpected_response_contents = '1,0'

        self.hostname = '12.34.56.78'
        self.dut_reset_delay = 12.34
        self.reset_delay = 3.21
        self.timeout = 11.12
        self.uut = ez_outlet_reset.EzOutletReset(hostname=self.hostname,
                                                 timeout=self.timeout)

    def configure_mock_urllib2(self, mock_urllib2):
        mock_urllib2.configure_mock(
                **{'urlopen.return_value': mock.MagicMock(
                        **{'read.return_value': self.unexpected_response_contents})})

    def test_reset_unexpected_response_get(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns unexpected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: ez_outlet_reset._get_url is called using the IP address with ez_outlet_reset.RESET_URL_PATH.
         and: urllib2.urlopen(ez_outlet_reset._get_url's result, timeout) is called.
        """
        _ = mock_time

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        try:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)
        except ez_outlet_reset.EzOutletResetError:
            pass  # exception tested elsewhere

        # Then
        mock_get_url.assert_called_with(self.hostname, ez_outlet_reset.EzOutletReset.RESET_URL_PATH)
        mock_urllib2.urlopen.assert_called_once_with(sample_url, timeout=self.timeout)

    def test_reset_unexpected_response_raises(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns unexpected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: reset() raises ez_outlet_reset.EzOutletResetError, e.
         and: e.message == ez_outlet_reset.EzOutletReset.UNEXPECTED_RESPONSE_MSG.format(unexpected_response_contents).
        """
        _ = mock_time
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        with self.assertRaises(ez_outlet_reset.EzOutletResetError) as e:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)

        # Then
        self.assertEqual(e.exception.message,
                         ez_outlet_reset.EzOutletReset.UNEXPECTED_RESPONSE_MSG.format(
                                 self.unexpected_response_contents))

    def test_reset_unexpected_response_no_sleep(self, mock_time, mock_urllib2, mock_get_url):
        """
        Given: Mock urllib2 configured such that
               urlopen returns a mock whose read() method returns unexpected_response_contents.
          and: EzOutletReset initialized with an IP address and timeout.
        When: Calling reset(dut_reset_delay, reset_delay).
        Then: time.sleep(dut_reset_delay + reset_delay) is _not_ called.
        """
        _ = mock_get_url

        # Given
        self.configure_mock_urllib2(mock_urllib2=mock_urllib2)

        # When
        try:
            self.uut.reset(dut_reset_delay=self.dut_reset_delay,
                           ez_outlet_reset_interval=self.reset_delay)
        except ez_outlet_reset.EzOutletResetError:
            pass  # exception tested elsewhere

        # Then
        mock_time.sleep.assert_not_called()


@pytest.mark.parametrize("hostname,expected_url", [('1.2.3.4', 'http://1.2.3.4/reset.cgi')])
def test_url(hostname, expected_url):
    """
    Given: A hostname.
    When: Creating an EzOutletReset using hostname.
    Then: Property `url` returns the expected URL.

    Args:
        hostname: test parameter
        expected_url: test parameter
    """
    uut = ez_outlet_reset.EzOutletReset(hostname=hostname)

    assert expected_url == uut.url
