import os
import re
import logging
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "8354885268:AAFgY_f_1FIEmZ0txNO4-pgAcvtSwBEvHKU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hello! Send me an HTML file and I'll extract the test information and create a new HTML file with the extracted data."
    )

async def handle_html_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the HTML file sent by the user."""
    processing_message = None
    try:
        # Send processing message
        processing_message = await update.message.reply_text("Processing your file...")
        
        # Get the file and its name
        original_filename = update.message.document.file_name
        file = await update.message.document.get_file()
        
        # Create a temporary file for download with the same name
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            file_path = temp_file.name
        
        # Download the file to temporary location
        await file.download_to_drive(file_path)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract test title from the test-info-card
        test_info_card = soup.find('div', class_='test-info-card')
        test_title = "Test Title Not Found"
        if test_info_card:
            test_info_header = test_info_card.find('div', class_='test-info-header')
            if test_info_header:
                h3_tag = test_info_header.find('h3')
                if h3_tag:
                    test_title = h3_tag.text.strip()
        
        # Extract welcome title from the welcome-title div
        welcome_title_div = soup.find('div', class_='welcome-title')
        welcome_title = "Welcome Title Not Found"
        if welcome_title_div:
            h2_tag = welcome_title_div.find('h2')
            if h2_tag:
                welcome_title = h2_tag.text.strip()
        
        # Extract minutes value from the info-item
        minutes_value = "Not Found"
        info_items = soup.find_all('div', class_='info-item')
        for item in info_items:
            clock_icon = item.find('i', class_='fas fa-clock')
            if clock_icon:
                span = item.find('span')
                if span:
                    minutes_value = span.text.strip()
                    break
        
        # Find the script tag and extract the questions array
        script_content = ""
        for script in soup.find_all('script'):
            if 'const questions = [' in script.text:
                script_content = script.text
                break
        
        # Extract the questions array using regex
        questions_match = re.search(r'const questions = \[(.*?)\];', script_content, re.DOTALL)
        questions_str = questions_match.group(1) if questions_match else "[]"
        questions = f"[{questions_str}]"
        
        # Extract total time expression from JavaScript variable
        total_time_match = re.search(r'const totalTime\s*=\s*([^;]+);', script_content)
        total_time_expression = "180 * 60"  # Default value
        if total_time_match:
            total_time_expression = total_time_match.group(1).strip()
        
        # Extract website URL from the navbar-actions
        website_url = "{website_url}"  # Default value
        pre_test_actions = soup.find('div', id='pre-test-actions')
        if pre_test_actions:
            website_link = pre_test_actions.find('a', class_='website-btn')
            if website_link and website_link.has_attr('href'):
                website_url = website_link['href']
        
        # Create the new HTML content with styling
        new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minor Test @ 01</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
        --primary: #facc15;
        --primary-dark: #111111;
        --secondary: #facc15; 
        --accent: #facc15;        
        --light-blue: #111111;    
        --dark: #0b1225;          
        --light: #111111;        
        --gray: #111111;  
        --success: #4CAF50;
        --warning: #FFC107;
        --danger: #F44336;
    }}

    @keyframes fadeIn {{
        from {{ opacity:0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes scaleIn {{
        from {{ transform: scale(0.9); opacity: 0; }}
        to {{ transform: scale(1); opacity: 1; }}
    }}

    @keyframes slideIn {{
        from {{ transform: translateX(-20px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        background: var(--light);
        font-family: 'Poppins', sans-serif;
        min-height: 100vh;
        padding-bottom: 70px;
        position: relative;
        color: #333;
        font-size: 14px;
        margin: 0;
        overflow-x: hidden; /* Prevent horizontal scrolling */
    }}

    .navbar {{
        background: var(--primary);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 0.8rem 0.5rem; /* Reduced padding for mobile */
    }}

    .navbar-brand {{
        font-size: 1.1rem; /* Slightly smaller for mobile */
        font-weight: 900;
        color: #0b1225 !important;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .navbar-brand i {{
        font-size: 1rem; /* Adjusted for mobile */
    }}

    .navbar-actions {{
        display: flex;
        align-items: center;
        gap: 0.5rem; /* Reduced gap for mobile */
        flex-wrap: wrap; /* Allow wrapping if needed */
    }}

    .timer {{
        background: rgba(255,255,255,0.2);
        padding: 0.4rem 0.8rem; /* Smaller padding */
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.8rem; /* Smaller font */
        color: white;
    }}

    .nav-action-btn {{
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 0.4rem 0.8rem; /* Smaller padding */
        border-radius: 20px;
        font-size: 0.8rem; /* Smaller font */
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        transition: all 0.2s ease;
        white-space: nowrap; /* Prevent text wrapping */
    }}

    .nav-action-btn:hover {{
        background: rgba(255,255,255,0.3);
    }}

    .nav-action-btn.submit-btn {{
        background: #4CAF50;
    }}

    .nav-action-btn.submit-btn:hover {{
        background: #43A047;
    }}

    .option-card.attempted {{
        pointer-events: none;
        opacity: 0.8;
    }}

    /* Modern Welcome Screen */
    .welcome-screen {{
        max-width: 100%; /* Use full width */
        margin: 1rem; /* Reduced margin */
        padding: 1.5rem; /* Reduced padding */
        background: #ffcc00;
        border-radius: 16px; /* Slightly smaller radius */
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }}

    .welcome-screen::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px; /* Thinner gradient bar */
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
    }}

    .test-info-card {{
        background: linear-gradient(145deg, #fff06b, #fff06bae);
        border-radius: 16px;
        padding: 1.2rem; /* Reduced padding */
        margin-bottom: 1.5rem;
        border: 1px solid rgba(33, 150, 243, 0.1);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.05);
    }}

    .test-info-header {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(33, 150, 243, 0.1);
    }}

    .test-info-header i {{
        font-size: 2rem;
        color: var(--primary);
        background: #0b1225;
        padding: 0.8rem;
        border-radius: 12px;
    }}

    .test-info-header h3 {{
        margin: 0;
        font-size: 1.3rem; /* Smaller font */
        font-weight: 600;
        color: #2c3e50;
    }}

    .test-info-body {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }}

    .info-item {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem;
        background: rgb(26, 0, 54);
        border-radius: 10px;
        border: 1px solid rgba(33, 150, 243, 0.1);
    }}

    .info-item i {{
        font-size: 1.2rem; /* Smaller icon */
        color: var(--primary);
    }}

    .info-item div {{
        display: flex;
        flex-direction: column;
    }}

    .info-item span {{
        font-size: 1.1rem; /* Smaller font */
        font-weight: 600;
        color: #2c3e50;
    }}

    .info-item label {{
        font-size: 0.75rem; /* Smaller label */
        color: #64748b;
        margin: 0;
    }}

    .instructions-card {{
        background: #fff06b;
        border-radius: 12px;
        padding: 1.2rem; /* Reduced padding */
        border: 1px solid rgba(33, 150, 243, 0.1);
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    }}

    .instructions-header {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(33, 150, 243, 0.1);
    }}

    .instructions-header i {{
        font-size: 1.2rem;
        color: var(--primary);
    }}

    .instructions-header h4 {{
        margin: 0;
        font-size: 1.1rem; /* Smaller font */
        font-weight: 600;
        color: #2c3e50;
    }}

    .instructions-grid {{
        display: grid;
        grid-template-columns: repeat(1, 1fr);
        gap: 0.8rem;
        padding: 0;
    }}

    .instruction-item {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem;
        background: #f8faff;
        border-radius: 10px;
        border: 1px solid rgba(33, 150, 243, 0.1);
        transition: all 0.3s ease;
    }}

    .instruction-item:hover {{
        transform: translateX(3px);
        background: #ffffff;
        border-color: var(--primary);
    }}

    .instruction-icon {{
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        flex-shrink: 0;
        font-size: 1rem;
        color: #ffffff;
        background: var(--primary);
    }}

    .instruction-icon.success {{ background: #4CAF50; }}
    .instruction-icon.danger {{ background: #F44336; }}
    .instruction-icon.warning {{ background: #FFC107; }}
    .instruction-icon.info {{ background: #FFC107; }}

    .instruction-text {{
        font-size: 0.9rem; /* Smaller font */
        color: #2c3e50;
        line-height: 1.4;
        font-weight: 500;
    }}

    .start-test-btn {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        width: 100%;
        padding: 0.8rem;
        margin-top: 1.5rem;
        background: linear-gradient(45deg, var(--dark), var(--dark));
        color: rgb(249, 249, 249);
        border: none;
        border-radius: 10px;
        font-size: 1rem; /* Smaller font */
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px #fff06b;
    }}

    .start-test-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px #b2a000;
    }}

    .start-test-btn i {{
        font-size: 1rem;
    }}

    .question-card {{
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem; /* Reduced margin */
        max-width: 100%; /* Use full width */
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        border: 1px solid var(--golden);
        animation: fadeIn 0.6s ease-out;
        overflow-x: hidden; /* Prevent horizontal overflow */
    }}

    .option-card {{
        background: rgb(255, 255, 255);
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.8rem 0.8rem 0.8rem 2.5rem; /* Adjusted padding */
        margin: 0.6rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        font-family: 'Poppins', sans-serif;
        font-size: 0.9rem;
        font-weight: 400;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .option-card:hover {{
        background: var(--light-blue);
        transform: translateX(3px);
        border-color: var(--primary);
    }}

    .option-card::before {{
        content: attr(data-option);
        position: absolute;
        left: 0;
        top: 0;
        width: 2rem;
        height: 100%;
        background: var(--light-blue);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: var(--primary);
        border-radius: 8px 0 0 8px;
    }}

    .option-card.selected {{
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }}

    .option-card.correct {{
        background: rgba(0, 200, 83, 0.2);
        border-color: var(--success);
    }}

    .option-card.incorrect {{
        background: rgba(213, 0, 0, 0.2);
        border-color: var(--danger);
    }}

    .question-box {{
        background: var(--light-blue);
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        color: #2c3e50;
        line-height: 1.5;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .question-box::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(to bottom, var(--primary), var(--golden));
        border-radius: 20px 0 0 20px;
    }}

    .stats-mini {{
        background: white;
        border-radius: 10px;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap; /* Allow wrapping */
    }}

    .stats-mini-item {{
        text-align: center;
        padding: 0 0.5rem;
        flex: 1;
    }}

    .stats-mini-icon {{
        width: 30px;
        height: 30px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.9rem;
        background: rgba(255, 255, 255, 0.1) !important;
    }}

    .stats-mini-value {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.2rem;
    }}

    .stats-mini-label {{
        font-size: 0.75rem;
        color: var(--gray);
        font-weight: 500;
    }}

    .bottom-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 0.8rem;
        box-shadow: 0 -3px 15px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
        border-top: 1px solid rgba(33, 150, 243, 0.1);
        overflow-x: hidden; /* Prevent horizontal overflow */
    }}

    .nav-btn {{
        padding: 0.6rem 1rem; /* Smaller padding */
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.85rem; /* Smaller font */
        transition: all 0.3s ease;
        min-width: 100px; /* Reduced min-width */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        border: none;
        background: white;
        color: var(--primary);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }}

    .nav-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.15);
        background: var(--primary);
        color: white;
    }}

    .nav-btn-primary {{
        background: var(--primary);
        color: white;
    }}

    .nav-btn-outline {{
        border: 2px solid var(--primary);
        color: var(--primary);
        background: white;
    }}

    .nav-btn:disabled {{
        opacity: 0.7;
        transform: none;
        cursor: not-allowed;
        background: #f5f5f5;
        color: #999;
        border-color: #ddd;
        box-shadow: none;
    }}

    .question-number {{
        font-size: 0.9rem;
        color: var(--gray);
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .question-text {{
        font-size: 1.1rem;
        line-height: 1.6;
        color: var(--dark);
        margin-bottom: 1.5rem;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .status-badge {{
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    .questions-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
        gap: 0.4rem;
        padding: 0.8rem;
    }}

    .grid-btn {{
        aspect-ratio: 1;
        border: 1px solid var(--primary);
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        background: white;
        color: var(--primary);
    }}

    .grid-btn:hover {{
        background: var(--primary);
        color: white;
    }}

    .grid-btn.btn-success {{
        background: var(--success);
    }}

    .grid-btn.btn-warning {{
        background: var(--warning);
        color: var(--dark);
    }}

    .grid-btn.btn-primary {{
        background: var(--accent);
    }}

    .modal-content {{
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid var(--golden);
    }}

    .modal-header {{
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(75, 54, 33, 0.9) 100%);
        color: var(--golden);
        border-radius: 15px 15px 0 0;
        padding: 1rem;
        border-bottom: 1px solid var(--golden);
    }}

    .modal-title {{
        font-weight: 600;
        font-size: 1.2rem;
    }}

    .btn-close {{
        filter: brightness(0) invert(1);
    }}

    .stats-card {{
        background: rgba(0, 0, 0, 0.5);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid var(--golden);
        animation: scaleIn 0.5s ease-out;
    }}

    .stats-card:hover {{
        transform: translateY(-3px);
        background: rgba(255, 215, 0, 0.1);
    }}

    .stats-value {{
        font-size: 1.5rem; /* Smaller font */
        font-weight: 700;
        color: var(--golden);
        margin-bottom: 0.4rem;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
    }}

    .stats-label {{
        color: var(--gray);
        font-weight: 500;
        font-size: 0.8rem;
    }}

    .stats-container {{
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin: 1rem 0;
        padding: 0 0.5rem;
        max-width: 100%; /* Use full width */
        margin-left: auto;
        margin-right: auto;
        flex-wrap: wrap; /* Allow wrapping */
    }}

    .stats-card {{
        flex: 1;
        min-width: 140px; /* Reduced min-width */
        background: #f8f9ff;
        border: 1px solid #eef0f7;
        border-radius: 8px;
        padding: 0.6rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        transition: all 0.2s ease;
    }}

    .instruction-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem;
        padding: 1rem;
        background: #f8f9ff;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }}

    .instruction-item {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.7rem;
        background: #0b1225;
        border-radius: 8px;
        border: 1px solid #eef0f7;
    }}

    .instruction-icon {{
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        flex-shrink: 0;
    }}

    .instruction-text {{
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.3;
    }}

    /* Modern Result Display */
    .score-animation {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem; /* Reduced padding */
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        max-width: 100%; /* Use full width */
        margin: 1rem; /* Reduced margin */
        text-align: center;
        position: relative;
        overflow: hidden;
    }}

    .score-animation::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
    }}

    .score-value {{
        font-size: 3rem; /* Smaller font */
        font-weight: 700;
        background: linear-gradient(45deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
    }}

    .stats-row {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 0 0.5rem;
    }}

    .stat-item {{
        background: linear-gradient(145deg, #ffffff, #f8faff);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(33, 150, 243, 0.1);
        transition: all 0.3s ease;
    }}

    .stat-item:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }}

    .stat-value {{
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
        background: linear-gradient(45deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .stat-label {{
        color: #64748b;
        font-weight: 500;
        font-size: 0.9rem;
    }}

    .wrong-answers-section {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(33, 150, 243, 0.1);
        overflow-x: hidden; /* Prevent horizontal overflow */
    }}

    .wrong-answer-card {{
        background: linear-gradient(145deg, #ffffff, #f8faff);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(33, 150, 243, 0.1);
        transition: all 0.3s ease;
        overflow-x: hidden; /* Prevent horizontal overflow */
    }}

    .wrong-answer-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }}

    .wrong-answer, .correct-answer {{
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .grid-btn.active {{
        background: var(--primary);
        color: white;
    }}

    .modal-content {{
        background: #fff06b;
        border: none;
        border-radius: 12px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        max-width: 100%; /* Ensure modal fits screen */
    }}

    .modal-header {{
        background: #fff06b;
        padding: 0.8rem 1.2rem;
        border-bottom: 1px solid #fff06b;
    }}

    .modal-title {{
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .modal-title i {{
        color: var(--dark);
        font-size: 0.9rem;
    }}

    .questions-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
        gap: 0.4rem;
        padding: 0.8rem;
    }}

    .grid-btn {{
        aspect-ratio: 1;
        border: 1px solid #eef0f7;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.8rem;
        transition: all 0.2s ease;
        background: white;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }}

    .grid-btn:hover {{
        background: #f8f9ff;
        border-color: var(--primary);
        color: var(--primary);
    }}

    .grid-btn.active {{
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }}

    .grid-btn.answered {{
        background: #e8f5e9;
        color: #2e7d32;
        border-color: #a5d6a7;
    }}

    .grid-btn.marked {{
        background: #fff3e0;
        color: #f57c00;
        border-color: #ffcc80;
    }}

    .grid-legend {{
        display: flex;
        justify-content: center;
        gap: 1rem;
        padding: 0.8rem;
        border-top: 1px solid #eef0f7;
    }}

    .legend-item {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.75rem;
        color: #64748b;
    }}

    .legend-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
    }}

    .question-card {{
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.8rem;
        max-width: 100%;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }}

    .question-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #eef0f7;
    }}

    .question-number {{
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}

    .question-number i {{
        color: var(--primary);
        font-size: 0.85rem;
    }}

    .question-status {{
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }}

    .question-box {{
        background: #f8f9ff;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        font-weight: 500;
        color: #2c3e50;
        line-height: 1.5;
        border: 1px solid #eef0f7;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .options-container {{
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }}

    .option-card {{
        background: white;
        border: 1px solid #eef0f7;
        border-radius: 6px;
        padding: 0.7rem 0.7rem 0.7rem 2.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem;
        font-weight: 400;
        color: #475569;
        display: flex;
        align-items: center;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .option-card:hover {{
        background: #f8f9ff;
        border-color: var(--primary);
        transform: translateX(2px);
    }}

    .option-card::before {{
        content: attr(data-option);
        position: absolute;
        left: 0;
        top: 0;
        width: 2rem;
        height: 100%;
        background: #f8f9ff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: var(--primary);
        font-size: 0.85rem;
        border-right: 1px solid #eef0f7;
    }}

    .option-card.selected {{
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }}

    .option-card.selected::before {{
        background: rgba(255,255,255,0.1);
        color: white;
        border-right: 1px solid rgba(255,255,255,0.2);
    }}

    .option-card.correct {{
        background: #e8f5e9;
        color: #2e7d32;
        border-color: #a5d6a7;
    }}

    .option-card.incorrect {{
        background: #ffebee;
        color: #c62828;
        border-color: #ef9a9a;
    }}

    /* Modern Disclaimer */
    .disclaimer-alert {{
        background: #fff06b;
        border-radius: 12px;
        padding: 1.2rem;
        display: flex;
        gap: 1rem;
        box-shadow: 0 3px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(33, 150, 243, 0.1);
        position: relative;
        overflow: hidden;
    }}

    .disclaimer-alert::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 3px;
        background: linear-gradient(to bottom, #02217e, #02217e);
    }}

    .disclaimer-icon {{
        font-size: 1.5rem;
        color: #2196F3;
        flex-shrink: 0;
    }}

    .disclaimer-content h4 {{
        color: #2c3e50;
        margin-bottom: 0.8rem;
        font-weight: 600;
        font-size: 1.1rem;
    }}

    .disclaimer-content p {{
        color: #505c6d;
        line-height: 1.5;
        font-size: 0.9rem;
    }}

    .disclaimer-content a {{
        color: #2196F3;
        text-decoration: none;
        font-weight: 500;
    }}

    .disclaimer-content a:hover {{
        text-decoration: underline;
    }}

    /* Join Channel Modal */
    #joinChannelModal .modal-content {{
        border: none;
        border-radius: 16px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        max-width: 100%; /* Ensure modal fits screen */
    }}

    #joinChannelModal .modal-header {{
        background: linear-gradient(45deg, #001757, #0b1225);
        border: none;
        padding: 1rem;
    }}

    #joinChannelModal .btn-close {{
        color: #ffffff;
        opacity: 1;
        filter: brightness(0) invert(1);
    }}

    #joinChannelModal .modal-body {{
        padding: 1.5rem;
    }}

    #joinChannelModal .btn-primary {{
        background: linear-gradient(45deg, #facc15, #facc15);
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-weight: 500;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.3);
        transition: all 0.3s ease;
    }}

    #joinChannelModal .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4);
    }}

    /* Modern Navigation Buttons */
    .nav-action-btn {{
        border: 1px solid #e2e8f0;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
    }}

    .nav-action-btn:hover {{
        transform: translateY(-2px);
        border-color: #2196F3;
        color: #2196F3;
    }}

    .nav-action-btn.submit-btn {{
        background: linear-gradient(45deg, #091c50, #091c50);
        border: none;
        color: white;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.3);
    }}

    .nav-action-btn.submit-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.4);
    }}

    /* Question Navigation Grid */
    .questions-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
        gap: 0.6rem;
        padding: 1rem;
    }}

    .grid-btn {{
        aspect-ratio: 1;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        background: white;
        color: #4a5568;
    }}

    .grid-btn:hover {{
        background: #f8f9fa;
        border-color: #2196F3;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
    }}

    .grid-btn.active {{
        background: #2196F3;
        color: white;
        border-color: #2196F3;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
    }}

    .grid-btn.answered {{
        background: #48bb78;
        color: white;
        border-color: #48bb78;
    }}

    .grid-btn.marked {{
        background: #ecc94b;
        color: #744210;
        border-color: #ecc94b;
    }}

    /* Wrong Answers Display */
    .wrong-answer-card {{
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #eef0f7;
        overflow-x: hidden; /* Prevent horizontal overflow */
    }}

    .wrong-answer-card .question-text {{
        font-size: 1rem;
        color: #2c3e50;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #eef0f7;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .wrong-answer, .correct-answer {{
        padding: 0.8rem;
        border-radius: 10px;
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        margin-bottom: 0.4rem;
        word-wrap: break-word; /* Ensure text wraps */
    }}

    .wrong-answer {{
        background: #fff5f5;
        color: #e53e3e;
    }}

    .correct-answer {{
        background: #f0fff4;
        color: #38a169;
    }}

    .wrong-answer i, .correct-answer i {{
        font-size: 1rem;
        margin-top: 0.2rem;
    }}

    /* Mobile Responsiveness */
    @media (max-width: 768px) {{
        body {{
            font-size: 13px;
            padding-bottom: 60px;
            overflow-x: hidden; /* Ensure no horizontal scrolling */
        }}
        
        .container, .container-fluid {{
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}

        .navbar {{
            padding: 0.5rem;
        }}

        .navbar-brand {{
            font-size: 1rem;
        }}

        .navbar-actions {{
            gap: 0.3rem;
        }}

        .nav-btn {{
            padding: 0.4rem 0.8rem;
            min-width: 80px;
            font-size: 0.75rem;
        }}
        
        .nav-btn span {{
            display: none;
        }}
        
        .welcome-screen, .question-card, .score-animation, .wrong-answers-section {{
            margin: 0.5rem;
            padding: 1rem;
            max-width: calc(100% - 1rem); /* Ensure fits within viewport */
        }}

        .test-info-body {{
            grid-template-columns: 1fr;
            gap: 0.8rem;
        }}

        .info-item {{
            padding: 0.6rem;
        }}

        .info-item i {{
            font-size: 1rem;
        }}

        .info-item span {{
            font-size: 1rem;
        }}

        .instructions-grid {{
            grid-template-columns: 1fr;
            gap: 0.6rem;
        }}

        .instruction-item {{
            padding: 0.6rem;
        }}

        .instruction-icon {{
            width: 30px;
            height: 30px;
            font-size: 0.9rem;
        }}

        .instruction-text {{
            font-size: 0.85rem;
        }}

        .start-test-btn {{
            padding: 0.6rem;
            font-size: 0.9rem;
        }}

        .stats-mini {{
            padding: 0.6rem;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .stats-mini-item {{
            padding: 0 0.4rem;
            min-width: 80px;
        }}
        
        .stats-mini-icon {{
            width: 25px;
            height: 25px;
            font-size: 0.8rem;
        }}
        
        .stats-mini-value {{
            font-size: 1.1rem;
        }}
        
        .stats-mini-label {{
            font-size: 0.7rem;
        }}

        .option-card {{
            padding: 0.6rem 0.6rem 0.6rem 2rem;
            font-size: 0.8rem;
        }}

        .option-card::before {{
            width: 1.8rem;
            font-size: 0.8rem;
        }}

        .bottom-nav {{
            padding: 0.6rem;
            flex-wrap: nowrap; /* Prevent buttons from wrapping */
            gap: 0.5rem;
        }}

        .stats-container {{
            padding: 0 0.3rem;
            gap: 0.6rem;
            flex-wrap: wrap;
        }}
        
        .stats-card {{
            min-width: 120px;
            padding: 0.5rem;
            gap: 0.5rem;
        }}
        
        .stats-card i {{
            font-size: 0.9rem;
            width: 25px;
            height: 25px;
        }}
        
        .stats-value {{
            font-size: 0.8rem;
        }}
        
        .stats-label {{
            font-size: 0.65rem;
        }}

        .instruction-grid {{
            grid-template-columns: 1fr;
            gap: 0.6rem;
            padding: 0.8rem;
        }}
        
        .instruction-item {{
            padding: 0.6rem;
        }}
        
        .instruction-icon {{
            width: 25px;
            height: 25px;
        }}
        
        .instruction-text {{
            font-size: 0.8rem;
        }}

        .score-value {{
            font-size: 2.5rem;
        }}

        .stats-row {{
            grid-template-columns: 1fr 1fr;
            gap: 0.8rem;
        }}

        .stat-item {{
            padding: 1rem;
        }}

        .stat-value {{
            font-size: 1.5rem;
        }}

        .stat-label {{
            font-size: 0.8rem;
        }}

        .wrong-answer-card {{
            padding: 1rem;
            margin: 0.4rem;
        }}

        .wrong-answer, .correct-answer {{
            padding: 0.6rem;
            font-size: 0.8rem;
        }}

        .questions-grid {{
            grid-template-columns: repeat(auto-fill, minmax(30px, 1fr));
            gap: 0.3rem;
            padding: 0.6rem;
        }}

        .grid-btn {{
            font-size: 0.75rem;
        }}

        .question-box {{
            padding: 0.8rem;
            font-size: 0.9rem;
        }}

        .option-card {{
            padding: 0.6rem 0.6rem 0.6rem 2rem;
            font-size: 0.8rem;
        }}

        .option-card::before {{
            width: 1.8rem;
            font-size: 0.8rem;
        }}

        .legend-item {{
            font-size: 0.7rem;
        }}

        .disclaimer-alert {{
            padding: 1rem;
            gap: 0.8rem;
        }}

        .disclaimer-content h4 {{
            font-size: 1rem;
        }}

        .disclaimer-content p {{
            font-size: 0.85rem;
        }}

        #joinChannelModal .modal-body {{
            padding: 1rem;
        }}

        #joinChannelModal .btn-primary {{
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }}

        .nav-action-btn {{
            padding: 0.4rem 0.8rem;
            font-size: 0.75rem;
        }}
    }}

    @media (max-width: 576px) {{
        body {{
            font-size: 12px;
        }}

        .navbar {{
            padding: 0.4rem;
        }}

        .navbar-brand {{
            font-size: 1.2rem;
        }}

        .navbar-brand i {{
            font-size: 1.2rem;
        }}

        .timer {{
            padding: 0.3rem 0.6rem;
            font-size: 0.7rem;
        }}

        .nav-action-btn {{
            padding: 0.3rem 0.6rem;
            font-size: 0.7rem;
        }}

        .welcome-screen, .question-card, .score-animation, .wrong-answers-section {{
            margin: 0.3rem;
            padding: 0.8rem;
        }}

        .test-info-card {{
            padding: 0.8rem;
        }}

        .test-info-header h3 {{
            font-size: 1rem;
        }}

        .test-info-header i {{
            font-size: 1.5rem;
            padding: 0.6rem;
        }}

        .info-item {{
            padding: 0.5rem;
        }}

        .info-item i {{
            font-size: 0.9rem;
        }}

        .info-item span {{
            font-size: 0.9rem;
        }}

        .info-item label {{
            font-size: 0.65rem;
        }}

        .instructions-card {{
            padding: 0.8rem;
        }}

        .instructions-header h4 {{
            font-size: 1rem;
        }}

        .instructions-header i {{
            font-size: 1rem;
        }}

        .instruction-item {{
            padding: 0.5rem;
        }}

        .instruction-icon {{
            width: 25px;
            height: 25px;
            font-size: 0.8rem;
        }}

        .instruction-text {{
            font-size: 0.75rem;
        }}

        .start-test-btn {{
            padding: 0.5rem;
            font-size: 0.8rem;
        }}

        .stats-mini {{
            padding: 0.5rem;
            gap: 0.5rem;
        }}

        .stats-mini-item {{
            min-width: 70px;
        }}

        .stats-mini-icon {{
            width: 20px;
            height: 20px;
            font-size: 0.7rem;
        }}

        .stats-mini-value {{
            font-size: 1rem;
        }}

        .stats-mini-label {{
            font-size: 0.65rem;
        }}

        .bottom-nav {{
            padding: 0.5rem;
            gap: 0.3rem;
        }}

        .nav-btn {{
            padding: 0.4rem 0.6rem;
            min-width: 70px;
            font-size: 0.7rem;
        }}

        .stats-container {{
            gap: 0.5rem;
        }}

        .stats-card {{
            min-width: 100px;
            padding: 0.4rem;
        }}

        .stats-card i {{
            font-size: 0.8rem;
            width: 20px;
            height: 20px;
        }}

        .stats-value {{
            font-size: 0.7rem;
        }}

        .stats-label {{
            font-size: 0.6rem;
        }}

        .score-value {{
            font-size: 2rem;
        }}

        .stats-row {{
            grid-template-columns: 1fr;
            gap: 0.6rem;
        }}

        .stat-item {{
            padding: 0.8rem;
        }}

        .stat-value {{
            font-size: 1.2rem;
        }}

        .stat-label {{
            font-size: 0.75rem;
        }}

        .wrong-answer-card {{
            padding: 0.8rem;
            margin: 0.3rem;
        }}

        .wrong-answer, .correct-answer {{
            padding: 0.5rem;
            font-size: 0.75rem;
        }}

        .wrong-answer i, .correct-answer i {{
            font-size: 0.9rem;
        }}

        .questions-grid {{
            grid-template-columns: repeat(auto-fill, minmax(25px, 1fr));
            gap: 0.3rem;
            padding: 0.5rem;
        }}

        .grid-btn {{
            font-size: 0.7rem;
        }}

        .question-box {{
            padding: 0.6rem;
            font-size: 0.85rem;
        }}

        .option-card {{
            padding: 0.5rem 0.5rem 0.5rem 1.8rem;
            font-size: 0.75rem;
        }}

        .option-card::before {{
            width: 1.6rem;
            font-size: 0.75rem;
        }}

        .legend-item {{
            font-size: 0.65rem;
        }}

        .disclaimer-alert {{
            padding: 0.8rem;
            gap: 0.6rem;
        }}

        .disclaimer-content h4 {{
            font-size: 0.9rem;
        }}

        .disclaimer-content p {{
            font-size: 0.8rem;
        }}

        #joinChannelModal .modal-body {{
            padding: 0.8rem;
        }}

        #joinChannelModal .btn-primary {{
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }}

        .nav-action-btn {{
            padding: 0.3rem 0.6rem;
            font-size: 0.65rem;
        }}

        .header-image {{
              width: 50px;   /* logo jitna chhota karne ke liye width adjust karo */
            height: auto;  /* image proportion maintain rahegi */
}}


        
    }}
</style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div class="container-fluid">
            <a href="https://t.me/iamNinjastudy" target="_blank" class="navbar-brand">
                 <img src="https://i.postimg.cc/TYBCHbJc/logo.png" alt="Ninja Study Header" class="header-image" style="width:50px; height:auto;">
                NINJA STUDY
                 
                
            </a>
            <!-- Before test starts -->
            <div class="navbar-actions" id="pre-test-actions">
                <a href="{website_url}" target="_blank" class="nav-action-btn website-btn">
                <i class="fas fa-globe"></i>
                    Visit Website
                </a>
            </div>
            <!-- After test starts -->
            <div class="navbar-actions" id="test-actions" style="display: none;">
                <div class="timer" id="timer">
                    <i class="far fa-clock me-2"></i>00:00:00
                </div>
                <button class="nav-action-btn overview-btn" onclick="showQuestionsGrid()">
                    <i class="fas fa-th"></i>
                    Overview
                </button>
                <button class="nav-action-btn submit-btn" onclick="confirmSubmit()">
                    <i class="fas fa-paper-plane"></i>
                    Submit
                </button>
            </div>
        </div>
    </nav>

    <!-- Join Channel Popup -->
    <div class="modal fade" id="joinChannelModal">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-0 pb-0">
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center p-4">
                    <div class="mb-4">
                       <img src="https://i.postimg.cc/TYBCHbJc/logo.png" alt="Ninja Study Header" class="header-image" style="width:80px; height:auto;">
                    </div>
                    <h3 class="mb-3">Ninja Study!</h3>
                    <p class="text-muted mb-4">Get access to more free tests and study materials!</p>
                    <a href="https://t.me/iamNinjastudy" target="_blank" class="btn btn-primary btn-lg w-100 rounded-pill">
                        <i class="fab fa-telegram me-2"></i>Join Now
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Welcome Screen (Enhanced) -->
    <div class="welcome-screen" id="welcome-screen">
        <div class="welcome-header">
            <div class="welcome-icon">
                <i class="fas fa-graduation-cap"></i>
            </div>
            <div class="welcome-title">
                 <h2>{welcome_title}</h2>
                <p>Powered by <a href="https://t.me/iamNinjastudy" target="_blank">Ninja study</a></p>
            </div>
        </div>

        <!-- Modern Disclaimer -->
        <div class="disclaimer-alert mb-4">
            <div class="-content">
                <div class="disclaimer-badge">
                    <i class="fas fa-shield-alt"></i>
                    Important Notice
                </div>
                <div class="disclaimer-text">
                    <p class="mb-2">🎯 This test series is provided to help you prepare smarter and achieve higher scores with confidence! <strong>FREE</strong> by <a href="https://t.me/iamNinjastudy" target="_blank">Ninja Study</a></p>
                    <p class="mb-2">📚 Prepare Smarter, Score Higher! 🚀Boost your success with our expertly curated test series – your key to exam excellence.</p>
                    <div class="disclaimer-features">
                        <div class="feature-item">
                            <i class="fas fa-check-circle"></i>
                            High Quality Questions
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check-circle"></i>
                            Detailed Solutions
                        </div>
                        <div class="feature-item">
                            <i class="fas fa-check-circle"></i>
                            Real Exam Pattern
                        </div>
                    </div>
                    <hr>
                    <p class="small text-muted mb-0">
                        Content belongs to respective institutes. This is an unofficial version for practice only.
                    </p>
                </div>
            </div>
        </div>

        <div class="test-info-card mb-4">
            <div class="test-info-header">
                <i class="fas fa-graduation-cap"></i>
                <h3>{test_title}</h3>
            </div>
            <div class="test-info-body">
                <div class="info-item">
                    <i class="fas fa-question-circle"></i>
                    <div>
                        <span id="total-questions">0</span>
                        <label>Questions</label>
                    </div>
                </div>
                <div class="info-item">
                    <i class="fas fa-clock"></i>
                    <div>
                        <span>{minutes_value}</span>
                        <label>Minutes</label>
                    </div>
                </div>
                <div class="info-item">
                    <i class="fas fa-star"></i>
                    <div>
                        <span id="total-marks">0</span>
                        <label>Total Marks</label>
                    </div>
                </div>
            </div>
        </div>

        <div class="instructions-card">
            <div class="instructions-header">
                <i class="fas fa-info-circle"></i>
                <h4>Test Instructions</h4>
            </div>
            <div class="instructions-grid">
                <div class="instruction-item">
                    <div class="instruction-icon success">
                        <i class="fas fa-check"></i>
                    </div>
                    <div class="instruction-text">
                        Each correct answer earns positive marks
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-icon danger">
                        <i class="fas fa-minus"></i>
                    </div>
                    <div class="instruction-text">
                        Wrong answers have negative marking
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-icon warning">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="instruction-text">
                        You can change answers before final submission
                    </div>
                </div>
                <div class="instruction-item">
                    <div class="instruction-icon info">
                        <i class="fas fa-bookmark"></i>
                    </div>
                    <div class="instruction-text">
                        Mark important questions for review
                    </div>
                </div>
            </div>
        </div>

        <button class="start-test-btn" onclick="startTest()">
            <i class="fas fa-play"></i>
            Start Test
        </button>
    </div>

    <!-- Test Content -->
    <div id="test-content" style="display: none;">
        <div class="container py-4">
            <!-- Stats Mini Section (Modified to show only total and attempted) -->
            <div class="stats-mini">
                <div class="stats-mini-item">
                    <div class="stats-mini-icon" style="background: var(--primary)">
                        <i class="fas fa-tasks"></i>
                    </div>
                    <div>
                        <div class="stats-mini-value" id="mini-total">0/0</div>
                        <div class="stats-mini-label">Total Questions</div>
                    </div>
                </div>
                <div class="stats-mini-item">
                    <div class="stats-mini-icon" style="background: var(--success)">
                        <i class="fas fa-check"></i>
                    </div>
                    <div>
                        <div class="stats-mini-value" id="mini-attempted">0</div>
                        <div class="stats-mini-label">Attempted</div>
                    </div>
                </div>
                <div class="stats-mini-item">
                    <div class="stats-mini-icon" style="background: var(--warning)">
                        <i class="fas fa-minus-circle"></i>
                    </div>
                    <div>
                        <div class="stats-mini-value" id="mini-skipped">0</div>
                        <div class="stats-mini-label">Skipped</div>
                    </div>
                </div>
            </div>
            <div class="question-card">
                <div class="question-header">
                    <div class="question-number">
                        <i class="fas fa-pencil-alt"></i>
                        Question <span id="current-question">1</span> of <span id="total-questions">0</span>
                    </div>
                    <div class="question-status" id="question-status"></div>
                </div>
                <div class="question-box" id="question-container"></div>
                <div class="options-container" id="options-container"></div>
            </div>
        </div>
    </div>

    <!-- Bottom Navigation -->
    <div class="bottom-nav" id="bottom-nav" style="display: none;">
        <button class="nav-btn nav-btn-outline" onclick="prevQuestion()" id="prev-btn">
            <i class="fas fa-chevron-left"></i>
            <span>Previous</span>
        </button>
        <button class="nav-btn nav-btn-primary" onclick="markForReview()" id="review-btn">
            <i class="fas fa-bookmark"></i>
            <span>Review</span>
        </button>
        <button class="nav-btn nav-btn-outline" onclick="nextQuestion()" id="next-btn">
            <i class="fas fa-chevron-right"></i>
            <span>Next</span>
        </button>
    </div>

    <!-- Questions Grid Modal -->
    <div class="modal fade" id="questionsModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-th"></i>
                        Questions Overview
                    </h5>
                    <button type="button" class="btn-close-modern" data-bs-dismiss="modal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body p-0">
                    <div class="questions-grid" id="questions-grid"></div>
                    <div class="grid-legend">
                        <div class="legend-item">
                            <div class="legend-dot" style="background: var(--primary)"></div>
                            <span>Current</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-dot" style="background: #2e7d32"></div>
                            <span>Answered</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-dot" style="background: #f57c00"></div>
                            <span>Marked</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add this modal HTML before closing body tag -->
    <div class="modal fade" id="submitConfirmModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header border-0">
                    <h5 class="modal-title">
                        <i class="fas fa-paper-plane text-primary me-2"></i>
                        Submit Test
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="submit-stats mb-4">
                        <div class="submit-stat-item">
                            <div class="submit-stat-icon bg-success">
                                <i class="fas fa-check"></i>
                            </div>
                            <div class="submit-stat-info">
                                <div class="submit-stat-value" id="submit-attempted">0</div>
                                <div class="submit-stat-label">Attempted</div>
                            </div>
                        </div>
                        <div class="submit-stat-item">
                            <div class="submit-stat-icon bg-warning">
                                <i class="fas fa-bookmark"></i>
                            </div>
                            <div class="submit-stat-info">
                                <div class="submit-stat-value" id="submit-marked">0</div>
                                <div class="submit-stat-label">Marked for Review</div>
                            </div>
                        </div>
                        <div class="submit-stat-item">
                            <div class="submit-stat-icon bg-danger">
                                <i class="fas fa-times"></i>
                            </div>
                            <div class="submit-stat-info">
                                <div class="submit-stat-value" id="submit-unattempted">0</div>
                                <div class="submit-stat-label">Not Attempted</div>
                            </div>
                        </div>
                    </div>
                    <div class="alert alert-warning mb-4">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Are you sure you want to submit? You cannot change your answers after submission.
                    </div>
                    <div class="d-flex justify-content-end gap-2">
                        <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>
                            Cancel
                        </button>
                        <button type="button" class="btn btn-primary px-4" onclick="finalSubmit()">
                            <i class="fas fa-check me-2"></i>
                            Submit Test
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize variables
        let currentQuestion = 0;
        let answers = {{}};
        let markedForReview = {{}};
        let submitted = false;
        let testStarted = false;
        let startTime = null;
        let endTime = null;
        
        // Load questions data
        const questions = {questions}
          const totalTime = {total_time_expression}; // Convert minutes to seconds
        
        
        // Initialize the test
        window.onload = function() {{
            document.getElementById('total-questions').textContent = questions.length;
            let totalMarks = questions.reduce((sum, q) => sum + parseFloat(q.positive_marks || 0), 0);
            document.getElementById('total-marks').textContent = totalMarks;
            generateQuestionsGrid();
            
            setTimeout(() => {{
                new bootstrap.Modal(document.getElementById('joinChannelModal')).show();
            }}, 2000);
        }};

        function startTest() {{
            if (!testStarted) {{
                testStarted = true;
                startTime = new Date();
                endTime = new Date(startTime.getTime() + totalTime * 1000);
                document.getElementById('welcome-screen').style.display = 'none';
                document.getElementById('test-content').style.display = 'block';
                document.getElementById('bottom-nav').style.display = 'flex';
                document.getElementById('pre-test-actions').style.display = 'none';
                document.getElementById('test-actions').style.display = 'flex';
                showQuestion(0);
                startTimer();
            }}
        }}

        function showQuestion(index) {{
            try {{
                if (index < 0 || index >= questions.length) return;
                
                currentQuestion = index;
                const question = questions[index];
                
                // Create question HTML first
                const questionHTML = `
                    <div class="question-header">
                        <div class="question-number">
                            <i class="fas fa-pencil-alt"></i>
                            Question ${{index + 1}} of ${{questions.length}}
                        </div>
                        <div class="question-status" id="question-status"></div>
                    </div>
                    <div class="question-box">${{question.question}}</div>
                    <div class="options-container">
                        ${{generateOptionsHtml(question, index)}}
                    </div>
                `;
                
                // Update question container with animation
                const container = document.querySelector('.question-card');
                if (!container) {{
                    console.error('Question container not found');
                    return;
                }}
                
                // Update stats elements if they exist
                const currentQuestionEl = document.getElementById('current-question');
                const totalQuestionsEl = document.getElementById('total-questions');
                
                if (currentQuestionEl) currentQuestionEl.textContent = index + 1;
                if (totalQuestionsEl) totalQuestionsEl.textContent = questions.length;
                
                // Animate container
                container.style.opacity = '0';
                container.style.transform = 'translateY(20px)';
                
                setTimeout(() => {{
                    container.innerHTML = questionHTML;
                    container.style.opacity = '1';
                    container.style.transform = 'translateY(0)';
                    
                    // Update status after new content is added
                    updateQuestionStatus();
                    updateNavigationButtons();
                    updateQuestionsGrid();
                    updateMiniStats();
                }}, 300);
                
            }} catch (error) {{
                console.error('Error in showQuestion:', error);
            }}
        }}

        function generateOptionsHtml(question, qIndex) {{
            let options = [];
            for (let i = 1; i <= 10; i++) {{
                let optionKey = `option_${{i}}`;
                let optionImageKey = `option_image_${{i}}`;
                if (question[optionKey] && question[optionKey].trim()) {{
                    options.push({{
                        text: question[optionKey],
                        image: question[optionImageKey] || ''
                    }});
                }}
            }}
            
            const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
            return options.map((option, index) => `
                <div class="option-card ${{answers[qIndex] === index ? 'selected' : ''}}" 
                    onclick="selectAnswer(${{qIndex}}, ${{index}})"
                    data-option="${{letters[index]}}">
                    ${{option.text}}
                    ${{option.image ? `<img src="${{option.image}}" class="img-fluid mt-2">` : ''}}
                </div>
            `).join('');
        }}

        function selectAnswer(qIndex, optionIndex) {{
            if (submitted) return; // Don't allow changes after submission
            
            answers[qIndex] = optionIndex;
            
            // Update option styling
            const options = document.querySelectorAll('.option-card');
            options.forEach((option, idx) => {{
                if (idx === optionIndex) {{
                    option.classList.add('selected');
                }} else {{
                    option.classList.remove('selected');
                }}
            }});
            
            updateQuestionStatus();
            updateQuestionsGrid();
            updateMiniStats();
        }}

        function updateMiniStats() {{
            try {{
                const total = questions.length;
                const attempted = Object.keys(answers).length;
                const marked = Object.keys(markedForReview).length;
                const unattempted = total - attempted;
                
                const miniTotalEl = document.getElementById('mini-total');
                const miniAttemptedEl = document.getElementById('mini-attempted');
                const miniSkippedEl = document.getElementById('mini-skipped');
                
                if (miniTotalEl) miniTotalEl.textContent = `${{currentQuestion + 1}}/${{total}}`;
                if (miniAttemptedEl) miniAttemptedEl.textContent = attempted;
                if (miniSkippedEl) miniSkippedEl.textContent = unattempted;
            }} catch (error) {{
                console.error('Error in updateMiniStats:', error);
            }}
        }}

        function updateQuestionStatus() {{
            try {{
                const statusElement = document.getElementById('question-status');
                if (!statusElement) return;
                
                if (answers[currentQuestion] !== undefined) {{
                    statusElement.className = 'question-status bg-success text-white';
                    statusElement.innerHTML = '<i class="fas fa-check me-2"></i>Attempted';
                }} else if (markedForReview[currentQuestion]) {{
                    statusElement.className = 'question-status bg-warning text-white';
                    statusElement.innerHTML = '<i class="fas fa-bookmark me-2"></i>Marked for Review';
                }} else {{
                    statusElement.className = 'question-status bg-danger text-white';
                    statusElement.innerHTML = '<i class="fas fa-times me-2"></i>Not Attempted';
                }}
            }} catch (error) {{
                console.error('Error in updateQuestionStatus:', error);
            }}
        }}

        function updateNavigationButtons() {{
            try {{
                const prevBtn = document.getElementById('prev-btn');
                const nextBtn = document.getElementById('next-btn');
                
                if (prevBtn) prevBtn.disabled = currentQuestion === 0;
                if (nextBtn) nextBtn.disabled = currentQuestion === questions.length - 1;
            }} catch (error) {{
                console.error('Error in updateNavigationButtons:', error);
            }}
        }}

        function generateQuestionsGrid() {{
            try {{
                const grid = document.getElementById('questions-grid');
                if (!grid) return;
                
                grid.innerHTML = questions.map((_, index) => `
                    <button class="grid-btn ${{getQuestionButtonClass(index)}}" 
                            onclick="showQuestion(${{index}})"
                            type="button">
                        ${{index + 1}}
                    </button>
                `).join('');
            }} catch (error) {{
                console.error('Error in generateQuestionsGrid:', error);
            }}
        }}

        function getQuestionButtonClass(index) {{
            if (index === currentQuestion) return 'active';
            if (answers[index] !== undefined) return 'answered';
            if (markedForReview[index]) return 'marked';
            return '';
        }}

        function updateQuestionsGrid() {{
            try {{
                const grid = document.getElementById('questions-grid');
                if (!grid) return;
                
                const buttons = grid.querySelectorAll('.grid-btn');
                buttons.forEach((btn, index) => {{
                    btn.className = `grid-btn ${{getQuestionButtonClass(index)}}`;
                }});
            }} catch (error) {{
                console.error('Error in updateQuestionsGrid:', error);
            }}
        }}

        function markForReview() {{
            if (submitted) return; // Don't allow changes after submission
            
            markedForReview[currentQuestion] = !markedForReview[currentQuestion];
            updateQuestionStatus();
            updateQuestionsGrid();
        }}

        function nextQuestion() {{
            try {{
                if (currentQuestion < questions.length - 1) {{
                    showQuestion(currentQuestion + 1);
                }}
            }} catch (error) {{
                console.error('Error in nextQuestion:', error);
            }}
        }}

        function prevQuestion() {{
            try {{
                if (currentQuestion > 0) {{
                    showQuestion(currentQuestion - 1);
                }}
            }} catch (error) {{
                console.error('Error in prevQuestion:', error);
            }}
        }}

        function startTimer() {{
            const timerElement = document.getElementById('timer');
            const timerInterval = setInterval(() => {{
                if (!testStarted || submitted) {{
                    clearInterval(timerInterval);
                    return;
                }}

                const now = new Date();
                const timeLeft = Math.max(0, Math.floor((endTime - now) / 1000));
                
                if (timeLeft === 0) {{
                    clearInterval(timerInterval);
                    submitTest();
                    return;
                }}

                const hours = Math.floor(timeLeft / 3600);
                const minutes = Math.floor((timeLeft % 3600) / 60);
                const seconds = timeLeft % 60;
                
                timerElement.innerHTML = `
                    <i class="far fa-clock me-2"></i>
                    ${{String(hours).padStart(2, '0')}}:${{String(minutes).padStart(2, '0')}}:${{String(seconds).padStart(2, '0')}}
                `;
            }}, 1000);
        }}

        function showQuestionsGrid() {{
            try {{
                const modal = document.getElementById('questionsModal');
                if (!modal) return;
                
                // Ensure grid is updated before showing
                generateQuestionsGrid();
                new bootstrap.Modal(modal).show();
            }} catch (error) {{
                console.error('Error in showQuestionsGrid:', error);
            }}
        }}

        // Add keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (!testStarted || submitted) return;
            
            switch(e.key) {{
                case 'ArrowLeft':
                    prevQuestion();
                    break;
                case 'ArrowRight':
                    nextQuestion();
                    break;
                case '1': case '2': case '3': case '4':
                    const optionIndex = parseInt(e.key) - 1;
                    selectAnswer(currentQuestion, optionIndex);
                    break;
            }}
        }});

        function submitTest() {{
            if (submitted) return; // Prevent double submission

            
            
            submitted = true;
            testStarted = false;
            
            let correct = 0;
            let incorrect = 0;
            let totalMarks = 0;
            let wrongAnswers = [];
            
            questions.forEach((q, index) => {{
                if (answers[index] !== undefined) {{
                    let selectedOptionText = q[`option_${{answers[index] + 1}}`];
                    let correctOptionText = q[`option_${{q.answer}}`];
                    
                    if (answers[index] === parseInt(q.answer) - 1) {{
                        correct++;
                        totalMarks += parseFloat(q.positive_marks);
                    }} else {{
                        incorrect++;
                        totalMarks -= parseFloat(q.negative_marks);
                        wrongAnswers.push({{
                            questionNum: index + 1,
                            question: q.question,
                            yourAnswer: selectedOptionText,
                            correctAnswer: correctOptionText
                        }});
                    }}
                }}
            }});
            
            // Save wrong answers to localStorage
            localStorage.setItem('wrongAnswers', JSON.stringify(wrongAnswers));
            
            const wrongAnswersHtml = wrongAnswers.map(wa => `
                <div class="wrong-answer-card">
                    <div class="question-text mb-2">Q${{wa.questionNum}}. ${{wa.question}}</div>
                    <div class="d-flex gap-3">
                        <div class="wrong-answer">
                            <i class="fas fa-times-circle text-danger"></i>
                            Your Answer: Option ${{wa.yourAnswer}}
                        </div>
                        <div class="correct-answer">
                            <i class="fas fa-check-circle text-success"></i>
                            Correct Answer: Option ${{wa.correctAnswer}}
                        </div>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('test-content').innerHTML = `
                <div class="score-animation">
                    <div class="mb-4">
                        <i class="fas fa-award fa-3x text-primary"></i>
                    </div>
                    <div class="score-value">${{totalMarks.toFixed(2)}}</div>
                    <div class="h4 mb-4">Your Final Score</div>
                    
                    <div class="stats-row">
                        <div class="stat-item">
                            <div class="stat-value text-success">${{correct}}</div>
                            <div class="stat-label">Correct</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value text-danger">${{incorrect}}</div>
                            <div class="stat-label">Incorrect</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value text-warning">${{questions.length - (correct + incorrect)}}</div>
                            <div class="stat-label">Skipped</div>
                        </div>
                    </div>
                    
                    ${{incorrect > 0 ? `
                        <div class="wrong-answers-section mt-4">
                            <h5 class="mb-3">Review Incorrect Answers</h5>
                            ${{wrongAnswers.map(wa => `
                                <div class="wrong-answer-card">
                                    <div class="question-text">
                                        <strong>Question ${{wa.questionNum}}:</strong><br>
                                        ${{wa.question}}
                                    </div>
                                    <div class="answer-details">
                                        <div class="wrong-answer">
                                            <i class="fas fa-times-circle"></i>
                                            <div>
                                                <strong>Your Answer:</strong><br>
                                                ${{wa.yourAnswer}}
                                            </div>
                                        </div>
                                        <div class="correct-answer">
                                            <i class="fas fa-check-circle"></i>
                                            <div>
                                                <strong>Correct Answer:</strong><br>
                                                ${{wa.correctAnswer}}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}}
                        </div>
                    ` : ''}}
                </div>
            `;
            document.getElementById('bottom-nav').style.display = 'none';
        }}

        function confirmSubmit() {{
            // Calculate stats
            const total = questions.length;
            const attempted = Object.keys(answers).length;
            const marked = Object.keys(markedForReview).length;
            const unattempted = total - attempted;

            // Update stats in modal
            document.getElementById('submit-attempted').textContent = attempted;
            document.getElementById('submit-marked').textContent = marked;
            document.getElementById('submit-unattempted').textContent = unattempted;

            // Show modal
            new bootstrap.Modal(document.getElementById('submitConfirmModal')).show();
        }}

        // Add new function for final submission
        function finalSubmit() {{
            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('submitConfirmModal')).hide();
            // Submit test
            submitTest();
        }}
    </script>
</body>
</html>"""
        
        # Create a temporary file for the output with the same name as original
        output_filename = tempfile.mktemp(suffix=original_filename)
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            output_file.write(new_html)
        
        # Send the new HTML file back to the user with the same filename
        with open(output_filename, 'rb') as output_file:
            await update.message.reply_document(
                document=output_file,
                filename=original_filename,
                caption="Here's the extracted test information in HTML format."
            )
        
        # Clean up temporary files
        try:
            os.unlink(file_path)
            os.unlink(output_filename)
        except Exception as e:
            logger.error(f"Error deleting temporary files: {e}")
        
        # Delete the processing message
        if processing_message:
            await processing_message.delete()
        
    except Exception as e:
        logger.error(f"Error processing HTML file: {e}")
        # Clean up temporary files in case of error
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.unlink(file_path)
            if 'output_filename' in locals() and os.path.exists(output_filename):
                os.unlink(output_filename)
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")
        
        # Delete the processing message if it exists
        if processing_message:
            await processing_message.delete()
        
        await update.message.reply_text("Sorry, I couldn't process the HTML file. Please make sure it's a valid HTML file with the expected structure.")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.FileExtension("html"), handle_html_file))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":

    main()
