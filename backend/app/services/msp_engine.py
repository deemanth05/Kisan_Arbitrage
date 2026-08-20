import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Statutory MSP and Ministry Benchmark Rates (₹/quintal) for 2024-2026 seasons
GOVERNMENT_BENCHMARKS = {
    "cotton": {
        "type": "MSP",
        "benchmark_name": "MSP (Min Support Price)",
        "price": 7121.0,
        "season": "Kharif 2024-25",
        "authority": "CACP / Ministry of Agriculture"
    },
    "soybean": {
        "type": "MSP",
        "benchmark_name": "MSP (Min Support Price)",
        "price": 4892.0,
        "season": "Kharif 2024-25",
        "authority": "CACP / Ministry of Agriculture"
    },
    "wheat": {
        "type": "MSP",
        "benchmark_name": "MSP (Min Support Price)",
        "price": 2425.0,
        "season": "Rabi 2024-25",
        "authority": "CACP / Ministry of Agriculture"
    },
    "maize": {
        "type": "MSP",
        "benchmark_name": "MSP (Min Support Price)",
        "price": 2225.0,
        "season": "Kharif 2024-25",
        "authority": "CACP / Ministry of Agriculture"
    },
    "tomato": {
        "type": "TOP_BENCHMARK",
        "benchmark_name": "TOP Operation Greens Benchmark",
        "price": 1750.0,
        "season": "Current Season Fair Benchmark",
        "authority": "MoFPI / NAFED Operation Greens"
    },
    "onion": {
        "type": "TOP_BENCHMARK",
        "benchmark_name": "TOP Operation Greens Benchmark",
        "price": 2050.0,
        "season": "Current Season Fair Benchmark",
        "authority": "MoFPI / NAFED Operation Greens"
    },
    "potato": {
        "type": "TOP_BENCHMARK",
        "benchmark_name": "TOP Operation Greens Benchmark",
        "price": 1650.0,
        "season": "Current Season Fair Benchmark",
        "authority": "MoFPI / NAFED Operation Greens"
    },
    "green_chilli": {
        "type": "TOP_BENCHMARK",
        "benchmark_name": "MIS State Fair Benchmark",
        "price": 3100.0,
        "season": "Current Season Market Intervention Rate",
        "authority": "State Agriculture Board"
    }
}

class MSPEngine:
    """
    Evaluates mandi prices against statutory MSP and Operation Greens TOP fair benchmark prices.
    """
    
    def evaluate_benchmark(self, commodity: str, modal_price: float) -> Dict[str, Any]:
        crop_clean = commodity.strip().lower().replace(" ", "_")
        benchmark_info = GOVERNMENT_BENCHMARKS.get(crop_clean, {
            "type": "TOP_BENCHMARK",
            "benchmark_name": "Agricultural Fair Benchmark",
            "price": 1800.0,
            "season": "Current Season",
            "authority": "Department of Agriculture"
        })
        
        bench_price = benchmark_info["price"]
        diff = modal_price - bench_price
        
        if diff >= 50.0:
            status = "ABOVE_BENCHMARK"
            badge = f"✅ ₹{int(abs(diff))} ABOVE BENCHMARK"
        elif diff <= -50.0:
            status = "BELOW_BENCHMARK"
            badge = f"⚠️ ₹{int(abs(diff))} BELOW BENCHMARK"
        else:
            status = "AT_BENCHMARK"
            badge = "➡️ AT BENCHMARK PRICE"
            
        return {
            "benchmark_status": status,
            "benchmark_name": benchmark_info["benchmark_name"],
            "benchmark_price": bench_price,
            "benchmark_diff": round(diff, 2),
            "badge_text": badge,
            "authority": benchmark_info["authority"]
        }

msp_engine = MSPEngine()
