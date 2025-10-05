"""
TufeApiKeyService for managing TÜFE API keys.
"""

from typing import List, Optional
from datetime import datetime
from src.models.tufe_api_key import TufeApiKey
from src.storage.data_store import DataStore
from src.services.exceptions import TufeApiKeyError


class TufeApiKeyService:
    """Service for managing TÜFE API keys."""
    
    def __init__(self, data_store: DataStore):
        """Initialize the service with a data store."""
        self.data_store = data_store
    
    def get_api_key(self, source_id: int) -> Optional[str]:
        """Get the active API key for a data source."""
        try:
            row = self.data_store.get_active_tufe_api_key(source_id)
            if row:
                api_key = self.data_store._row_to_tufe_api_key(row)
                return api_key.api_key
            return None
        except Exception as e:
            raise TufeApiKeyError(f"Failed to get API key for source {source_id}: {e}")
    
    def set_api_key(self, source_id: int, key_name: str, api_key: str) -> int:
        """Set an API key for a data source."""
        try:
            # Validate input
            if not key_name or not key_name.strip():
                raise ValueError("key_name must be a non-empty string")
            if not api_key or not api_key.strip():
                raise ValueError("api_key must be a non-empty string")
            if source_id <= 0:
                raise ValueError("source_id must be a positive integer")
            
            # Create API key object
            tufe_api_key = TufeApiKey(
                key_name=key_name,
                api_key=api_key,
                source_id=source_id,
                is_active=True
            )
            
            # Save to database
            key_id = self.data_store.save_tufe_api_key(tufe_api_key)
            return key_id
        except Exception as e:
            raise TufeApiKeyError(f"Failed to set API key: {e}")
    
    def update_api_key(self, key_id: int, new_api_key: str) -> bool:
        """Update an existing API key."""
        try:
            if not new_api_key or not new_api_key.strip():
                raise ValueError("new_api_key must be a non-empty string")
            
            # Get existing API key
            row = self.data_store.get_tufe_api_key_by_id(key_id)
            if not row:
                return False
            
            api_key = self.data_store._row_to_tufe_api_key(row)
            api_key.api_key = new_api_key
            
            # Save updated API key
            self.data_store.save_tufe_api_key(api_key)
            return True
        except Exception as e:
            raise TufeApiKeyError(f"Failed to update API key {key_id}: {e}")
    
    def deactivate_api_key(self, key_id: int) -> bool:
        """Deactivate an API key."""
        try:
            # Get existing API key
            row = self.data_store.get_tufe_api_key_by_id(key_id)
            if not row:
                return False
            
            api_key = self.data_store._row_to_tufe_api_key(row)
            api_key.deactivate()
            
            # Save updated API key
            self.data_store.save_tufe_api_key(api_key)
            return True
        except Exception as e:
            raise TufeApiKeyError(f"Failed to deactivate API key {key_id}: {e}")
    
    def activate_api_key(self, key_id: int) -> bool:
        """Activate an API key."""
        try:
            # Get existing API key
            row = self.data_store.get_tufe_api_key_by_id(key_id)
            if not row:
                return False
            
            api_key = self.data_store._row_to_tufe_api_key(row)
            api_key.activate()
            
            # Save updated API key
            self.data_store.save_tufe_api_key(api_key)
            return True
        except Exception as e:
            raise TufeApiKeyError(f"Failed to activate API key {key_id}: {e}")
    
    def get_keys_for_source(self, source_id: int) -> List[TufeApiKey]:
        """Get all API keys for a data source."""
        try:
            rows = self.data_store.get_tufe_api_keys_for_source(source_id)
            return [self.data_store._row_to_tufe_api_key(row) for row in rows]
        except Exception as e:
            raise TufeApiKeyError(f"Failed to get API keys for source {source_id}: {e}")
    
    def get_active_keys_for_source(self, source_id: int) -> List[TufeApiKey]:
        """Get active API keys for a data source."""
        try:
            all_keys = self.get_keys_for_source(source_id)
            return [key for key in all_keys if key.is_active]
        except Exception as e:
            raise TufeApiKeyError(f"Failed to get active API keys for source {source_id}: {e}")
    
    def record_api_usage(self, key_id: int) -> None:
        """Record API key usage."""
        try:
            # Get existing API key
            row = self.data_store.get_tufe_api_key_by_id(key_id)
            if not row:
                return
            
            api_key = self.data_store._row_to_tufe_api_key(row)
            api_key.record_usage()
            
            # Save updated API key
            self.data_store.save_tufe_api_key(api_key)
        except Exception as e:
            raise TufeApiKeyError(f"Failed to record API usage for key {key_id}: {e}")
    
    def get_api_key_by_id(self, key_id: int) -> Optional[TufeApiKey]:
        """Get an API key by ID."""
        try:
            row = self.data_store.get_tufe_api_key_by_id(key_id)
            if row:
                return self.data_store._row_to_tufe_api_key(row)
            return None
        except Exception as e:
            raise TufeApiKeyError(f"Failed to get API key by ID {key_id}: {e}")
    
    def get_api_key_statistics(self, source_id: int) -> dict:
        """Get statistics about API keys for a source."""
        try:
            all_keys = self.get_keys_for_source(source_id)
            active_keys = [k for k in all_keys if k.is_active]
            recently_used = [k for k in all_keys if k.is_recently_used()]
            old_keys = [k for k in all_keys if k.is_old()]
            
            return {
                "total_keys": len(all_keys),
                "active_keys": len(active_keys),
                "recently_used_keys": len(recently_used),
                "old_keys": len(old_keys),
                "usage_rate": len(recently_used) / len(all_keys) if all_keys else 0
            }
        except Exception as e:
            raise TufeApiKeyError(f"Failed to get API key statistics for source {source_id}: {e}")
    
    def cleanup_old_keys(self, max_age_days: int = 365) -> int:
        """Clean up old API keys."""
        try:
            all_keys = self.get_keys_for_source(0)  # Get all keys
            cleaned_count = 0
            
            for key in all_keys:
                if key.is_old(max_age_days):
                    # In a real implementation, you might want to delete the key
                    # For now, we'll just count them
                    cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            raise TufeApiKeyError(f"Failed to cleanup old API keys: {e}")
    
    def validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format."""
        try:
            if not api_key or not api_key.strip():
                return False
            
            # Basic validation - in production, you might want more sophisticated validation
            if len(api_key) < 10:
                return False
            
            # Check for common invalid patterns
            invalid_patterns = ['test', 'demo', 'sample', 'invalid']
            api_key_lower = api_key.lower()
            for pattern in invalid_patterns:
                if pattern in api_key_lower:
                    return False
            
            return True
        except Exception:
            return False
    
    def rotate_api_key(self, source_id: int, old_key_id: int, new_key: str, key_name: str = None) -> int:
        """Rotate an API key by deactivating the old one and creating a new one."""
        try:
            # Deactivate old key
            self.deactivate_api_key(old_key_id)
            
            # Create new key
            if key_name is None:
                key_name = f"Rotated Key {datetime.now().strftime('%Y-%m-%d')}"
            
            new_key_id = self.set_api_key(source_id, key_name, new_key)
            return new_key_id
        except Exception as e:
            raise TufeApiKeyError(f"Failed to rotate API key: {e}")
