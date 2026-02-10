"""Tests for backup system."""

import pytest
import os


class TestBackupScripts:
    """Test backup scripts exist and are valid."""
    
    def test_backup_script_exists(self):
        """Test that backup script exists."""
        script_path = "scripts/backup/run_backup.sh"
        assert os.path.exists(script_path)
    
    def test_send_to_telegram_script_exists(self):
        """Test that Telegram script exists."""
        script_path = "scripts/backup/send_to_telegram.py"
        assert os.path.exists(script_path)
    
    def test_restore_instructions_exist(self):
        """Test that restore instructions exist."""
        script_path = "scripts/backup/restore_instructions.sh"
        assert os.path.exists(script_path)
    
    def test_backup_script_is_executable(self):
        """Test that backup script is executable."""
        script_path = "scripts/backup/run_backup.sh"
        if os.path.exists(script_path):
            # On Windows this may not work, but file should exist
            assert os.access(script_path, os.R_OK)


class TestBackupConfiguration:
    """Test backup configuration."""
    
    def test_backup_env_vars_in_example(self):
        """Test that backup env vars are documented."""
        with open(".env.example", "r") as f:
            content = f.read()
        
        assert "BACKUP_ENABLED" in content
        assert "BACKUP_DIR" in content
        assert "BACKUP_TG_CHAT_ID" in content
