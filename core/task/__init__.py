from .task import TaskScheduler

# Module-level singleton instance for global scheduler usage
# Auto-starts background event loop on first import
GlobalScheduler = TaskScheduler()

__all__ = ['TaskScheduler', 'GlobalScheduler']