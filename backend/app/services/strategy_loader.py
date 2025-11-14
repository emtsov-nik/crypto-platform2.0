import importlib
import inspect
import os
from typing import Dict, List, Type, Any, Optional
from pathlib import Path
from app.strategies.base_strategy import BaseStrategy


class StrategyLoader:
    """
    Dynamic strategy loader that discovers and loads strategy classes
    from the strategies directory
    """

    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {}
        self._strategy_dir = Path(__file__).parent.parent / "strategies"
        self._load_all_strategies()

    def _load_all_strategies(self):
        """Load all strategy classes from the strategies directory"""
        if not self._strategy_dir.exists():
            print(f"Strategies directory not found: {self._strategy_dir}")
            return

        # Get all Python files in strategies directory
        strategy_files = [
            f for f in os.listdir(self._strategy_dir)
            if f.endswith('.py') and not f.startswith('__') and f != 'base_strategy.py'
        ]

        for filename in strategy_files:
            module_name = filename[:-3]  # Remove .py extension
            try:
                # Import the module
                module = importlib.import_module(f"app.strategies.{module_name}")

                # Find all classes in the module that inherit from BaseStrategy
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Skip BaseStrategy itself and imported classes
                    if (obj is not BaseStrategy and
                        issubclass(obj, BaseStrategy) and
                        obj.__module__ == module.__name__):

                        strategy_name = obj.__name__
                        self._strategies[strategy_name] = obj
                        print(f"Loaded strategy: {strategy_name}")

            except Exception as e:
                print(f"Error loading strategy from {filename}: {e}")

    def get_strategy(self, strategy_name: str, params: Dict[str, Any]) -> Optional[BaseStrategy]:
        """
        Get an instance of a strategy by name

        Args:
            strategy_name: Name of the strategy class
            params: Parameters to pass to the strategy constructor

        Returns:
            Strategy instance or None if not found
        """
        strategy_class = self._strategies.get(strategy_name)
        if strategy_class is None:
            print(f"Strategy not found: {strategy_name}")
            return None

        try:
            return strategy_class(params)
        except Exception as e:
            print(f"Error instantiating strategy {strategy_name}: {e}")
            return None

    def list_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of all available strategies with metadata

        Returns:
            List of strategy information dictionaries
        """
        strategies = []

        for name, strategy_class in self._strategies.items():
            try:
                # Get default params from docstring or create empty dict
                default_params = self._get_default_params(strategy_class)

                # Create temporary instance to get metadata
                temp_instance = strategy_class(default_params)
                metadata = temp_instance.get_metadata()

                strategies.append({
                    'name': name,
                    'class_name': strategy_class.__name__,
                    'metadata': metadata,
                    'default_params': default_params,
                    'doc': strategy_class.__doc__ or ''
                })
            except Exception as e:
                print(f"Error getting metadata for {name}: {e}")
                strategies.append({
                    'name': name,
                    'class_name': strategy_class.__name__,
                    'metadata': {},
                    'default_params': {},
                    'doc': strategy_class.__doc__ or '',
                    'error': str(e)
                })

        return strategies

    def _get_default_params(self, strategy_class: Type[BaseStrategy]) -> Dict[str, Any]:
        """
        Extract default parameters from strategy class docstring or __init__

        Args:
            strategy_class: Strategy class

        Returns:
            Dictionary of default parameters
        """
        # This is a simple implementation. In production, you might want to
        # parse the docstring more carefully or use a different approach
        default_params = {}

        # Try to find default params in the class
        if hasattr(strategy_class, 'DEFAULT_PARAMS'):
            return strategy_class.DEFAULT_PARAMS

        # For RSIBBStrategy, we know the defaults
        if strategy_class.__name__ == 'RSIBBStrategy':
            default_params = {
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30,
                'bb_period': 20,
                'bb_std': 2.0,
                'atr_period': 14,
                'risk_percent': 1.0,
                'risk_reward_ratio': 2.0,
                'max_steps': 3,
                'step_distance_percent': 2.0,
            }

        return default_params

    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific strategy

        Args:
            strategy_name: Name of the strategy class

        Returns:
            Strategy information dictionary or None if not found
        """
        strategies = self.list_strategies()
        for strategy in strategies:
            if strategy['name'] == strategy_name:
                return strategy
        return None

    def reload_strategies(self):
        """Reload all strategies from disk"""
        self._strategies.clear()
        self._load_all_strategies()

    def strategy_exists(self, strategy_name: str) -> bool:
        """
        Check if a strategy exists

        Args:
            strategy_name: Name of the strategy class

        Returns:
            True if strategy exists, False otherwise
        """
        return strategy_name in self._strategies

    def get_strategy_class(self, strategy_name: str) -> Optional[Type[BaseStrategy]]:
        """
        Get strategy class (not instance) by name

        Args:
            strategy_name: Name of the strategy class

        Returns:
            Strategy class or None if not found
        """
        return self._strategies.get(strategy_name)


# Global strategy loader instance
_strategy_loader: Optional[StrategyLoader] = None


def get_strategy_loader() -> StrategyLoader:
    """
    Get global strategy loader instance (singleton pattern)

    Returns:
        StrategyLoader instance
    """
    global _strategy_loader
    if _strategy_loader is None:
        _strategy_loader = StrategyLoader()
    return _strategy_loader


def reload_strategies():
    """Reload all strategies in the global loader"""
    loader = get_strategy_loader()
    loader.reload_strategies()
