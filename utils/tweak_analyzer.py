import json
from datetime import datetime


class TweakAnalyzer:
    def __init__(self):
        self.analysis_file = "tweak_analysis.json"

    def collect_tweak_statuses(self, tweaks):
        """Collect current status of all tweaks"""
        from config import TWEAKS

        tweak_configs = {t["key"]: t for t in TWEAKS}
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "tweaks": {}
        }

        for tweak_key, tweak_data in tweaks.items():
            if tweak_data.get("check_status_func"):
                try:
                    is_enabled = tweak_data["check_status_func"]()
                    tweak_instance = tweak_data.get("instance")
                    config = tweak_configs.get(tweak_key, {})
                    optimized_state = config.get("optimized_state", True)
                    is_optimized = is_enabled == optimized_state

                    analysis["tweaks"][tweak_key] = {
                        "enabled": is_enabled,
                        "optimized": is_optimized,
                        "category": tweak_data.get("category", "Unknown"),
                        "title": tweak_instance.metadata.title if tweak_instance else tweak_key
                    }
                except Exception as e:
                    print(f"Error checking status for {tweak_key}: {e}")

        return analysis

    def save_analysis(self, analysis):
        """Save analysis to file"""
        try:
            with open(self.analysis_file, "w", encoding='utf-8') as f:
                json.dump(analysis, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return False

    def load_latest_analysis(self):
        """Load the latest analysis from file"""
        try:
            with open(self.analysis_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
