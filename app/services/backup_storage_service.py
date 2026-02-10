"""BackupStorage service for v1.1 (safe no-op when disabled)."""

from typing import Optional, Dict, Any

from app.config import settings


class BackupStorageService:
    """Service for external backup storage (v1.1 feature)."""
    
    def __init__(self):
        self.enabled = settings.feature_external_backup
    
    async def upload_backup(
        self,
        local_file_path: str,
        remote_filename: str
    ) -> Dict[str, Any]:
        """Upload backup to external storage. Returns safe no-op when disabled."""
        if not self.enabled:
            # Safe no-op behavior
            return {
                "success": False,
                "url": None,
                "message": "Внешнее хранилище не настроено"
            }
        
        # Implementation would go here when enabled
        return {
            "success": False,
            "url": None,
            "message": "Внешнее хранилище не настроено"
        }
    
    async def list_backups(self) -> Dict[str, Any]:
        """List available backups in external storage."""
        if not self.enabled:
            return {
                "success": False,
                "backups": [],
                "message": "Внешнее хранилище не настроено"
            }
        
        # Implementation would go here
        return {
            "success": False,
            "backups": [],
            "message": "Внешнее хранилище не настроено"
        }
    
    async def download_backup(
        self,
        remote_filename: str,
        local_path: str
    ) -> bool:
        """Download backup from external storage."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
    
    async def delete_backup(self, remote_filename: str) -> bool:
        """Delete backup from external storage."""
        if not self.enabled:
            return False
        
        # Implementation would go here
        return False
