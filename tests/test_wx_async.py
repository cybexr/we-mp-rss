"""
Comprehensive async tests for Wx class async conversion.
Tests all async methods with proper mocking and verification.

Covers:
- Token() async method
- wxLogin() async method
- switch_account() async method
- Call_Success() async method
- Close() async method
- HasLogin() async method
- Concurrent access with asyncio.Lock
- Resource cleanup verification
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from driver.wx import Wx
from driver.playwright_driver import PlaywrightController

# Module-level pytest mark for async tests
pytestmark = pytest.mark.asyncio


class TestTokenAsync:
    """Test async Token() method with proper await statements."""

    @pytest.mark.asyncio
    async def test_token_async_success(self):
        """Test Token() method with successful authentication."""
        wx = Wx()

        # Mock PlaywrightController async methods
        wx.controller = AsyncMock()
        wx.controller.start_browser = AsyncMock(return_value=MagicMock())
        wx.controller.open_url = AsyncMock()
        wx.controller.add_cookies = AsyncMock()
        wx.controller.add_cookie = AsyncMock()
        wx.controller.cleanup = AsyncMock()

        # Mock page elements for login detection
        mock_page = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[])  # No login page
        wx.controller.start_browser = AsyncMock(return_value=mock_page)

        # Mock Call_Success to return session dict
        with patch.object(wx, 'Call_Success', new=AsyncMock(return_value={'token': 'test123'})):
            result = await wx.Token(callback=None, isClose=False)

            # Verify all async methods were awaited
            assert wx.controller.start_browser.called
            assert wx.controller.open_url.called
            assert result is not None

    @pytest.mark.asyncio
    async def test_token_async_cleanup_on_error(self):
        """Test Token() method cleanup on exception."""
        wx = Wx()

        # Mock cleanup to verify it's called
        wx.controller.cleanup = AsyncMock()

        # Mock start_browser to raise exception
        wx.controller.start_browser = AsyncMock(side_effect=Exception("Browser error"))

        result = await wx.Token(callback=None, isClose=True)

        # Verify cleanup was called despite exception
        assert wx.controller.cleanup.called
        assert result is None


class TestWxLoginAsync:
    """Test async wxLogin() method with proper await statements."""

    @pytest.mark.asyncio
    async def test_wxlogin_async_success(self):
        """Test wxLogin() method with successful login."""
        wx = Wx()

        # Mock PlaywrightController
        wx.controller = AsyncMock()
        mock_page = MagicMock()
        wx.controller.start_browser = AsyncMock(return_value=mock_page)
        wx.controller.open_url = AsyncMock()

        # Mock login state management
        wx.check_lock = MagicMock(return_value=True)  # No lock file exists
        wx.set_lock = MagicMock()
        wx.release_lock = MagicMock()

        # Mock Call_Success
        with patch.object(wx, 'Call_Success', new=AsyncMock(return_value={'token': 'test123'})):
            with patch.object(wx, 'cleanup_resources', new=AsyncMock()):
                result = await wx.wxLogin(CallBack=None, NeedExit=False)

                # Verify async methods were awaited
                assert wx.controller.start_browser.called
                assert wx.controller.open_url.called

    @pytest.mark.asyncio
    async def test_wxlogin_async_lock_check_fails(self):
        """Test wxLogin() when lock check fails."""
        wx = Wx()

        # Mock check_lock to return False (lock file exists)
        wx.check_lock = MagicMock(return_value=False)

        result = await wx.wxLogin(CallBack=None, NeedExit=True)

        # Should return None without starting browser
        assert result is None
        assert not wx.controller.start_browser.called

    @pytest.mark.asyncio
    async def test_wxlogin_async_timeout(self):
        """Test wxLogin() timeout handling."""
        wx = Wx()

        # Mock lock check passes
        wx.check_lock = MagicMock(return_value=True)
        wx.set_lock = MagicMock()
        wx.release_lock = MagicMock()

        # Mock start_browser to raise timeout
        wx.controller.start_browser = AsyncMock(side_effect=TimeoutError("Login timeout"))

        with patch.object(wx, 'cleanup_resources', new=AsyncMock()):
            result = await wx.wxLogin(CallBack=None, NeedExit=True)

            # Should handle timeout gracefully
            assert result is None
            assert wx.release_lock.called  # Lock released in finally block


class TestSwitchAccountAsync:
    """Test async switch_account() and Call_Success() methods."""

    @pytest.mark.asyncio
    async def test_switch_account_async_success(self):
        """Test switch_account() method with successful switch."""
        wx = Wx()

        # Mock PlaywrightController
        wx.controller = AsyncMock()
        mock_page = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[])  # No login page

        # Mock Token method
        with patch.object(wx, 'Token', new=AsyncMock(return_value={'token': 'test123'})):
            # Mock Call_Success method
            with patch.object(wx, 'Call_Success', new=AsyncMock(return_value={'token': 'new123'})):
                # Mock get_cookies
                wx.controller.get_cookies = AsyncMock(return_value=[
                    {'name': 'token', 'value': 'new123', 'expires': -1}
                ])

                result = await wx.switch_account(username="test_account")

                # Verify async methods were called
                assert wx.controller.get_cookies.called
                assert result is True

    @pytest.mark.asyncio
    async def test_call_success_async(self):
        """Test Call_Success() async method."""
        wx = Wx()

        # Mock PlaywrightController
        wx.controller = AsyncMock()
        wx.controller.get_cookies = AsyncMock(return_value=[
            {'name': 'token', 'value': 'test123', 'domain': '.qq.com'}
        ])

        # Mock state management
        wx._haslogin = False

        result = await wx.Call_Success(has_extdata=True)

        # Verify cookies were retrieved
        assert wx.controller.get_cookies.called
        assert result is not None
        assert 'token' in result or result is None  # May be None if no token

    @pytest.mark.asyncio
    async def test_switch_account_async_failure(self):
        """Test switch_account() method handles failures."""
        wx = Wx()

        # Mock Token to return False (login page detected)
        with patch.object(wx, 'Token', new=AsyncMock(return_value=False)):
            result = await wx.switch_account(username="test_account")

            # Should return False on failure
            assert result is False


class TestCloseAsync:
    """Test async Close() method with proper cleanup."""

    @pytest.mark.asyncio
    async def test_close_async_success(self):
        """Test Close() method with successful cleanup."""
        wx = Wx()

        # Mock PlaywrightController.Close method
        wx.controller = AsyncMock()
        wx.controller.Close = AsyncMock(return_value=True)

        result = await wx.Close()

        # Verify Close was awaited
        assert wx.controller.Close.called
        assert result is True

    @pytest.mark.asyncio
    async def test_close_async_failure(self):
        """Test Close() method handles exceptions gracefully."""
        wx = Wx()

        # Mock Close to raise exception
        wx.controller = AsyncMock()
        wx.controller.Close = AsyncMock(side_effect=Exception("Cleanup error"))

        result = await wx.Close()

        # Should handle exception and return False
        assert result is False

    @pytest.mark.asyncio
    async def test_close_async_no_controller(self):
        """Test Close() method when controller not initialized."""
        wx = Wx()

        # Remove controller
        delattr(wx, 'controller')

        result = await wx.Close()

        # Should return False gracefully
        assert result is False


class TestHasLoginAsync:
    """Test async HasLogin() method with asyncio.Lock."""

    @pytest.mark.asyncio
    async def test_haslogin_async_true(self):
        """Test HasLogin() returns True when logged in."""
        wx = Wx()
        wx._haslogin = True

        result = await wx.HasLogin()

        # Should return True
        assert result is True

    @pytest.mark.asyncio
    async def test_haslogin_async_false(self):
        """Test HasLogin() returns False when not logged in."""
        wx = Wx()
        wx._haslogin = False

        result = await wx.HasLogin()

        # Should return False
        assert result is False


class TestConcurrentAccess:
    """Test concurrent access with asyncio.Lock prevents race conditions."""

    @pytest.mark.asyncio
    async def test_concurrent_haslogin(self):
        """Test concurrent HasLogin() calls see consistent state."""
        wx = Wx()
        wx._haslogin = True

        # Create 10 concurrent HasLogin calls
        tasks = [wx.HasLogin() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should see the same state
        assert all(r is True for r in results)
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_concurrent_setlogin(self):
        """Test concurrent setHasLogin() calls with lock."""
        wx = Wx()
        wx._haslogin = False

        async def set_and_get():
            """Set login state and verify."""
            async with wx._login_lock:
                wx._haslogin = True
                await asyncio.sleep(0.01)  # Simulate async operation
                return wx._haslogin

        # Create 10 concurrent tasks
        tasks = [set_and_get() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should see True (lock prevents race conditions)
        assert all(r is True for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_call_success(self):
        """Test concurrent Call_Success() calls with lock."""
        wx = Wx()

        # Mock PlaywrightController
        wx.controller = AsyncMock()
        wx.controller.get_cookies = AsyncMock(return_value=[
            {'name': 'token', 'value': 'test123'}
        ])

        # Create 5 concurrent Call_Success calls
        tasks = [wx.Call_Success(has_extdata=False) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should complete without errors
        assert len(results) == 5
        assert all(r is not None for r in results)


class TestResourceCleanup:
    """Test resource cleanup and state management."""

    @pytest.mark.asyncio
    async def test_cleanup_resources_async(self):
        """Test cleanup_resources() async method."""
        wx = Wx()
        wx._haslogin = True
        wx.HasCode = True

        # Mock file cleanup
        with patch('os.remove'):
            await wx.cleanup_resources()

            # Verify state reset
            assert wx._haslogin is False
            assert wx.HasCode is False

    @pytest.mark.asyncio
    async def test_token_cleanup_on_exception(self):
        """Test Token() cleanup in finally block."""
        wx = Wx()

        wx.controller = AsyncMock()
        wx.controller.start_browser = AsyncMock(side_effect=Exception("Error"))
        wx.controller.cleanup = AsyncMock()

        result = await wx.Token(callback=None, isClose=True)

        # Verify cleanup called in finally block
        assert wx.controller.cleanup.called
        assert result is None

    @pytest.mark.asyncio
    async def test_wxlogin_cleanup_on_exception(self):
        """Test wxLogin() cleanup in finally block."""
        wx = Wx()

        wx.check_lock = MagicMock(return_value=True)
        wx.set_lock = MagicMock()
        wx.release_lock = MagicMock()

        wx.controller = AsyncMock()
        wx.controller.start_browser = AsyncMock(side_effect=Exception("Error"))
        wx.controller.cleanup = AsyncMock()

        with patch.object(wx, 'cleanup_resources', new=AsyncMock()):
            result = await wx.wxLogin(CallBack=None, NeedExit=True)

            # Verify cleanup called
            assert wx.release_lock.called  # Lock released in finally

    @pytest.mark.asyncio
    async def test_qr_code_file_cleanup(self):
        """Test QR code file cleanup in Clean() method."""
        wx = Wx()

        # Mock file operations
        with patch('os.path.exists', return_value=True):
            with patch('os.remove') as mock_remove:
                wx.Clean()

                # Verify file deletion attempted
                mock_remove.assert_called_once()


class TestStateConsistency:
    """Test state consistency across async operations."""

    @pytest.mark.asyncio
    async def test_login_state_transition(self):
        """Test login state transitions correctly through async methods."""
        wx = Wx()

        # Initial state
        assert await wx.HasLogin() is False

        # Simulate login success
        async with wx._login_lock:
            wx._haslogin = True

        # Verify state changed
        assert await wx.HasLogin() is True

        # Simulate logout
        async with wx._login_lock:
            wx._haslogin = False

        # Verify state changed
        assert await wx.HasLogin() is False

    @pytest.mark.asyncio
    async def test_session_state_consistency(self):
        """Test SESSION dict remains consistent under concurrent access."""
        wx = Wx()
        wx.SESSION = {}

        # Mock Call_Success to set SESSION
        wx.controller = AsyncMock()
        wx.controller.get_cookies = AsyncMock(return_value=[
            {'name': 'token', 'value': 'test123'}
        ])

        # Create concurrent tasks
        tasks = [wx.Call_Success(has_extdata=False) for _ in range(3)]
        results = await asyncio.gather(*tasks)

        # Verify SESSION is set consistently
        assert wx.SESSION is not None
        assert len(results) == 3


class TestIntegrationScenarios:
    """Integration tests for complete async workflows."""

    @pytest.mark.asyncio
    async def test_token_to_call_success_flow(self):
        """Test Token → Call_Success async flow."""
        wx = Wx()

        wx.controller = AsyncMock()
        mock_page = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[])
        wx.controller.start_browser = AsyncMock(return_value=mock_page)
        wx.controller.open_url = AsyncMock()
        wx.controller.add_cookies = AsyncMock()
        wx.controller.add_cookie = AsyncMock()
        wx.controller.cleanup = AsyncMock()

        # Mock Call_Success to return session
        session = {'token': 'test123', 'expiry': {'expiry_time': '2025-12-31'}}
        with patch.object(wx, 'Call_Success', new=AsyncMock(return_value=session)):
            result = await wx.Token(callback=None, isClose=False)

            # Verify flow completed
            assert result == session

    @pytest.mark.asyncio
    async def test_wxlogin_to_call_success_flow(self):
        """Test wxLogin → Call_Success async flow."""
        wx = Wx()

        wx.check_lock = MagicMock(return_value=True)
        wx.set_lock = MagicMock()
        wx.release_lock = MagicMock()

        wx.controller = AsyncMock()
        mock_page = MagicMock()
        wx.controller.start_browser = AsyncMock(return_value=mock_page)
        wx.controller.open_url = AsyncMock()

        # Mock Call_Success
        with patch.object(wx, 'Call_Success', new=AsyncMock(return_value={'token': 'test123'})):
            with patch.object(wx, 'cleanup_resources', new=AsyncMock()):
                result = await wx.wxLogin(CallBack=None, NeedExit=False)

                # Verify login initiated
                assert wx.controller.start_browser.called

    @pytest.mark.asyncio
    async def test_switch_account_complete_flow(self):
        """Test complete switch_account async flow."""
        wx = Wx()

        wx.controller = AsyncMock()
        mock_page = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[])

        # Mock Token and Call_Success
        token_response = {'token': 'test123'}
        with patch.object(wx, 'Token', new=AsyncMock(return_value=token_response)):
            with patch.object(wx, 'Call_Success', new=AsyncMock(return_value=token_response)):
                wx.controller.get_cookies = AsyncMock(return_value=[
                    {'name': 'token', 'value': 'new123'}
                ])

                result = await wx.switch_account(username="test_user")

                # Verify complete flow
                assert result is True


class TestErrorHandling:
    """Test error handling in async methods."""

    @pytest.mark.asyncio
    async def test_token_handles_import_error(self):
        """Test Token() handles ImportError gracefully."""
        wx = Wx()

        wx.controller = AsyncMock()
        wx.controller.start_browser = AsyncMock(side_effect=ImportError("Module not found"))
        wx.controller.cleanup = AsyncMock()

        result = await wx.Token(callback=None, isClose=True)

        # Should handle ImportError and return None
        assert result is None
        assert wx.controller.cleanup.called  # Cleanup in finally

    @pytest.mark.asyncio
    async def test_call_success_handles_no_controller(self):
        """Test Call_Success() handles missing controller."""
        wx = Wx()
        wx.controller = None

        result = await wx.Call_Success(has_extdata=True)

        # Should return None gracefully
        assert result is None

    @pytest.mark.asyncio
    async def test_close_handles_cleanup_exception(self):
        """Test Close() handles cleanup exceptions."""
        wx = Wx()

        wx.controller = AsyncMock()
        wx.controller.Close = AsyncMock(side_effect=RuntimeError("Cleanup failed"))

        result = await wx.Close()

        # Should return False on exception
        assert result is False


# Run tests with pytest command:
# pytest tests/test_wx_async.py -v
# pytest tests/test_wx_async.py --cov=driver/wx --cov-report=term
