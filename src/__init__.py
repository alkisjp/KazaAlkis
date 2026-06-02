"""
KazaALKIS - Daily Greek Calendar
A Windows-based open-data calendar notification system

Version: 1.1.0
Created: June 1, 2026
Location: E:\\07_050_Workspaces_Code_Projects(latest)\\KazaALKIS
"""

__version__ = "1.1.0"
__author__ = "ALKIS"
__title__ = "KazaALKIS - Daily Greek Calendar"
__description__ = "Automated daily WhatsApp notifications with Greek Orthodox calendar data"

from .database import KazaALKISDatabase
from .config_manager import ConfigurationManager
from .message_builder import MessageBuilder
from .whatsapp_notifier import WhatsAppNotifier, BulkMessageSender
from .logger_dashboard import KazaALKISLogger, KazaALKISDashboard
from .calendar_exporter import CalendarExporter
from .data_importer import DataImporter

__all__ = [
    'KazaALKISDatabase',
    'ConfigurationManager',
    'MessageBuilder',
    'WhatsAppNotifier',
    'BulkMessageSender',
    'KazaALKISLogger',
    'KazaALKISDashboard',
    'CalendarExporter',
    'DataImporter'
]
