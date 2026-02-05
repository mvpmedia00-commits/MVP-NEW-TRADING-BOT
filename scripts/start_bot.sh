#!/bin/bash

################################################################################
# Start Script for MVP Trading Bot
#
# This script starts the trading bot with various options and modes.
# It handles environment setup, validation, and process management.
#
# Usage:
#   ./scripts/start_bot.sh [OPTIONS]
#
# Options:
#   --mode MODE          Set trading mode: paper, live (default: from config)
#   --daemon            Run bot as background daemon
#   --log-level LEVEL   Set log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
#   --validate          Validate configuration without starting
#   --dry-run           Show what would be executed without running
#   --help              Show this help message
#
# Examples:
#   ./scripts/start_bot.sh                    # Start with default settings
#   ./scripts/start_bot.sh --mode paper       # Start in paper trading mode
#   ./scripts/start_bot.sh --daemon           # Start as background process
#   ./scripts/start_bot.sh --validate         # Validate config only
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
MODE=""
DAEMON=false
LOG_LEVEL=""
VALIDATE_ONLY=false
DRY_RUN=false
PID_FILE="$PROJECT_ROOT/bot.pid"
LOG_FILE="$PROJECT_ROOT/logs/bot.log"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --daemon)
            DAEMON=true
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --validate)
            VALIDATE_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
print_banner() {
    echo ""
    echo "========================================================================"
    echo "                    MVP Trading Bot Launcher"
    echo "========================================================================"
    echo ""
}

# Check if bot is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_error "Bot is already running with PID $PID"
            log_info "To stop it, run: kill $PID"
            exit 1
        else
            log_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -d "$PROJECT_ROOT/venv" ]; then
        log_info "Activating virtual environment..."
        source "$PROJECT_ROOT/venv/bin/activate"
        log_success "Virtual environment activated"
    elif [ ! -f "/.dockerenv" ]; then
        log_warning "Virtual environment not found. Run ./scripts/setup.sh first."
    fi
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."
    
    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    
    # Check global config
    if [ ! -f "$PROJECT_ROOT/config/global.json" ]; then
        log_error "config/global.json not found"
        exit 1
    fi
    
    # Validate broker configs
    BROKER_COUNT=$(find "$PROJECT_ROOT/config/brokers" -name "*.json" ! -name "_template.json" | wc -l)
    if [ "$BROKER_COUNT" -eq 0 ]; then
        log_warning "No broker configurations found in config/brokers/"
        log_warning "Use ./scripts/add_broker.py to create broker configs"
    fi
    
    # Validate Python environment
    if ! python3 -c "import ccxt, pandas, numpy" 2>/dev/null; then
        log_error "Required Python packages not installed"
        log_info "Run: pip install -r requirements.txt"
        exit 1
    fi
    
    log_success "Configuration validation passed"
}

# Set environment variables
set_environment() {
    log_info "Setting environment variables..."
    
    # Load .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
    fi
    
    # Override with command line arguments
    if [ -n "$MODE" ]; then
        export TRADING_MODE="$MODE"
        log_info "Trading mode set to: $MODE"
    fi
    
    if [ -n "$LOG_LEVEL" ]; then
        export LOG_LEVEL="$LOG_LEVEL"
        log_info "Log level set to: $LOG_LEVEL"
    fi
    
    # Set Python path
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
}

# Build command
build_command() {
    CMD="python3 -m bot.main"
    echo "$CMD"
}

# Start bot in foreground
start_foreground() {
    log_info "Starting bot in foreground mode..."
    log_info "Press Ctrl+C to stop"
    echo ""
    
    CMD=$(build_command)
    
    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Would execute: $CMD"
        return
    fi
    
    cd "$PROJECT_ROOT"
    exec $CMD
}

# Start bot as daemon
start_daemon() {
    log_info "Starting bot as background daemon..."
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    CMD=$(build_command)
    
    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Would execute: $CMD > $LOG_FILE 2>&1 &"
        return
    fi
    
    cd "$PROJECT_ROOT"
    nohup $CMD > "$LOG_FILE" 2>&1 &
    
    PID=$!
    echo $PID > "$PID_FILE"
    
    # Wait a moment and check if process is still running
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        log_success "Bot started successfully with PID $PID"
        log_info "Log file: $LOG_FILE"
        log_info "To stop: kill $PID"
        log_info "To view logs: tail -f $LOG_FILE"
    else
        log_error "Bot failed to start. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Print status
print_status() {
    CURRENT_MODE="${TRADING_MODE:-paper}"
    CURRENT_LOG_LEVEL="${LOG_LEVEL:-INFO}"
    
    echo ""
    echo "Configuration:"
    echo "  Trading Mode:   $CURRENT_MODE"
    echo "  Log Level:      $CURRENT_LOG_LEVEL"
    echo "  Project Root:   $PROJECT_ROOT"
    
    if [ "$DAEMON" = true ]; then
        echo "  Daemon Mode:    Enabled"
        echo "  Log File:       $LOG_FILE"
        echo "  PID File:       $PID_FILE"
    else
        echo "  Daemon Mode:    Disabled (foreground)"
    fi
    echo ""
}

# Main execution
main() {
    print_banner
    
    cd "$PROJECT_ROOT"
    
    # Validation only mode
    if [ "$VALIDATE_ONLY" = true ]; then
        validate_config
        log_success "Validation complete - configuration is valid"
        exit 0
    fi
    
    # Normal startup
    check_running
    activate_venv
    validate_config
    set_environment
    print_status
    
    # Warning for live mode
    if [ "$MODE" = "live" ] || grep -q 'mode.*live' "$PROJECT_ROOT/config/global.json" 2>/dev/null; then
        log_warning "═══════════════════════════════════════════════════════════"
        log_warning "  WARNING: LIVE TRADING MODE"
        log_warning "  This will execute REAL trades with REAL money!"
        log_warning "  Make sure you have tested your strategy thoroughly."
        log_warning "═══════════════════════════════════════════════════════════"
        
        if [ "$DRY_RUN" = false ]; then
            read -p "Are you sure you want to continue? (yes/no): " CONFIRM
            if [ "$CONFIRM" != "yes" ]; then
                log_info "Startup cancelled by user"
                exit 0
            fi
        fi
    fi
    
    # Start bot
    if [ "$DAEMON" = true ]; then
        start_daemon
    else
        start_foreground
    fi
}

# Run main function
main
