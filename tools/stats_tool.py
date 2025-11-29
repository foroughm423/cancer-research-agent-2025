"""
Statistical survival analysis tool using lifelines library.
Generates Kaplan-Meier curves and performs log-rank tests.
"""

import os
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
from typing import Dict, Any

logger = logging.getLogger(__name__)


def perform_survival_analysis() -> Dict[str, Any]:
    """
    Execute survival analysis comparing pembrolizumab vs nivolumab in advanced melanoma.
    
    Uses simulated but clinically realistic data showing superior OS with pembrolizumab.
    
    Returns:
        Dictionary with results, p-value, medians, and saved figure path.
    """
    try:
        os.makedirs("outputs/figures", exist_ok=True)
        
        # Enhanced simulated data: Pembrolizumab shows clear survival benefit
        data = pd.DataFrame({
            'duration': [
                6, 8, 10, 12, 15, 18, 20, 24, 28, 36,   # Pembrolizumab: longer survival
                2, 3, 4, 5, 6, 7, 8, 9, 10, 12          # Nivolumab: shorter survival
            ],
            'event': [
                1, 1, 0, 1, 0, 0, 0, 0, 1, 0,           # 4 events
                1, 1, 1, 1, 1, 1, 1, 1, 0, 0            # 8 events
            ],
            'group': ['Pembrolizumab'] * 10 + ['Nivolumab'] * 10
        })

        kmf = KaplanMeierFitter()
        plt.figure(figsize=(10, 6))

        medians = {}
        for treatment in ['Pembrolizumab', 'Nivolumab']:
            mask = data['group'] == treatment
            kmf.fit(
                durations=data[mask]['duration'],
                event_observed=data[mask]['event'],
                label=treatment
            )
            kmf.plot_survival_function(ci_show=True)
            medians[treatment] = float(kmf.median_survival_time_) if not pd.isna(kmf.median_survival_time_) else None

        # Log-rank test
        group1 = data[data['group'] == 'Pembrolizumab']
        group2 = data[data['group'] == 'Nivolumab']
        
        logrank_result = logrank_test(
            durations_A=group1['duration'],
            durations_B=group2['duration'],
            event_observed_A=group1['event'],
            event_observed_B=group2['event']
        )
        
        p_value = logrank_result.p_value

        # Figure styling
        plt.title(
            'Kaplan-Meier Overall Survival: Pembrolizumab vs Nivolumab\n'
            'Advanced Melanoma (Simulated Clinical Trial Data)',
            fontsize=12, fontweight='bold'
        )
        plt.xlabel('Time (months)', fontsize=11)
        plt.ylabel('Overall Survival Probability', fontsize=11)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(loc='lower left', fontsize=10)
        plt.tight_layout()

        fig_path = "outputs/figures/km_survival_analysis.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()

        # Interpretation
        significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
        interpretation = (
            f"Log-rank test p-value: {p_value:.4f}. "
            f"The survival difference between treatments is {significance} (alpha=0.05). "
            f"Median OS for pembrolizumab: {medians['Pembrolizumab'] or 'Not reached'} months; "
            f"nivolumab: {medians['Nivolumab']} months."
        )

        logger.info(f"Survival analysis completed: p={p_value:.4f}")

        return {
            "status": "success",
            "figure_path": fig_path,
            "p_value": round(p_value, 4),
            "median_pembrolizumab": medians['Pembrolizumab'],
            "median_nivolumab": medians['Nivolumab'],
            "interpretation": interpretation,
            "test_statistic": round(logrank_result.test_statistic, 4)
        }

    except Exception as e:
        logger.error(f"Survival analysis failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    result = perform_survival_analysis()
    if result["status"] == "success":
        print("Analysis successful")
        print(f"P-value: {result['p_value']}")
        print(f"Figure saved: {result['figure_path']}")