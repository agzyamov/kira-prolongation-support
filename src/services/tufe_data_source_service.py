"""
TufeDataSourceService for managing TÜFE data sources.
"""

from typing import List, Optional
from datetime import datetime
from src.models.tufe_data_source import TufeDataSource
from src.storage.data_store import DataStore
from src.services.exceptions import TufeDataSourceError


class TufeDataSourceService:
    """Service for managing TÜFE data sources."""
    
    def __init__(self, data_store: DataStore):
        """Initialize the service with a data store."""
        self.data_store = data_store
    
    def get_all_sources(self) -> List[TufeDataSource]:
        """Get all TÜFE data sources."""
        try:
            rows = self.data_store.get_all_tufe_data_sources()
            return [self.data_store._row_to_tufe_data_source(row) for row in rows]
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get all data sources: {e}")
    
    def get_active_source(self) -> Optional[TufeDataSource]:
        """Get the currently active TÜFE data source."""
        try:
            row = self.data_store.get_active_tufe_data_source()
            if row:
                return self.data_store._row_to_tufe_data_source(row)
            return None
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get active data source: {e}")
    
    def get_source_by_id(self, source_id: int) -> Optional[TufeDataSource]:
        """Get a TÜFE data source by ID."""
        try:
            row = self.data_store.get_tufe_data_source_by_id(source_id)
            if row:
                return self.data_store._row_to_tufe_data_source(row)
            return None
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get data source by ID {source_id}: {e}")
    
    def add_source(self, source: TufeDataSource) -> int:
        """Add a new TÜFE data source."""
        try:
            source_id = self.data_store.save_tufe_data_source(source)
            return source_id
        except Exception as e:
            raise TufeDataSourceError(f"Failed to add data source: {e}")
    
    def update_source(self, source_id: int, source: TufeDataSource) -> bool:
        """Update an existing TÜFE data source."""
        try:
            source.id = source_id
            self.data_store.save_tufe_data_source(source)
            return True
        except Exception as e:
            raise TufeDataSourceError(f"Failed to update data source {source_id}: {e}")
    
    def deactivate_source(self, source_id: int) -> bool:
        """Deactivate a TÜFE data source."""
        try:
            source = self.get_source_by_id(source_id)
            if source:
                source.deactivate()
                self.data_store.save_tufe_data_source(source)
                return True
            return False
        except Exception as e:
            raise TufeDataSourceError(f"Failed to deactivate data source {source_id}: {e}")
    
    def activate_source(self, source_id: int) -> bool:
        """Activate a TÜFE data source."""
        try:
            source = self.get_source_by_id(source_id)
            if source:
                source.activate()
                self.data_store.save_tufe_data_source(source)
                return True
            return False
        except Exception as e:
            raise TufeDataSourceError(f"Failed to activate data source {source_id}: {e}")
    
    def verify_source(self, source_id: int) -> bool:
        """Verify a TÜFE data source."""
        try:
            source = self.get_source_by_id(source_id)
            if source:
                source.update_verification()
                self.data_store.save_tufe_data_source(source)
                return True
            return False
        except Exception as e:
            raise TufeDataSourceError(f"Failed to verify data source {source_id}: {e}")
    
    def get_sources_needing_verification(self, max_age_days: int = 30) -> List[TufeDataSource]:
        """Get data sources that need verification."""
        try:
            all_sources = self.get_all_sources()
            return [source for source in all_sources if source.needs_verification(max_age_days)]
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get sources needing verification: {e}")
    
    def get_tcmb_source(self) -> Optional[TufeDataSource]:
        """Get the TCMB EVDS data source."""
        try:
            all_sources = self.get_all_sources()
            for source in all_sources:
                if "TCMB" in source.source_name.upper() or "EVDS" in source.source_name.upper():
                    return source
            return None
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get TCMB data source: {e}")
    
    def create_default_tcmb_source(self) -> TufeDataSource:
        """Create a default TCMB EVDS data source."""
        try:
            tcmb_source = TufeDataSource(
                source_name="TCMB EVDS API",
                api_endpoint="https://evds2.tcmb.gov.tr/service/evds/",
                series_code="TP.FE.OKTG01",
                data_format="json",
                requires_auth=True,
                rate_limit_per_hour=100,
                is_active=True
            )
            source_id = self.add_source(tcmb_source)
            tcmb_source.id = source_id
            return tcmb_source
        except Exception as e:
            raise TufeDataSourceError(f"Failed to create default TCMB data source: {e}")
    
    def get_source_statistics(self) -> dict:
        """Get statistics about data sources."""
        try:
            all_sources = self.get_all_sources()
            active_sources = [s for s in all_sources if s.is_active]
            verified_sources = [s for s in all_sources if s.is_verified()]
            needs_verification = [s for s in all_sources if s.needs_verification()]
            
            return {
                "total_sources": len(all_sources),
                "active_sources": len(active_sources),
                "verified_sources": len(verified_sources),
                "sources_needing_verification": len(needs_verification),
                "verification_rate": len(verified_sources) / len(all_sources) if all_sources else 0
            }
        except Exception as e:
            raise TufeDataSourceError(f"Failed to get source statistics: {e}")
    
    def cleanup_inactive_sources(self, days_inactive: int = 90) -> int:
        """Clean up sources that have been inactive for a long time."""
        try:
            all_sources = self.get_all_sources()
            cleaned_count = 0
            
            for source in all_sources:
                if not source.is_active and source.get_verification_age_days() and source.get_verification_age_days() > days_inactive:
                    # In a real implementation, you might want to delete the source
                    # For now, we'll just count them
                    cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            raise TufeDataSourceError(f"Failed to cleanup inactive sources: {e}")
