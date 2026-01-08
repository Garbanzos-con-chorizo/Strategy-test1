from typing import List, Any, Dict, Optional

class MyMomentumStrategy:
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize strategy with parameters.
        params: dictionary of configuration values (e.g. {'period': 14})
        """
        self.params = params
        self.period = params.get('period', 14)
        self.rsi_period = params.get('rsi_period', 14)

    def step(self, bar: Any, state: Any) -> tuple[List[Any], Any]:
        """
        Called on every market bar.
        
        Args:
            bar: The current candle/bar object (has .close, .open, etc.)
            state: Arbitrary state object passed back from previous step (or None)
            
        Returns:
            (actions, new_state)
            actions: List of Order objects (or empty list)
            new_state: Updated state to pass to next step
        """
        # If this is the first step, initialize state
        if state is None:
            state = {
                'prices': [],
                'rsi': 50.0 # Default neutral
            }

        # Example logic: accumulate prices
        # In a real strategy, we would calculate indicators here
        if hasattr(bar, 'close'):
            state['prices'].append(bar.close)
            # Keep state manageable
            if len(state['prices']) > 100:
                state['prices'] = state['prices'][-100:]

        # Return empty actions and updated state
        return [], state
