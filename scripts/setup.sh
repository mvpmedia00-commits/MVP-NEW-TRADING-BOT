#!/bin/bash

################################################################################
# Setup Script for MVP Trading Bot
# 
# This script performs initial setup and installation of the trading bot:
# - Checks system requirements
# - Installs Python dependencies
# - Creates necessary directories
# - Sets up configuration files
# - Initializes database (if enabled)
# - Validates installation
#
# Usage:
#   ./scripts/setup.sh [--dev] [--skip-deps] [--docker]
#
# Options:
#   --dev         Install development dependencies
#   --skip-deps   Skip Python package installation
#   --docker      Setup for Docker environment
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

# Parse command line arguments
INSTALL_DEV=false
SKIP_DEPS=false
DOCKER_MODE=false

for arg in "$@"; do
    case $arg in
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
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
    echo "           MVP Trading Bot - Setup & Installation"
    echo "========================================================================"
    echo ""
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
        log_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION detected"
}

# Check pip
check_pip() {
    log_info "Checking pip installation..."
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    log_success "pip3 is installed"
}

# Create virtual environment
setup_venv() {
    if [ "$DOCKER_MODE" = true ]; then
        log_info "Skipping virtual environment creation in Docker mode"
        return
    fi
    
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        python3 -m venv "$PROJECT_ROOT/venv"
        log_success "Virtual environment created"
    else
        log_warning "Virtual environment already exists"
    fi
    
    log_info "Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
}

# Install Python dependencies
install_dependencies() {
    if [ "$SKIP_DEPS" = true ]; then
        log_info "Skipping dependency installation (--skip-deps flag)"
        return
    fi
    
    log_info "Installing Python dependencies..."
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r "$PROJECT_ROOT/requirements.txt"
        log_success "Dependencies installed"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies if requested
    if [ "$INSTALL_DEV" = true ]; then
        if [ -f "$PROJECT_ROOT/requirements-dev.txt" ]; then
            log_info "Installing development dependencies..."
            pip install -r "$PROJECT_ROOT/requirements-dev.txt"
            log_success "Development dependencies installed"
        else
            log_warning "requirements-dev.txt not found, skipping dev dependencies"
        fi
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    DIRECTORIES=(
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/data/historical"
        "$PROJECT_ROOT/data/cache"
        "$PROJECT_ROOT/data/backtest_results"
        "$PROJECT_ROOT/config/brokers"
        "$PROJECT_ROOT/config/strategies"
        "$PROJECT_ROOT/user_strategies/examples"
    )
    
    for dir in "${DIRECTORIES[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
}

# Setup configuration files
setup_config() {
    log_info "Setting up configuration files..."
    
    # Copy .env.example to .env if it doesn't exist
    if [ ! -f "$PROJECT_ROOT/.env" ] && [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        log_success "Created .env file from .env.example"
        log_warning "Please update .env with your API keys and configuration"
    else
        log_info ".env file already exists"
    fi
    
    # Ensure global config exists
    if [ ! -f "$PROJECT_ROOT/config/global.json" ]; then
        log_warning "config/global.json not found - this should be created by the repository"
    fi
}

# Set file permissions
set_permissions() {
    log_info "Setting file permissions..."
    
    # Make scripts executable
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        chmod +x "$PROJECT_ROOT/scripts"/*.sh 2>/dev/null || true
        chmod +x "$PROJECT_ROOT/scripts"/*.py 2>/dev/null || true
        log_success "Script files are now executable"
    fi
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    # Check if main bot module can be imported
    if python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from bot import main" 2>/dev/null; then
        log_success "Bot module imports successfully"
    else
        log_warning "Could not import bot module - this may be normal if dependencies are missing"
    fi
    
    # Check critical files
    CRITICAL_FILES=(
        "$PROJECT_ROOT/bot/main.py"
        "$PROJECT_ROOT/config/global.json"
        "$PROJECT_ROOT/requirements.txt"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Critical file missing: $file"
            exit 1
        fi
    done
    
    log_success "All critical files present"
}

# Initialize database
init_database() {
    log_info "Checking database configuration..."
    
    # Check if database is enabled in config
    DB_ENABLED=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/config/global.json')); print(config.get('database', {}).get('enabled', False))" 2>/dev/null || echo "false")
    
    if [ "$DB_ENABLED" = "True" ]; then
        log_info "Database is enabled - checking connection..."
        # Database initialization would go here
        # For now, just log that it's enabled
        log_warning "Database initialization not yet implemented - manual setup may be required"
    else
        log_info "Database is disabled in configuration"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo "========================================================================"
    echo "                    Setup Complete!"
    echo "========================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Configure your trading bot:"
    echo "     - Edit .env with your API credentials"
    echo "     - Configure brokers in config/brokers/"
    echo "     - Configure strategies in config/strategies/"
    echo ""
    echo "  2. Test your configuration:"
    echo "     - Run in paper trading mode first"
    echo "     - Use backtesting to validate strategies"
    echo ""
    echo "  3. Start the bot:"
    if [ "$DOCKER_MODE" = false ]; then
        echo "     source venv/bin/activate"
    fi
    echo "     ./scripts/start_bot.sh"
    echo ""
    echo "  4. Useful commands:"
    echo "     ./scripts/backtest.py --strategy sma_crossover --days 30"
    echo "     ./scripts/add_broker.py binance"
    echo ""
    echo "========================================================================"
    echo ""
}

# Main execution
main() {
    print_banner
    
    cd "$PROJECT_ROOT"
    
    check_python
    check_pip
    setup_venv
    install_dependencies
    create_directories
    setup_config
    set_permissions
    validate_installation
    init_database
    
    print_next_steps
}

# Run main function
main
