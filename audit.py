"""
Swem Team Trading Suite: Strategy Auditor Core
Contains pure business logic for options strategy analysis.
No GUI dependencies.
"""

from typing import List, Dict, TypedDict, Union


class LegInput(TypedDict):
    type: str  # 'call' or 'put'
    action: str  # 'buy' or 'sell'
    delta: float


class AuditResult(TypedDict):
    Strategy: str
    Directional_Bias: str
    Net_Delta: float
    Prob_of_Success: str


def audit_strategy(legs: List[LegInput]) -> AuditResult:
    """
    Analyzes an option strategy based on its legs.
    
    Args:
        legs: List of dictionaries containing:
            - type: 'call' or 'put'
            - action: 'buy' or 'sell' 
            - delta: Absolute delta value (float)
            
    Returns:
        AuditResult containing strategy type, directional bias, net delta, and POP.
    """
    net_delta = 0.0
    short_call_delta = 0.0
    short_put_delta = 0.0
    
    # Calculate Net Delta and identify short legs for POP
    for leg in legs:
        d = abs(leg['delta'])
        leg_type = leg['type'].lower()
        action = leg['action'].lower()
        
        if leg_type == 'call':
            # Sell Call = Negative Delta, Buy Call = Positive Delta
            net_delta += -d if action == 'sell' else d
            if action == 'sell': 
                short_call_delta = d
        else:
            # Sell Put = Positive Delta, Buy Put = Negative Delta
            net_delta += d if action == 'sell' else -d
            if action == 'sell': 
                short_put_delta = d

    # Identify Strategy and Bias
    num_legs = len(legs)
    has_calls = any(l['type'].lower() == 'call' and l['action'].lower() == 'sell' for l in legs)
    has_puts = any(l['type'].lower() == 'put' and l['action'].lower() == 'sell' for l in legs)
    
    strategy = "Unknown"
    if num_legs == 2:
        strategy = "Bear Call Spread" if has_calls else "Bull Put Spread"
    elif num_legs == 4 and has_calls and has_puts:
        strategy = "Iron Condor"

    # Directional Bias
    bias = "Neutral"
    if net_delta > 0.05: 
        bias = "Bullish"
    elif net_delta < -0.05: 
        bias = "Bearish"

    # Probability of Success (POP)
    if strategy == "Iron Condor":
        prob_success = 1 - (short_call_delta + short_put_delta)
    else:
        prob_success = 1 - (short_call_delta if has_calls else short_put_delta)

    return {
        "Strategy": strategy,
        "Directional_Bias": bias,
        "Net_Delta": round(net_delta, 3),
        "Prob_of_Success": f"{max(0, prob_success):.2%}"
    }
