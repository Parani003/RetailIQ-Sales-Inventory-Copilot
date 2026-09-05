"""
Business Rules & Configuration Module for RetailIQ Copilot.
All thresholds are explicit, configurable, and transparently attributed to 'Application business rule'.
"""

class Config:
    # Inventory Rules
    LOW_STOCK_THRESHOLD: int = 10                 # Units
    STOCKOUT_DAYS_THRESHOLD: float = 3.0          # Days of inventory remaining
    OVERSTOCK_DAYS_THRESHOLD: float = 45.0        # Days of inventory remaining
    SLOW_MOVING_THRESHOLD_DAYS: int = 14          # Days without sales
    
    # Anomaly Detection Rules
    SPIKE_THRESHOLD_PCT: float = 50.0             # % increase over historical baseline
    DROP_THRESHOLD_PCT: float = -40.0             # % decrease under historical baseline
    
    # Calculation Window Rules
    DEMAND_ESTIMATION_WINDOW: int = 14            # Days used for avg daily sales
    RECENT_ANOMALY_WINDOW: int = 7                # Recent period for anomaly detection
    HISTORICAL_BASELINE_WINDOW: int = 30          # Historical baseline window (excluding recent period)
    
    # Source attribution
    RULE_SOURCE: str = "Application business rule"

    @classmethod
    def to_dict(cls) -> dict:
        return {
            "low_stock_threshold": cls.LOW_STOCK_THRESHOLD,
            "stockout_days_threshold": cls.STOCKOUT_DAYS_THRESHOLD,
            "overstock_days_threshold": cls.OVERSTOCK_DAYS_THRESHOLD,
            "slow_moving_threshold_days": cls.SLOW_MOVING_THRESHOLD_DAYS,
            "spike_threshold_pct": cls.SPIKE_THRESHOLD_PCT,
            "drop_threshold_pct": cls.DROP_THRESHOLD_PCT,
            "demand_estimation_window": cls.DEMAND_ESTIMATION_WINDOW,
            "recent_anomaly_window": cls.RECENT_ANOMALY_WINDOW,
            "historical_baseline_window": cls.HISTORICAL_BASELINE_WINDOW,
            "rule_source": cls.RULE_SOURCE,
        }

    @classmethod
    def update_rules(cls, **kwargs):
        for key, value in kwargs.items():
            attr = key.upper()
            if hasattr(cls, attr):
                setattr(cls, attr, value)
