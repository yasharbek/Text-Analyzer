import spacy
from collections import Counter
import sys
import os
import time
import threading
from textblob import TextBlob
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import sqlite3
import hashlib
from datetime import datetime

# database setup
DB_NAME = "text_analysis.db"

def init_database():
    """initialize the database with required tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # analysis history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, file_path),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    """create a new user in the database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def authenticate_user(username, password):
    """authenticate a user"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        password_hash = hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def add_to_history(user_id, file_path, filename):
    """add a file analysis to user's history"""
    try:
        file_size = os.path.getsize(file_path)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # use INSERT OR IGNORE to avoid duplicates
        cursor.execute('''
        INSERT OR IGNORE INTO analysis_history 
        (user_id, filename, file_path, file_size) 
        VALUES (?, ?, ?, ?)
        ''', (user_id, filename, file_path, file_size))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding to history: {e}")
        return False

def get_user_history(user_id):
    """get analysis history for a user"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT filename, file_path, file_size, analysis_date 
        FROM analysis_history 
        WHERE user_id = ? 
        ORDER BY analysis_date DESC
        ''', (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        return history
    except Exception as e:
        print(f"Error getting history: {e}")
        return []

# initialize database
init_database()

#loading spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading the 'en_core_web_sm' model for spaCy...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def clear_screen():
    """clearing the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_text_file(file_path):
    """load and return the content of a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def preprocess_text(text):
    """process text with spacy, return the doc object"""
    return nlp(text)

def display_loading_animation():
    """display a loading animation that transitions from red to green"""
    width = 40
    duration = 1.5  # seconds
    steps = 20
    interval = duration / steps
    
    for i in range(steps + 1):
        progress = i / steps
        filled = int(width * progress)
        empty = width - filled
        
        # calculate color transition 
        r = int(255 * (1 - progress))
        g = int(255 * progress)
        b = 0
        
        # create the loading bar with ANSI color codes
        bar = "█" * filled + "░" * empty
        color_code = f"\033[38;2;{r};{g};{b}m"
        reset_code = "\033[0m"
        
        # print the loading bar
        sys.stdout.write(f"\r{color_code}[{bar}] {int(progress*100)}%{reset_code}")
        sys.stdout.flush()
        time.sleep(interval)
    
    # clear the loading line
    sys.stdout.write("\r" + " " * (width + 10) + "\r")
    sys.stdout.flush()

def run_with_loading_animation(func, *args, **kwargs):
    """run a function with the loading animation"""
    result = None
    exception = None
    
    def worker():
        nonlocal result, exception
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = e
    
    # start the function in a separate thread
    thread = threading.Thread(target=worker)
    thread.start()
    
    # display loading animation while the function is running
    display_loading_animation()
    
    # wait for the thread to complete
    thread.join()
    
    # if there was an exception, raise it
    if exception:
        raise exception
    
    return result

def display_auth_screen():
    """display authentication screen with login and signup options"""
    clear_screen()
    print("="*60)
    print("TEXT ANALYSIS TOOL - WELCOME")
    print("="*60)
    print("1. Login")
    print("2. Sign Up")
    print("3. Exit")
    print("="*60)
    
    while True:
        choice = input("Please enter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")

def login_user():
    """handle user login"""
    clear_screen()
    print("="*60)
    print("LOGIN")
    print("="*60)
    
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Username and password are required.")
        time.sleep(1.5)
        return None
    
    print("\nAuthenticating...")
    user_id = run_with_loading_animation(authenticate_user, username, password)
    
    if user_id:
        clear_screen()
        print(f"Welcome back, {username}!")
        time.sleep(1.5)
        return user_id, username
    else:
        clear_screen()
        print("Invalid username or password.")
        time.sleep(1.5)
        return None

def signup_user():
    """handle user signup"""
    clear_screen()
    print("="*60)
    print("SIGN UP")
    print("="*60)
    
    username = input("Choose a username: ").strip()
    password = input("Choose a password: ").strip()
    confirm_password = input("Confirm password: ").strip()
    
    if not username or not password:
        print("Username and password are required.")
        time.sleep(1.5)
        return None
    
    if password != confirm_password:
        print("Passwords do not match.")
        time.sleep(1.5)
        return None
    
    if len(password) < 4:
        print("Password must be at least 4 characters long.")
        time.sleep(1.5)
        return None
    
    print("\nCreating account...")
    success = run_with_loading_animation(create_user, username, password)
    
    if success:
        clear_screen()
        print("Account created successfully! Please login.")
        time.sleep(1.5)
        return login_user()
    else:
        clear_screen()
        print("Username already exists. Please choose a different username.")
        time.sleep(1.5)
        return None

def display_history_menu(user_id):
    """display analysis history for the user"""
    clear_screen()
    print("="*60)
    print("ANALYSIS HISTORY")
    print("="*60)
    
    history = get_user_history(user_id)
    
    if not history:
        print("No analysis history found.")
        return None
    
    print(f"{'#':<3} {'Filename':<30} {'Size':<10} {'Date':<15}")
    print("-"*60)
    
    for i, (filename, file_path, file_size, analysis_date) in enumerate(history, 1):
        # format file size
        size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
        
        # format date
        date_obj = datetime.strptime(analysis_date, '%Y-%m-%d %H:%M:%S')
        date_str = date_obj.strftime('%Y-%m-%d')
        
        print(f"{i:<3} {filename[:28]:<30} {size_str:<10} {date_str:<15}")
    
    print("="*60)
    print("\nEnter the number to re-analyze a file, or 'b' to go back.")
    
    while True:
        choice = input("Your choice: ").strip().lower()
        if choice == 'b':
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(history):
                return history[index][1]  # Return file_path
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Please enter a number or 'b' to go back.")

def display_menu(username):
    """display the menu options"""
    print("="*60)
    print(f"TEXT ANALYSIS MENU - Welcome, {username}")
    print("="*60)
    print("1.  Display most frequent tokens")
    print("2.  Display most frequent lemmas")
    print("3.  Display overall sentiment analysis")
    print("4.  Display top sentiment value tokens")
    print("5.  Display lowest sentiment value tokens")
    print("6.  Display text statistics")
    print("7.  Display part-of-speech distribution")
    print("8.  Generate word cloud")
    print("9.  Display most common noun phrases")
    print("10. Display readability score")
    print("11. Display keyword in context (KWIC)")
    print("12. Export analysis results to file")
    print("13. View analysis history")
    print("14. Analyze new file")
    print("15. Logout")
    print("="*60)


def get_most_frequent_tokens(doc, n=10):
    """get the most frequent tokens (excluding stop words and punctuation)"""
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return Counter(tokens).most_common(n)

def get_most_frequent_lemmas(doc, n=10):
    """get the most frequent lemmas (excluding stop words and punctuation)"""
    lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return Counter(lemmas).most_common(n)

def get_overall_sentiment(doc):
    """calculate overall sentiment of the text using TextBlob"""
    text = doc.text
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def get_unique_sentiment_by_tokens(doc, n=10, highest=True):
    """get unique tokens with highest or lowest sentiment values"""
    sentiment_dict = {}
    
    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            # use lemma to group similar words
            key = token.lemma_.lower()
            blob = TextBlob(token.text)
            sentiment = blob.sentiment.polarity
            
            # keep the highest absolute sentiment value for each lemma
            if key not in sentiment_dict or abs(sentiment) > abs(sentiment_dict[key][1]):
                sentiment_dict[key] = (token.text, sentiment)
    
    # convert to list and sort by sentiment score
    sentiment_scores = list(sentiment_dict.values())
    sentiment_scores.sort(key=lambda x: x[1], reverse=highest)
    
    return sentiment_scores[:n]

def get_text_statistics(doc):
    """get comprehensive text statistics"""
    total_chars = len(doc.text)
    total_tokens = len([token for token in doc if not token.is_space])
    total_sentences = len(list(doc.sents))
    total_words = len([token for token in doc if not token.is_punct and not token.is_space])
    unique_words = len(set(token.text.lower() for token in doc if not token.is_punct and not token.is_space))
    avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
    lexical_diversity = unique_words / total_words if total_words > 0 else 0
    
    return {
        "total_characters": total_chars,
        "total_tokens": total_tokens,
        "total_words": total_words,
        "unique_words": unique_words,
        "total_sentences": total_sentences,
        "avg_sentence_length": avg_sentence_length,
        "lexical_diversity": lexical_diversity
    }

def get_pos_distribution(doc):
    """get distribution of parts of speech"""
    pos_counts = Counter()
    for token in doc:
        if not token.is_punct and not token.is_space:
            pos_counts[token.pos_] += 1
    return pos_counts

def generate_wordcloud(doc):
    """generate a word cloud from the text"""
    # extract text without stopwords, punctuation, and spaces
    words = [token.text for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    text = ' '.join(words)
    
    # generate word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud')
    plt.tight_layout()
    plt.show()

def get_most_common_noun_phrases(doc, n=10):
    """extract the most common noun phrases"""
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    return Counter(noun_phrases).most_common(n)

def get_readability_score(doc):
    """calculate approximate readability score"""
    total_sentences = len(list(doc.sents))
    total_words = len([token for token in doc if not token.is_punct and not token.is_space])
    total_syllables = sum([count_syllables(token.text) for token in doc if not token.is_punct and not token.is_space])
    
    if total_sentences > 0 and total_words > 0:
        # rlesch reading ease formula
        score = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
        return score
    return 0

def count_syllables(word):
    """approximate syllable count for a word"""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

def display_keyword_in_context(doc, keyword, context=3):
    """display keyword in context with surrounding words"""
    keyword = keyword.lower()
    results = []
    
    for i, token in enumerate(doc):
        if token.text.lower() == keyword:
            start = max(0, i - context)
            end = min(len(doc), i + context + 1)
            context_text = ' '.join([doc[j].text for j in range(start, end)])
            results.append(context_text)
    
    return results[:10]  # return first 10 results

def export_analysis_results(doc, filename="text_analysis_report.txt"):
    """export comprehensive analysis results to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("TEXT ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        # basic statistics
        stats = get_text_statistics(doc)
        f.write("TEXT STATISTICS:\n")
        for key, value in stats.items():
            f.write(f"{key.replace('_', ' ').title()}: {value}\n")
        
        f.write("\n" + "=" * 50 + "\n\n")
        
        # most frequent tokens
        f.write("MOST FREQUENT TOKENS:\n")
        tokens = get_most_frequent_tokens(doc, 20)
        for i, (token, count) in enumerate(tokens, 1):
            f.write(f"{i}. {token}: {count}\n")
        
        f.write("\n" + "=" * 50 + "\n\n")
        
        # sentiment analysis
        polarity, subjectivity = get_overall_sentiment(doc)
        f.write("SENTIMENT ANALYSIS:\n")
        f.write(f"Polarity: {polarity:.3f}\n")
        f.write(f"Subjectivity: {subjectivity:.3f}\n")
        
        f.write("\n" + "=" * 50 + "\n\n")
        
        # part-of-speech distribution
        f.write("PART-OF-SPEECH DISTRIBUTION:\n")
        pos_dist = get_pos_distribution(doc)
        total = sum(pos_dist.values())
        for pos, count in pos_dist.most_common():
            percentage = (count / total) * 100
            f.write(f"{pos}: {count} ({percentage:.1f}%)\n")
    
    return filename

def get_file_path_from_user():
    """get file path from user by displaying available .txt files"""
    clear_screen()
    print("="*60)
    print("ANALYZE NEW FILE")
    print("="*60)
    
    # get all .txt files in the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    txt_files = [f for f in os.listdir(current_dir) 
                if f.endswith('.txt') and os.path.isfile(os.path.join(current_dir, f))]
    
    if not txt_files:
        print("No .txt files found in the current directory.")
        print(f"Current directory: {current_dir}")
        print("\nPlease make sure your text files are in the same directory as this script.")
        time.sleep(3)
        return None
    
    # display available .txt files
    print("Available text files:\n")
    for i, filename in enumerate(txt_files, 1):
        file_path = os.path.join(current_dir, filename)
        file_size = os.path.getsize(file_path)
        size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
        print(f"{i:2d}. {filename:<30} ({size_str})")
    
    print("\n" + "="*60)
    print("Enter the number of the file to analyze, or 'm' to enter manual path.")
    
    while True:
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'm':
            # manual path entry
            manual_path = input("Enter the full path to the text file: ").strip()
            if not manual_path:
                print("No file path provided.")
                time.sleep(1.5)
                continue
            
            if not os.path.exists(manual_path):
                print(f"Error: The file '{manual_path}' was not found.")
                time.sleep(1.5)
                continue
            
            return manual_path
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(txt_files):
                selected_file = txt_files[index]
                file_path = os.path.join(current_dir, selected_file)
                print(f"Selected: {selected_file}")
                time.sleep(0.5)
                return file_path
            else:
                print(f"Please enter a number between 1 and {len(txt_files)}, or 'm' for manual path.")
        except ValueError:
            print(f"Please enter a number between 1 and {len(txt_files)}, or 'm' for manual path.")

def main_analysis_loop(user_id, username, file_path):
    """main analysis loop for a specific file"""
    # load and process the file
    filename = os.path.basename(file_path)
    text = load_text_file(file_path)
    if text is None:
        return False
    
    # add to user's history
    add_to_history(user_id, file_path, filename)
    
    # preprocess the text
    clear_screen()
    print("Processing text...")
    doc = run_with_loading_animation(preprocess_text, text)
    
    while True:
        clear_screen()
        display_menu(username)
        choice = input("Please enter your choice (1-15): ").strip()
        
        if choice == '1':
            clear_screen()
            print("Analyzing most frequent tokens...")
            tokens = run_with_loading_animation(get_most_frequent_tokens, doc, 15)
            clear_screen()
            print("Most frequent tokens (excluding stop words and punctuation):\n")
            for i, (token, count) in enumerate(tokens, 1):
                print(f"{i}. {token}: {count}")
                
        elif choice == '2':
            clear_screen()
            print("Analyzing most frequent lemmas...")
            lemmas = run_with_loading_animation(get_most_frequent_lemmas, doc, 15)
            clear_screen()
            print("Most frequent lemmas (excluding stop words and punctuation):\n")
            for i, (lemma, count) in enumerate(lemmas, 1):
                print(f"{i}. {lemma}: {count}")
                
        elif choice == '3':
            clear_screen()
            print("Calculating sentiment analysis...")
            polarity, subjectivity = run_with_loading_animation(get_overall_sentiment, doc)
            clear_screen()
            print("SENTIMENT ANALYSIS:\n")
            print(f"Polarity: {polarity:.3f}")
            print(f"Subjectivity: {subjectivity:.3f}\n")
            
            if polarity > 0.1:
                print("The text has a positive sentiment.")
            elif polarity < -0.1:
                print("The text has a negative sentiment.")
            else:
                print("The text has a neutral sentiment.")
                
            if subjectivity > 0.5:
                print("The text is quite subjective (personal opinions).")
            else:
                print("The text is quite objective (factual information).")
                
        elif choice == '4':
            clear_screen()
            print("Finding tokens with highest sentiment...")
            top_tokens = run_with_loading_animation(get_unique_sentiment_by_tokens, doc, highest=True)
            clear_screen()
            print("Tokens with highest sentiment values (unique lemmas):\n")
            for i, (token, sentiment) in enumerate(top_tokens, 1):
                print(f"{i}. {token}: {sentiment:.3f}")
                
        elif choice == '5':
            clear_screen()
            print("Finding tokens with lowest sentiment...")
            low_tokens = run_with_loading_animation(get_unique_sentiment_by_tokens, doc, highest=False)
            clear_screen()
            print("Tokens with lowest sentiment values (unique lemmas):\n")
            for i, (token, sentiment) in enumerate(low_tokens, 1):
                print(f"{i}. {token}: {sentiment:.3f}")
                
        elif choice == '6':
            clear_screen()
            print("Calculating text statistics...")
            stats = run_with_loading_animation(get_text_statistics, doc)
            clear_screen()
            print("TEXT STATISTICS:\n")
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
                
        elif choice == '7':
            clear_screen()
            print("Analyzing part-of-speech distribution...")
            pos_dist = run_with_loading_animation(get_pos_distribution, doc)
            clear_screen()
            print("PART-OF-SPEECH DISTRIBUTION:\n")
            total = sum(pos_dist.values())
            for pos, count in pos_dist.most_common():
                percentage = (count / total) * 100
                print(f"{pos}: {count} ({percentage:.1f}%)")
                
        elif choice == '8':
            clear_screen()
            print("Generating word cloud...")
            try:
                run_with_loading_animation(generate_wordcloud, doc)
                clear_screen()
                print("Word cloud generated and displayed.")
            except Exception as e:
                clear_screen()
                print(f"Error generating word cloud: {e}")
                print("Make sure you have matplotlib and wordcloud installed:")
                print("pip install matplotlib wordcloud")
                
        elif choice == '9':
            clear_screen()
            print("Extracting noun phrases...")
            noun_phrases = run_with_loading_animation(get_most_common_noun_phrases, doc)
            clear_screen()
            print("MOST COMMON NOUN PHRASES:\n")
            for i, (phrase, count) in enumerate(noun_phrases, 1):
                print(f"{i}. {phrase}: {count}")
                
        elif choice == '10':
            clear_screen()
            print("Calculating readability score...")
            score = run_with_loading_animation(get_readability_score, doc)
            clear_screen()
            print("READABILITY SCORE (Flesch Reading Ease):\n")
            print(f"Score: {score:.1f}\n")
            
            if score >= 90:
                print("Very easy to read (5th grade level)")
            elif score >= 80:
                print("Easy to read (6th grade level)")
            elif score >= 70:
                print("Fairly easy to read (7th grade level)")
            elif score >= 60:
                print("Plain English (8th-9th grade level)")
            elif score >= 50:
                print("Fairly difficult to read (10th-12th grade level)")
            elif score >= 30:
                print("Difficult to read (college level)")
            else:
                print("Very difficult to read (graduate level)")
                
        elif choice == '11':
            clear_screen()
            keyword = input("Enter keyword to search for: ").strip()
            if keyword:
                clear_screen()
                print(f"Searching for '{keyword}' in context...")
                results = run_with_loading_animation(display_keyword_in_context, doc, keyword)
                clear_screen()
                print(f"KEYWORD IN CONTEXT: '{keyword}'\n")
                if results:
                    for i, context in enumerate(results, 1):
                        print(f"{i}. ...{context}...")
                else:
                    print("No occurrences found.")
            else:
                clear_screen()
                print("No keyword entered.")
                time.sleep(1)
                continue
                
        elif choice == '12':
            clear_screen()
            filename = input("Enter output filename (or press Enter for default): ").strip()
            if not filename:
                filename = "text_analysis_report.txt"
            print("Exporting analysis results...")
            output_file = run_with_loading_animation(export_analysis_results, doc, filename)
            clear_screen()
            print(f"Analysis results exported to: {output_file}")
                
        elif choice == '13':
            # riew history
            selected_file = display_history_menu(user_id)
            if selected_file:
                # re-analyze the selected file
                return selected_file  # this will break the current loop and restart with the new file
            
        elif choice == '14':
            # analyze new file
            new_file_path = get_file_path_from_user()
            if new_file_path:
                return new_file_path  # this will break the current loop and restart with the new file
            
        elif choice == '15':
            clear_screen()
            print("Logging out...")
            time.sleep(1.5)
            return None  # signal to logout
            
        else:
            clear_screen()
            print("Invalid choice. Please enter a number between 1 and 15.")
            time.sleep(1.5)
            continue
        
        # pause before showing the menu again
        print("\n" + "="*60)
        input("Press Enter to return to the menu...")
    
    return file_path  # continue with current file

def main():
    """main application entry point"""
    current_user = None
    current_username = None
    current_file_path = None
    
    while True:
        if not current_user:
            # authentication phase
            auth_choice = display_auth_screen()
            
            if auth_choice == '1':
                result = login_user()
                if result:
                    current_user, current_username = result
                
            elif auth_choice == '2':
                result = signup_user()
                if result:
                    current_user, current_username = result
                
            elif auth_choice == '3':
                clear_screen()
                print("Goodbye!")
                break
        
        if current_user and not current_file_path:
            # get file to analyze
            current_file_path = get_file_path_from_user()
            if not current_file_path:
                continue
        
        if current_user and current_file_path:
            # main analysis loop
            result = main_analysis_loop(current_user, current_username, current_file_path)
            
            if result is None:
                # logout
                current_user = None
                current_username = None
                current_file_path = None
            else:
                # xwitch to different file (either from history or new file)
                current_file_path = result

if __name__ == "__main__":
    main()