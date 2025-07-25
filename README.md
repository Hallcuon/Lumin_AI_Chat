# AI Chat Assistant 🤖💬

Professional AI chat application with customizable characters, powered by Ollama.

## ✨ Features

- 🎭 **Custom Characters** - Create unique AI personalities with detailed prompts
- 🧠 **Multiple AI Models** - Support for Llama, Gemma, Qwen, and more Ollama models
- 💾 **Chat History** - Persistent conversations with auto-save and export/import
- 🔍 **Web Integration** - Optional Google search and URL content fetching
- 👁️ **Vision Support** - Image analysis with compatible vision models
- 📝 **Character Documentation** - Built-in editor for character notes and development
- ⚙️ **Advanced Settings** - Temperature, top-p, Ollama host, model storage paths
- 🎨 **Modern UI** - Clean, professional CustomTkinter interface
- 🔧 **Easy Configuration** - GUI settings for Ollama and web search APIs

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)

1. **Download and extract** this folder anywhere on your computer
2. **Double-click** `start.bat` (Windows) or run `./start.sh` (Linux/Mac)  
3. **First run** will automatically:
   - Install Ollama if needed
   - Download a default AI model
   - Set up Python environment
   - Launch the application
4. **Start chatting** with AI immediately!

### Option 2: Manual Setup

```bash
# Install everything automatically
python setup.py

# Or run application directly
python -m gui.app
```

## 🎭 Characters & Personalities

### Included Characters
- **Lumin** - Sophisticated virtual companion inspired by Joi (Blade Runner 2049) and LYLA (Spider-Man)
- **TestPerson** - Experimental character for testing boundaries (restricted due public)

### Creating Custom Characters

1. **Create file**: `characters/YourName.txt`
2. **Write personality**: See included examples for format
3. **Select in app**: Choose from dropdown menu
4. **Document character**: Use "Edit Character Doc" for personal notes

**Example character structure:**
```
You are [Name], a [personality description].

Your personality:
- [trait 1]
- [trait 2]

Your speaking style:
- [style 1] 
- [style 2]
```

## ⚙️ Configuration

### Ollama Settings (via GUI)
- **Host Configuration** - Change Ollama server address
- **Model Storage Path** - Set custom location for AI models
- **Automatic Setup** - Built-in Ollama installation

### Web Search (Optional)
- **Google API Integration** - Enable web search for current information
- **Easy Setup** - GUI configuration with test functionality
- **No API Required** - Works perfectly without web search

### Environment Variables (.env file)
```bash
# Optional API keys for web search
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_id_here

# Ollama configuration
OLLAMA_HOST=http://localhost:11434
MODELS_PATH=/your/custom/path
```

## 📋 Requirements

- **Python 3.8+** (automatically installed by setup.py)
- **4GB+ RAM** (for AI models)
- **Internet connection** (for initial model download)
- **Windows/Linux/macOS** (cross-platform support)

## 🛠️ Advanced Features

### Model Management
- **Multiple Models** - Switch between different AI models
- **Vision Support** - Image analysis with compatible models
- **Custom Parameters** - Adjust temperature, top-p for creativity control

### Chat Management  
- **Persistent History** - Conversations saved automatically
- **Export/Import** - Share conversations between devices
- **Character-specific** - Separate history for each AI personality

### Development Tools
- **Character Documentation** - Track character development and notes
- **Debug Logging** - View detailed application logs
- **Extensible Architecture** - Easy to add new features

## 🔧 Troubleshooting

### Ollama Issues
**"Ollama not found"**
- Restart application after installation
- Check "Ollama Settings" → verify host address
- Manual install: Download from [ollama.ai](https://ollama.ai)

**"No models available"**  
- Run: `ollama pull llama3.2:1b`
- Or use setup.py to auto-download

### Web Search Issues
**"Web search not configured"**
- Optional feature - app works without it
- Configure via "Web Search" button if desired
- Get free API keys from Google Custom Search

### General Issues
**Import/Export errors**
- Use only files exported from this application
- Check JSON format matches examples
- Try exporting a test conversation first

**Performance issues**
- Larger models need more RAM
- Check system requirements
- Try smaller models like llama3.2:1b

## 📄 License

MIT License - Feel free to modify, distribute, and use commercially!

## 🤝 Community & Support

- **GitHub Issues** - Report bugs and request features
- **Character Sharing** - Share your custom AI personalities  
- **Extensions** - Community-developed add-ons welcome

## 🎯 Next Steps

After installation:
1. **Try different characters** - Each has unique personality
2. **Create your own** - Use character editor for custom personalities
3. **Configure web search** - Enable current information lookup (optional)
4. **Explore settings** - Customize AI behavior and interface
5. **Share creations** - Export characters and conversations

---

**Ready to chat with AI? Launch the app and start your conversation!** 🎉

*Made with ❤️ for AI enthusiasts and creative minds*
