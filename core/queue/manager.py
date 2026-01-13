"""
Dual Queue Manager for WeChat RSS System

This module provides a QueueManager class that manages two independent task queues:
- ListQueue: For article list collection (can be paused when QR code expires)
- ContentQueue: For article content extraction (continues independently)

The dual-queue architecture allows selective pausing of list collection during
WeChat authentication issues without affecting content extraction operations.
"""

from typing import Dict, Any
from core.queue.queue import TaskQueueManager
from core.print import print_info, print_warning, print_success


class QueueManager:
    """Dual-queue manager for separating article list and content collection tasks

    Architecture:
        - list_queue: Handles article list fetching from WeChat MPs
        - content_queue: Handles article content extraction (independent)

    Usage:
        from core.queue import GlobalQueueManager

        # Add article list collection task
        GlobalQueueManager.list_queue.add_task(fetch_article_list, mp_id)

        # Add content extraction task
        GlobalQueueManager.content_queue.add_task(extract_content, article_id)

        # Pause list queue on QR expiry
        GlobalQueueManager.pause_list_queue()

        # Content queue continues running
        assert not GlobalQueueManager.content_queue.is_paused
    """

    def __init__(self):
        """Initialize dual task queues with automatic background execution"""
        self.list_queue = TaskQueueManager(tag="Article List Queue")
        self.content_queue = TaskQueueManager(tag="Content Extraction Queue")

        # Start background processing for both queues
        self.list_queue.run_task_background()
        self.content_queue.run_task_background()

        print_success("Dual-queue manager initialized: ListQueue + ContentQueue")

    def pause_list_queue(self) -> None:
        """Pause article list collection queue

        Use when:
            - WeChat QR code expires
            - Token becomes invalid
            - Rate limiting detected
        """
        self.list_queue.pause()
        print_warning("Article list collection paused (content extraction continues)")

    def resume_list_queue(self) -> None:
        """Resume article list collection queue

        Use when:
            - WeChat login successful
            - Token refreshed
            - Rate limit cleared
        """
        self.list_queue.resume()
        print_success("Article list collection resumed")

    def pause_content_queue(self) -> None:
        """Pause article content extraction queue

        Use when:
            - Browser resource limits reached
            - Database maintenance
            - System overload
        """
        self.content_queue.pause()
        print_warning("Content extraction paused")

    def resume_content_queue(self) -> None:
        """Resume article content extraction queue"""
        self.content_queue.resume()
        print_success("Content extraction resumed")

    def get_list_queue_status(self) -> Dict[str, Any]:
        """Get article list queue status

        Returns:
            dict: {
                'is_paused': bool,
                'is_running': bool,
                'pending_tasks': int,
                'tag': str
            }
        """
        queue_info = self.list_queue.get_queue_info()
        return {
            'is_paused': self.list_queue.is_queue_paused(),
            'is_running': queue_info['is_running'],
            'pending_tasks': queue_info['pending_tasks'],
            'tag': self.list_queue.tag
        }

    def get_content_queue_status(self) -> Dict[str, Any]:
        """Get article content queue status

        Returns:
            dict: {
                'is_paused': bool,
                'is_running': bool,
                'pending_tasks': int,
                'tag': str
            }
        """
        queue_info = self.content_queue.get_queue_info()
        return {
            'is_paused': self.content_queue.is_queue_paused(),
            'is_running': queue_info['is_running'],
            'pending_tasks': queue_info['pending_tasks'],
            'tag': self.content_queue.tag
        }

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of both queues

        Returns:
            dict: {
                'list_queue': {...},
                'content_queue': {...}
            }
        """
        return {
            'list_queue': self.get_list_queue_status(),
            'content_queue': self.get_content_queue_status()
        }


# Module-level singleton for global access
GlobalQueueManager = QueueManager()
