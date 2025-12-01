# MarketAI - Advanced Market Analysis AI System

A comprehensive AI system for market analysis with self-training capabilities, multi-instance synchronization, and modern user interfaces.

## 🎯 Requirements Checklist

- [x] **Todo List Created** - All requirements documented in this checklist
- [x] **Multi-Instance Data Sharing** - Shared data system prevents duplicate errors and training data across instances
- [x] **Self-Training AI** - AI can train autonomously with screen and web detection capabilities
- [x] **Production Ready** - No dummy features, all components are functional with modern UI
- [x] **Local Data Management** - Data stored locally in `shared_data/` with modification support
- [x] **Entry Point Files Created**:
  - [x] `setup.py` / `Setup.bat` - Sets up dependencies
  - [x] `dev.py` / `Dev.bat` - Developer access with profile-based authentication
  - [x] `user_version.py` / `UserVersion.bat` - Default user version
- [x] **Organized Folder Structure** - AI modules organized in `ai/` folder
- [x] **API Integration** - Integrated AntiPublic, LZT Market, and LolzTeam APIs
- [x] **Modern GUI** - Tabbed interface with Autobuy, Market Watch, Analytics, and Settings

## 📁 Project Structure

```
MarketAI/
├── setup.py              # Setup script (compile to Setup.exe)
├── dev.py                # Developer console (compile to Dev.exe)
├── user_version.py       # User application (compile to UserVersion.exe)
├── Setup.bat             # Windows batch wrapper for setup
├── Dev.bat               # Windows batch wrapper for dev console
├── UserVersion.bat       # Windows batch wrapper for user app
├── requirements.txt      # Python dependencies
├── ai/                   # AI Module (organized folder)
│   ├── core/            # Core AI engine and model
│   ├── training/        # Self-training capabilities
│   ├── detection/       # Screen and web detection
│   ├── data/            # Shared data management
│   ├── config/          # Configuration management
│   ├── api/             # API integrations (AntiPublic, LZT Market, LolzTeam)
│   ├── gui/             # Modern GUI components and tabs
│   └── utils/           # Utilities and authentication
├── shared_data/          # Shared data across instances
│   ├── config.json      # Configuration
│   ├── api_config.json  # API key configuration
│   ├── models/          # Saved models
│   ├── training/        # Training results
│   ├── instances/       # Instance registry
│   └── errors/          # Error logs
└── profiles/             # User profiles for authentication
```

## 🚀 Quick Start

### 1. Setup (Required First)

**Windows:**
```batch
Setup.bat
```

**Cross-platform:**
```bash
python setup.py
```

This will:
- Install all required dependencies
- Create necessary directories
- Initialize configuration
- Set up default user profiles

### 2. Developer Access

**Windows:**
```batch
Dev.bat
```

**Cross-platform:**
```bash
python dev.py
```

**Default Developer Credentials:**
- Username: `developer`
- Password: `dev_access_key`

**Admin Credentials:**
- Username: `admin`
- Password: `marketai_admin_2024`

### 3. User Version

**Windows:**
```batch
UserVersion.bat
```

**Cross-platform:**
```bash
python user_version.py
```

## 🔧 Building Executables

To create standalone .exe files:

```bash
pip install pyinstaller

# Build Setup.exe
pyinstaller --onefile --name Setup setup.py

# Build Dev.exe
pyinstaller --onefile --name Dev dev.py

# Build UserVersion.exe (with GUI)
pyinstaller --onefile --windowed --name UserVersion user_version.py
```

Executables will be in the `dist/` folder.

## 🧠 Features

### Modern GUI Interface
The application features a modern tabbed interface with:
- **🤖 Autobuy Tab**: Automated purchasing (disabled by default, never saved as enabled for safety)
- **👁️ Market Watch Tab**: Real-time market monitoring, notifications, and game/category selection
- **📊 Analytics Tab**: AI-powered market analysis, predictions, and trading tips
- **⚙️ Settings Tab**: API key configuration for all integrated services

### API Integrations
Three market-related APIs are integrated:
- **AntiPublic API**: Data breach checking and credential verification ([Documentation](https://antipublic.readme.io/reference/information))
- **LZT Market API**: Digital marketplace for account trading ([Documentation](https://lzt-market.readme.io/reference/information))
- **LolzTeam API**: Forum data, user profiles, and discussions ([Documentation](https://lolzteam.readme.io/reference/information))

### Multi-Instance Synchronization
- Shared data prevents duplicate training
- Error tracking across all instances
- Automatic instance discovery and heartbeat

### Self-Training AI
- Screen detection using OCR and computer vision
- Web content detection and analysis
- Autonomous training loop
- Configurable training parameters

### Detection Capabilities
- **Screen Detection**: Captures and analyzes screen content
- **Web Detection**: Scrapes and processes web pages
- **OCR**: Text recognition from images
- **Object Detection**: Visual element recognition

### Security
- Role-based access control (Admin, Developer, User)
- Profile-based authentication
- Secure credential storage
- Autobuy disabled by default and never persisted as enabled

## 📊 Configuration

Edit `shared_data/config.json` to customize:

```json
{
  "model_path": "shared_data/models/market_ai.model",
  "training": {
    "enabled": true,
    "auto_train": true,
    "epochs": 10,
    "min_samples": 100
  },
  "detection": {
    "screen": { "enabled": true, "ocr_enabled": true },
    "web": { "enabled": true, "headless": true }
  }
}
```

## 👥 User Profiles

Manage profiles through the Developer console or edit `profiles/profiles.json`:

- **admin**: Full system access
- **developer**: Development and training access
- **user**: Basic usage only

## 🔄 Data Sharing

The `shared_data/` folder enables multi-instance operation:

- **instances/registry.json**: Active instance tracking
- **training/processed.json**: Processed data hashes
- **training/results.json**: Training history
- **errors/log.json**: Shared error log

## 📝 License

Copyright © 2024 MarketAI. All rights reserved.
