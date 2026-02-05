#!/usr/bin/env python3
"""
Add Broker Configuration Helper

This script helps users create new broker configuration files from a template.
It guides users through the process of setting up broker credentials and settings.

Usage:
    python scripts/add_broker.py <broker_name>
    python scripts/add_broker.py binance --interactive
    python scripts/add_broker.py coinbase --api-key YOUR_KEY --api-secret YOUR_SECRET
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.utils import get_logger

logger = get_logger(__name__)

# Supported brokers
SUPPORTED_BROKERS = {
    'binance': {
        'type': 'crypto',
        'description': 'Binance cryptocurrency exchange',
        'testnet_available': True,
        'required_fields': ['api_key', 'api_secret'],
        'optional_fields': [],
        'default_pairs': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    },
    'coinbase': {
        'type': 'crypto',
        'description': 'Coinbase Pro cryptocurrency exchange',
        'testnet_available': True,
        'required_fields': ['api_key', 'api_secret', 'passphrase'],
        'optional_fields': [],
        'default_pairs': ['BTC/USD', 'ETH/USD', 'LTC/USD']
    },
    'gemini': {
        'type': 'crypto',
        'description': 'Gemini cryptocurrency exchange',
        'testnet_available': True,
        'required_fields': ['api_key', 'api_secret'],
        'optional_fields': [],
        'default_pairs': ['BTC/USD', 'ETH/USD']
    },
    'kraken': {
        'type': 'crypto',
        'description': 'Kraken cryptocurrency exchange',
        'testnet_available': False,
        'required_fields': ['api_key', 'api_secret'],
        'optional_fields': [],
        'default_pairs': ['BTC/USD', 'ETH/USD', 'XRP/USD']
    },
    'mt4': {
        'type': 'forex',
        'description': 'MetaTrader 4 (Forex/CFDs)',
        'testnet_available': True,
        'required_fields': ['account_number', 'password', 'server'],
        'optional_fields': ['path'],
        'default_pairs': ['EURUSD', 'GBPUSD', 'USDJPY']
    },
    'alpaca': {
        'type': 'stocks',
        'description': 'Alpaca stock trading',
        'testnet_available': True,
        'required_fields': ['api_key', 'api_secret'],
        'optional_fields': [],
        'default_pairs': ['AAPL', 'GOOGL', 'MSFT']
    }
}


class BrokerConfigCreator:
    """Helper class to create broker configuration files"""
    
    def __init__(self, project_root: Path):
        """
        Initialize the creator
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.config_dir = project_root / 'config' / 'brokers'
        self.template_path = self.config_dir / '_template.json'
        
    def load_template(self) -> Dict[str, Any]:
        """Load the template configuration"""
        if not self.template_path.exists():
            logger.error(f"Template file not found: {self.template_path}")
            sys.exit(1)
        
        with open(self.template_path, 'r') as f:
            return json.load(f)
    
    def create_config(
        self,
        broker_name: str,
        api_credentials: Dict[str, str],
        testnet: bool = True,
        enabled: bool = False,
        interactive: bool = False
    ) -> Dict[str, Any]:
        """
        Create broker configuration
        
        Args:
            broker_name: Name of the broker
            api_credentials: API credentials dictionary
            testnet: Use testnet/sandbox mode
            enabled: Enable broker by default
            interactive: Interactive mode for additional settings
            
        Returns:
            Broker configuration dictionary
        """
        # Get broker info
        broker_info = SUPPORTED_BROKERS.get(broker_name.lower())
        if not broker_info:
            logger.error(f"Unsupported broker: {broker_name}")
            logger.info(f"Supported brokers: {', '.join(SUPPORTED_BROKERS.keys())}")
            sys.exit(1)
        
        # Load template
        config = self.load_template()
        
        # Update basic info
        config['name'] = broker_name.upper()
        config['type'] = broker_info['type']
        config['enabled'] = enabled
        config['description'] = broker_info['description']
        
        # Update credentials
        config['api_credentials'] = api_credentials
        
        # Update settings
        if broker_info['testnet_available']:
            config['settings']['testnet'] = testnet
        else:
            config['settings'].pop('testnet', None)
        
        # Update supported pairs
        config['supported_pairs'] = broker_info['default_pairs']
        
        # Interactive mode - ask for additional settings
        if interactive:
            config = self._interactive_settings(config, broker_name)
        
        return config
    
    def _interactive_settings(self, config: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """
        Interactively configure additional settings
        
        Args:
            config: Base configuration
            broker_name: Broker name
            
        Returns:
            Updated configuration
        """
        print("\n" + "="*60)
        print("Additional Settings (press Enter to use defaults)")
        print("="*60)
        
        # Trading settings
        print("\n--- Trading Settings ---")
        
        order_type = input(f"Default order type (limit/market) [{config['trading_settings']['default_order_type']}]: ").strip()
        if order_type:
            config['trading_settings']['default_order_type'] = order_type
        
        # Risk management
        print("\n--- Risk Management ---")
        
        max_position = input(f"Max position size [{config['risk_management']['max_position_size']}]: ").strip()
        if max_position:
            config['risk_management']['max_position_size'] = float(max_position)
        
        stop_loss = input(f"Stop loss percentage [{config['risk_management']['stop_loss_percentage']}]: ").strip()
        if stop_loss:
            config['risk_management']['stop_loss_percentage'] = float(stop_loss)
        
        take_profit = input(f"Take profit percentage [{config['risk_management']['take_profit_percentage']}]: ").strip()
        if take_profit:
            config['risk_management']['take_profit_percentage'] = float(take_profit)
        
        # Trading pairs
        print("\n--- Trading Pairs ---")
        print(f"Current pairs: {', '.join(config['supported_pairs'])}")
        
        add_pairs = input("Add additional trading pairs (comma-separated, or press Enter to skip): ").strip()
        if add_pairs:
            new_pairs = [p.strip() for p in add_pairs.split(',')]
            config['supported_pairs'].extend(new_pairs)
        
        return config
    
    def save_config(self, broker_name: str, config: Dict[str, Any], overwrite: bool = False):
        """
        Save broker configuration to file
        
        Args:
            broker_name: Broker name
            config: Configuration dictionary
            overwrite: Overwrite existing file
        """
        output_file = self.config_dir / f"{broker_name.lower()}.json"
        
        # Check if file exists
        if output_file.exists() and not overwrite:
            logger.error(f"Configuration file already exists: {output_file}")
            logger.info("Use --overwrite to replace existing configuration")
            sys.exit(1)
        
        # Save configuration
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to: {output_file}")
    
    def validate_credentials(self, broker_name: str, credentials: Dict[str, str]) -> bool:
        """
        Validate required credentials are provided
        
        Args:
            broker_name: Broker name
            credentials: Credentials dictionary
            
        Returns:
            True if valid, False otherwise
        """
        broker_info = SUPPORTED_BROKERS.get(broker_name.lower())
        if not broker_info:
            return False
        
        required_fields = broker_info['required_fields']
        
        for field in required_fields:
            if field not in credentials or not credentials[field]:
                logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def interactive_credentials(self, broker_name: str) -> Dict[str, str]:
        """
        Interactively collect credentials
        
        Args:
            broker_name: Broker name
            
        Returns:
            Credentials dictionary
        """
        broker_info = SUPPORTED_BROKERS.get(broker_name.lower())
        credentials = {}
        
        print("\n" + "="*60)
        print(f"Enter API Credentials for {broker_name.upper()}")
        print("="*60)
        
        for field in broker_info['required_fields']:
            value = input(f"{field.replace('_', ' ').title()}: ").strip()
            credentials[field] = value
        
        for field in broker_info.get('optional_fields', []):
            value = input(f"{field.replace('_', ' ').title()} (optional): ").strip()
            if value:
                credentials[field] = value
        
        return credentials


def list_supported_brokers():
    """Print list of supported brokers"""
    print("\nSupported Brokers:")
    print("="*70)
    print(f"{'Broker':<15} {'Type':<10} {'Testnet':<10} {'Description'}")
    print("-"*70)
    
    for broker, info in SUPPORTED_BROKERS.items():
        testnet = "Yes" if info['testnet_available'] else "No"
        print(f"{broker:<15} {info['type']:<10} {testnet:<10} {info['description']}")
    
    print("="*70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Create broker configuration from template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended for first-time setup)
  python scripts/add_broker.py binance --interactive
  
  # Quick setup with command-line arguments
  python scripts/add_broker.py coinbase --api-key KEY --api-secret SECRET --passphrase PASS
  
  # Enable broker immediately
  python scripts/add_broker.py binance --api-key KEY --api-secret SECRET --enabled
  
  # Live/production mode (not testnet)
  python scripts/add_broker.py binance --api-key KEY --api-secret SECRET --no-testnet
  
  # List all supported brokers
  python scripts/add_broker.py --list
        """
    )
    
    parser.add_argument('broker', nargs='?', help='Broker name (e.g., binance, coinbase, gemini)')
    parser.add_argument('--list', action='store_true', help='List supported brokers')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--api-key', help='API key')
    parser.add_argument('--api-secret', help='API secret')
    parser.add_argument('--passphrase', help='API passphrase (for exchanges that require it)')
    parser.add_argument('--account-number', help='Account number (for MT4)')
    parser.add_argument('--password', help='Password (for MT4)')
    parser.add_argument('--server', help='Server (for MT4)')
    parser.add_argument('--enabled', action='store_true', help='Enable broker immediately')
    parser.add_argument('--no-testnet', action='store_true', help='Use production/live mode (not testnet)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing configuration')
    
    args = parser.parse_args()
    
    # Show supported brokers
    if args.list:
        list_supported_brokers()
        return
    
    # Validate broker name provided
    if not args.broker:
        parser.print_help()
        print("\n")
        list_supported_brokers()
        return
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Initialize creator
    creator = BrokerConfigCreator(project_root)
    
    broker_name = args.broker.lower()
    
    # Collect credentials
    if args.interactive:
        credentials = creator.interactive_credentials(broker_name)
    else:
        # Build credentials from arguments
        credentials = {}
        
        if args.api_key:
            credentials['api_key'] = args.api_key
        if args.api_secret:
            credentials['api_secret'] = args.api_secret
        if args.passphrase:
            credentials['passphrase'] = args.passphrase
        if args.account_number:
            credentials['account_number'] = args.account_number
        if args.password:
            credentials['password'] = args.password
        if args.server:
            credentials['server'] = args.server
        
        # Validate credentials
        if not creator.validate_credentials(broker_name, credentials):
            logger.error("Invalid or incomplete credentials")
            logger.info("Use --interactive mode or provide all required credentials")
            
            # Show required fields
            broker_info = SUPPORTED_BROKERS.get(broker_name)
            if broker_info:
                logger.info(f"Required fields: {', '.join(broker_info['required_fields'])}")
            
            sys.exit(1)
    
    # Create configuration
    config = creator.create_config(
        broker_name=broker_name,
        api_credentials=credentials,
        testnet=not args.no_testnet,
        enabled=args.enabled,
        interactive=args.interactive
    )
    
    # Save configuration
    creator.save_config(broker_name, config, overwrite=args.overwrite)
    
    # Print summary
    print("\n" + "="*60)
    print("Configuration Created Successfully!")
    print("="*60)
    print(f"Broker:         {broker_name.upper()}")
    print(f"Mode:           {'Testnet/Sandbox' if not args.no_testnet else 'Production/Live'}")
    print(f"Enabled:        {'Yes' if args.enabled else 'No'}")
    print(f"Config File:    config/brokers/{broker_name}.json")
    print("="*60)
    
    if not args.enabled:
        print("\nNote: Broker is disabled by default.")
        print("Edit the config file and set 'enabled': true to activate it.")
    
    if not args.no_testnet:
        print("\nNote: Testnet/Sandbox mode is enabled.")
        print("This is recommended for testing. Set --no-testnet for live trading.")
    else:
        print("\n⚠️  WARNING: Production/Live mode is configured!")
        print("Make sure you have tested thoroughly before trading with real funds.")
    
    print("\nNext steps:")
    print("1. Review and edit config/brokers/{}.json".format(broker_name))
    print("2. Test connection: python -m bot.main --validate")
    print("3. Start bot: ./scripts/start_bot.sh")
    print("")


if __name__ == '__main__':
    main()
