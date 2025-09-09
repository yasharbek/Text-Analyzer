# 📝 Text Analyzer Pro

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-green?logo=spacy)](https://spacy.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive text analysis tool built with Python that provides advanced NLP capabilities, user management, and historical analysis tracking. Developed by **[@yasharbek](https://github.com/yasharbek)**.

## Features

### 🔐 User Management
- **👤 User Authentication** - Login/signup system
- **📊 User-specific History** - Each user maintains their own analysis history

### 📊 Text Analysis
- **🔤 Token Frequency** - Most frequent tokens and lemmas
- **😊 Sentiment Analysis** - Polarity and subjectivity scoring
- **📈 Text Statistics** - Character/word counts, lexical diversity
- **🏷️ POS Tagging** - Part-of-speech distribution
- **☁️ Word Clouds** - Visual representation of frequent words
- **📖 Readability Scores** - Flesch Reading Ease assessment
- **🔍 Keyword in Context** - Find words with surrounding context
- **📝 Noun Phrase Extraction** - Most common noun phrases

### 💾 Data Persistence
- **🗄️ SQLite Database** - Persistent storage of user data and history
- **📋 Analysis History** - Track all analyzed files with timestamps
- **🚫 Duplicate Prevention** - Same files aren't stored multiple times

### 🎨 User Experience
- **🎯 File Selection** - Visual menu of available .txt files
- **⏳ Loading Animations** - Beautiful red-to-green progress bars
- **🖥️ Clean Interface** - Terminal-based with clear navigation

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yasharbek/text-analyzer-pro.git
   cd text-analyzer-pro
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Add your text files**
   - Place `.txt` files in the same directory as the script
   - Or use absolute paths when prompted

## Usage

### Starting the Application
```bash
python text_analyzer.py
```

### Authentication
1. **Sign Up** - Create a new account with username and password
2. **Login** - Access your existing account and analysis history

### File Analysis
1. **Select from available .txt files** - Choose from numbered list
2. **Or enter manual path** - Type 'm' for custom file path
3. **Choose analysis options** - Use the menu (1-15) for different analyses

### Menu Options
| # | Option | Description |
|---|--------|-------------|
| 1 | Frequent Tokens | Most common words (excluding stop words) |
| 2 | Frequent Lemmas | Most common word roots |
| 3 | Sentiment Analysis | Overall emotional tone |
| 4 | Top Sentiment Words | Words with highest positive sentiment |
| 5 | Low Sentiment Words | Words with highest negative sentiment |
| 6 | Text Statistics | Comprehensive text metrics |
| 7 | POS Distribution | Parts of speech frequency |
| 8 | Word Cloud | Visual word frequency display |
| 9 | Noun Phrases | Most common noun chunks |
| 10 | Readability Score | Flesch Reading Ease assessment |
| 11 | Keyword in Context | Find words with surrounding text |
| 12 | Export Results | Save analysis to text file |
| 13 | View History | Browse previous analyses |
| 14 | Analyze New File | Choose another file to analyze |
| 15 | Logout | Return to login screen |

## Project Structure

```
text-analyzer-pro/
├── text_analyzer.py      # Main application file
├── text_analysis.db      # SQLite database (auto-generated)
├── README.md            # This file
└── *.txt                # Your text files for analysis
```

## Technical Details

### Built With
- **🐍 Python** - Core programming language
- **🤖 spaCy** - Advanced natural language processing
- **📊 TextBlob** - Sentiment analysis and text processing
- **🗄️ SQLite** - Database management
- **📈 Matplotlib** - Data visualization
- **☁️ WordCloud** - Word cloud generation

### Database Schema
```sql
users (id, username, password_hash, created_at)
analysis_history (id, user_id, filename, file_path, file_size, analysis_date)
```

## Sample Output

### Text Statistics Example
```
TEXT STATISTICS:
Total Characters: 12560
Total Tokens: 2345
Total Words: 2100
Unique Words: 856
Total Sentences: 120
Avg Sentence Length: 17.5
Lexical Diversity: 0.41
```

### Sentiment Analysis Example
```
SENTIMENT ANALYSIS:
Polarity: 0.215
Subjectivity: 0.478

The text has a positive sentiment.
The text is quite objective (factual information).
```

## Contributing

contributions are welcome! feel free to submit a Pull Request. for major changes, please open an issue first to discuss what you would like to change.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Developer

**Yasharbek** - [@yasharbek](https://github.com/yasharbek)

-  Portfolio: [GitHub Profile](https://github.com/yasharbek)

## Acknowledgments

- spaCy team for excellent NLP library
- TextBlob for sentiment analysis capabilities
- SQLite for lightweight database management
- Python community for amazing tools and libraries

---
⭐ **If you find this project useful, please give it a star on GitHub!**
```
