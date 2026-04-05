import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment
load_dotenv()

# Setup Client
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def process_task(file_path):
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=f'As a Digital FTE, draft a professional reply for this: \n\n {content}'
        )
        
        vault_base = os.getenv('VAULT_PATH', './Vault')
        pending_dir = Path(vault_base) / 'Pending_Approval'
        pending_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = pending_dir / f'DRAFT_{Path(file_path).name}'
        output_file.write_text(response.text, encoding='utf-8')
        print(f'✅ Success! Draft created: {output_file}')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_path = Path('./Vault/Needs_Action/test_task.md')
    if test_path.exists():
        process_task(test_path)
    else:
        print('Waiting for Vault/Needs_Action/test_task.md...')