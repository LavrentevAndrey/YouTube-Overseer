from abc import ABC, abstractmethod

class INetworkBlocker(ABC):
    """
    Interface for blocking network traffic to specific targets.
    """

    @abstractmethod
    def block_target(self, target: str) -> bool:
        """
        Blocks network traffic to the specified target (IP or domain).
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def unblock_target(self, target: str) -> bool:
        """
        Unblocks network traffic to the specified target.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def is_blocked(self, target: str) -> bool:
        """
        Checks if the specified target is currently blocked.
        """
        pass
