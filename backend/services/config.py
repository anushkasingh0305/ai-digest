"""
Configuration management for AI Digest system.
Manages system settings with persistence to JSON files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel
from ..logging_config import get_logger

logger = get_logger(__name__)


class AdapterConfig(BaseModel):
    """Configuration for an adapter."""
    name: str
    enabled: bool
    settings: Dict[str, Any] = {}


class DeliveryConfig(BaseModel):
    """Configuration for delivery channels."""
    email_enabled: bool = False
    email_address: Optional[str] = None
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None


class SchedulerConfig(BaseModel):
    """Configuration for scheduler."""
    enabled: bool = False
    hour: int = 6  # UTC
    minute: int = 0  # UTC
    delivery_enabled: bool = True


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    file_enabled: bool = True
    file_path: str = "logs/ai_digest.log"
    console_enabled: bool = True


class SystemConfig(BaseModel):
    """Complete system configuration."""
    adapters: Dict[str, AdapterConfig] = {}
    delivery: DeliveryConfig = DeliveryConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    logging: LoggingConfig = LoggingConfig()


class ConfigManager:
    """Manages system configuration with persistence."""

    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to configuration file.
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
        logger.info(
            f"ConfigManager initialized with {self.config_file}",
            extra={"config_file": str(self.config_file), "component": "config"},
        )

    def get_config(self) -> SystemConfig:
        """
        Get current configuration.

        Returns:
            SystemConfig object.
        """
        logger.debug("Getting config", extra={"component": "config"})
        return self.config

    def update_config(self, config: SystemConfig) -> None:
        """
        Update configuration and persist to file.

        Args:
            config: New configuration object.
        """
        try:
            self.config = config
            self._save_config()
            logger.info(
                "Configuration updated",
                extra={"component": "config"},
            )
        except Exception as e:
            logger.error(
                f"Failed to update config: {str(e)}",
                extra={"error": str(e), "component": "config"},
                exc_info=True,
            )
            raise

    def get_adapter_config(self, adapter_name: str) -> Optional[AdapterConfig]:
        """
        Get configuration for a specific adapter.

        Args:
            adapter_name: Name of the adapter.

        Returns:
            AdapterConfig or None if not found.
        """
        return self.config.adapters.get(adapter_name)

    def set_adapter_config(
        self,
        adapter_name: str,
        enabled: bool,
        settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Set configuration for an adapter.

        Args:
            adapter_name: Name of the adapter.
            enabled: Whether to enable the adapter.
            settings: Optional adapter-specific settings.
        """
        try:
            self.config.adapters[adapter_name] = AdapterConfig(
                name=adapter_name,
                enabled=enabled,
                settings=settings or {},
            )
            self._save_config()
            logger.info(
                f"Adapter config updated: {adapter_name}",
                extra={
                    "adapter": adapter_name,
                    "enabled": enabled,
                    "component": "config",
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to set adapter config: {str(e)}",
                extra={"adapter": adapter_name, "error": str(e), "component": "config"},
                exc_info=True,
            )
            raise

    def get_delivery_config(self) -> DeliveryConfig:
        """Get delivery configuration."""
        return self.config.delivery

    def set_delivery_config(self, delivery: DeliveryConfig) -> None:
        """
        Set delivery configuration.

        Args:
            delivery: New delivery configuration.
        """
        try:
            self.config.delivery = delivery
            self._save_config()
            logger.info(
                "Delivery config updated",
                extra={
                    "email_enabled": delivery.email_enabled,
                    "telegram_enabled": delivery.telegram_enabled,
                    "component": "config",
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to set delivery config: {str(e)}",
                extra={"error": str(e), "component": "config"},
                exc_info=True,
            )
            raise

    def get_scheduler_config(self) -> SchedulerConfig:
        """Get scheduler configuration."""
        return self.config.scheduler

    def set_scheduler_config(self, scheduler: SchedulerConfig) -> None:
        """
        Set scheduler configuration.

        Args:
            scheduler: New scheduler configuration.
        """
        try:
            self.config.scheduler = scheduler
            self._save_config()
            logger.info(
                "Scheduler config updated",
                extra={
                    "enabled": scheduler.enabled,
                    "time": f"{scheduler.hour:02d}:{scheduler.minute:02d}",
                    "component": "config",
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to set scheduler config: {str(e)}",
                extra={"error": str(e), "component": "config"},
                exc_info=True,
            )
            raise

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.config.logging

    def set_logging_config(self, logging: LoggingConfig) -> None:
        """
        Set logging configuration.

        Args:
            logging: New logging configuration.
        """
        try:
            self.config.logging = logging
            self._save_config()
            logger.info(
                "Logging config updated",
                extra={
                    "level": logging.level,
                    "component": "config",
                },
            )
        except Exception as e:
            logger.error(
                f"Failed to set logging config: {str(e)}",
                extra={"error": str(e), "component": "config"},
                exc_info=True,
            )
            raise

    def list_adapters(self) -> Dict[str, AdapterConfig]:
        """Get all adapter configurations."""
        return self.config.adapters

    def _load_config(self) -> SystemConfig:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.debug(
                    f"Loaded config from {self.config_file}",
                    extra={"component": "config"},
                )
                return SystemConfig(**data)
        except Exception as e:
            logger.warning(
                f"Failed to load config: {str(e)}, using defaults",
                extra={"error": str(e), "component": "config"},
            )

        # Return default configuration
        return SystemConfig()

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config.dict(), f, indent=2)
            logger.debug(
                f"Saved config to {self.config_file}",
                extra={"component": "config"},
            )
        except Exception as e:
            logger.error(
                f"Failed to save config: {str(e)}",
                extra={"error": str(e), "component": "config"},
                exc_info=True,
            )
            raise


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: str = "config.json") -> ConfigManager:
    """
    Get or create the global ConfigManager instance.

    Args:
        config_file: Path to configuration file.

    Returns:
        ConfigManager instance.
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_file)

    return _config_manager
