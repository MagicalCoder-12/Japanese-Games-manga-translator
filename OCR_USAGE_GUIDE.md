# OCR Text Extractor - Usage Guide

## 🎯 Getting Started

### Installation
1. Make sure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Ollama is running with the translator model:
   ```bash
   ollama pull lauchacarro/qwen2.5-translator:latest
   ```

### Launching the Application
Run the enhanced OCR launcher:
```bash
python run_ocr.py
```
Or double-click `run_ocr.bat` on Windows.

## 🎮 Feature Overview

### 1. Interactive Region Selection
- Click "🎯 Select OCR Region" button
- A semi-transparent overlay appears
- Click and drag to select the area containing Japanese text
- Press ENTER to confirm or ESC to cancel
- The region is automatically saved for the current game

### 2. Region Memory System
- Regions are saved per game/executable automatically
- Switch between different games - each maintains its own regions
- View recent regions in the bottom panel
- No manual configuration needed

### 3. Re-OCR Hotkey (Ctrl+Shift+R)
- **Primary Feature**: Instantly re-scan the last selected region
- Works globally - even when the app is minimized
- Perfect for dynamic text that changes frequently
- No need to re-select the region every time

### 4. Auto-OCR Mode
- Toggle "⚡ Start Auto-OCR" to begin continuous scanning
- OCR runs every 2 seconds automatically
- Stops when you click "⏹️ Stop Auto-OCR"
- Great for cutscenes or dialogue sequences

### 5. Real-time Translation
- Extracted text is automatically sent to the translator
- Translations appear instantly in the translator window
- Long text is intelligently chunked for better quality
- No manual copying/pasting required

## 💡 Usage Scenarios

### Scenario 1: Visual Novel Dialogue
1. Launch your visual novel
2. In OCR launcher, select the dialogue text box area
3. Use `Ctrl+Shift+R` whenever new dialogue appears
4. Read the English translation instantly

### Scenario 2: RPG Subtitles
1. Start your RPG game
2. Select the subtitle/caption area
3. Enable Auto-OCR mode
4. Play normally - translations update automatically

### Scenario 3: Manga/Comic Reading
1. Open your manga viewer
2. Select the speech bubble area
3. Use Re-OCR hotkey when moving to next panel
4. Get instant translations of dialogue

## ⚙️ Advanced Features

### Sentence Chunking
- Automatically splits long text (>500 characters) into logical segments
- Preserves sentence boundaries when possible
- Each chunk gets individual translation for better accuracy
- Handles both Japanese and English punctuation

### Game Detection
- Automatically identifies the active game/window
- Maintains separate region profiles for each game
- Shows current game name in the interface
- Switch games seamlessly without losing region data

### Hotkey Management
- `Ctrl+Shift+R`: Re-OCR last region (global hotkey)
- Works even when app is in background
- May require administrator privileges on Windows
- Can be customized in the source code

## 🔧 Troubleshooting

### Common Issues

**Hotkey not working:**
- Run the application as Administrator
- Check if another app is using the same hotkey
- Try restarting the application

**OCR not detecting text:**
- Ensure the region is properly selected
- Check lighting/contrast in the game
- Some fonts may not be OCR-compatible
- Try adjusting the region size

**Translation quality issues:**
- Long text is automatically chunked for better results
- Very short phrases may lack context
- Some game-specific terminology may need manual adjustment

**Region selection problems:**
- Close other fullscreen applications first
- Multi-monitor setups may require adjustment
- Some games may interfere with screen capture

### Performance Tips

1. **Optimal Region Size**: Select only the text area, not entire screens
2. **Auto-OCR Interval**: Currently 2 seconds - modify in source if needed
3. **Memory Usage**: Regions are saved to `region_config.json`
4. **Background Operation**: The app can minimize to tray while running

## 📁 Configuration Files

- `region_config.json`: Stores all region data per game
- Format: `{game_executable: [{region, timestamp, window_title}]}`
- Can be manually edited or backed up

## 🔒 Privacy & Security

- All processing happens locally on your machine
- No internet required for OCR or translation
- Region data is stored locally only
- No telemetry or data collection

## 🆘 Need Help?

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure Ollama service is running
4. Test with the traditional translator app first

## 🔄 Updates & Customization

The source code is fully customizable:
- Adjust chunk sizes in `chunk_text()` function
- Modify hotkeys in `register_hotkeys()` function
- Change OCR frequency in `start_continuous_ocr()` function
- Customize region selection behavior in `RegionSelector` class

All major features are implemented as modular components for easy modification.