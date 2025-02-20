import json
from datetime import datetime
from typing import Dict, Any, Optional
from functools import lru_cache
import os


class TweakAnalyzer:
    def __init__(self):
        self.analysis_file = "tweak_analysis.json"
        self._latest_analysis: Optional[Dict[str, Any]] = None
        self._last_analysis_time = 0
        self._analysis_cache_ttl = 300  # 5 minutes cache TTL

    @lru_cache(maxsize=32)
    def _get_tweak_configs(self) -> Dict[str, Any]:
        """Cache tweak configurations to avoid repeated imports"""
        from config import TWEAKS
        return {t["key"]: t for t in TWEAKS}

    def _get_tweak_status(self, tweak_key: str, tweak_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get status for a single tweak with error handling"""
        try:
            if not tweak_data.get("check_status_func"):
                return None

            is_enabled = tweak_data["check_status_func"]()
            tweak_instance = tweak_data.get("instance")
            config = self._get_tweak_configs().get(tweak_key, {})
            optimized_state = config.get("optimized_state", True)

            return {
                "enabled": is_enabled,
                "optimized": is_enabled == optimized_state,
                "category": tweak_data.get("category", "Unknown"),
                "title": (tweak_instance.metadata.title
                          if tweak_instance and hasattr(tweak_instance, 'metadata')
                          else tweak_key)
            }
        except Exception as e:
            print(f"Error checking status for {tweak_key}: {e}")
            return None

    def collect_tweak_statuses(self, tweaks: Dict[str, Any]) -> Dict[str, Any]:
        """Collect current status of all tweaks with improved performance"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "tweaks": {}
        }

        # Process tweaks in batches for better memory management
        batch_size = 10
        tweak_items = list(tweaks.items())

        for i in range(0, len(tweak_items), batch_size):
            batch = tweak_items[i:i + batch_size]
            for tweak_key, tweak_data in batch:
                status = self._get_tweak_status(tweak_key, tweak_data)
                if status:
                    analysis["tweaks"][tweak_key] = status

        return analysis

    def save_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Save analysis to file with backup protection"""
        backup_file = f"{self.analysis_file}.backup"
        try:
            # Create backup of existing file if it exists
            if os.path.exists(self.analysis_file):
                try:
                    os.replace(self.analysis_file, backup_file)
                except OSError:
                    pass

            # Write new analysis
            with open(self.analysis_file, "w", encoding='utf-8') as f:
                json.dump(analysis, f, indent=4, ensure_ascii=False)

            # Update cache
            self._latest_analysis = analysis
            self._last_analysis_time = datetime.now().timestamp()

            # Remove backup if save was successful
            if os.path.exists(backup_file):
                os.remove(backup_file)

            return True

        except Exception as e:
            print(f"Error saving analysis: {e}")
            # Restore from backup if save failed
            if os.path.exists(backup_file):
                try:
                    os.replace(backup_file, self.analysis_file)
                except OSError:
                    pass
            return False

    def load_latest_analysis(self) -> Optional[Dict[str, Any]]:
        """Load the latest analysis with caching"""
        current_time = datetime.now().timestamp()

        # Return cached analysis if it's still valid
        if (self._latest_analysis and
                current_time - self._last_analysis_time < self._analysis_cache_ttl):
            return self._latest_analysis

        try:
            # Check if file exists before attempting to open
            if not os.path.exists(self.analysis_file):
                return None

            with open(self.analysis_file, "r", encoding='utf-8') as f:
                analysis = json.load(f)

            # Update cache
            self._latest_analysis = analysis
            self._last_analysis_time = current_time

            return analysis

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading analysis: {e}")
            return None

    def cleanup(self):
        """Cleanup resources"""
        self._get_tweak_configs.cache_clear()
        self._latest_analysis = None
        self._last_analysis_time = 0