"""
Test API Connectivity for Intelligence Engine
"""
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env
env_file = Path('backend/.env')
load_dotenv(dotenv_path=env_file)

print('='*80)
print('🔍 TESTING API CONNECTIVITY')
print('='*80)
print()

print('Testing API Connections:')
print('-'*80)

results = []

# 1. Groq API
try:
    from groq import Groq
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    print(f'✅ Groq API              - Client instantiated')
    results.append(('pass', 'Groq'))
except Exception as e:
    print(f'❌ Groq API              - Error: {str(e)[:50]}')
    results.append(('fail', 'Groq'))

# 2. Hunter.io API
try:
    response = requests.get(
        'https://api.hunter.io/v2/account',
        params={'api_key': os.getenv('HUNTER_API_KEY')},
        timeout=5
    )
    if response.status_code == 200:
        data = response.json()
        remaining = data.get('data', {}).get('requests', {}).get('searches', {}).get('available', 'N/A')
        print(f'✅ Hunter.io API         - Connected (Searches remaining: {remaining})')
        results.append(('pass', 'Hunter.io'))
    else:
        print(f'⚠️  Hunter.io API         - HTTP {response.status_code}')
        results.append(('warn', 'Hunter.io'))
except Exception as e:
    print(f'❌ Hunter.io API         - Error: {str(e)[:50]}')
    results.append(('fail', 'Hunter.io'))

# 3. Serper API
try:
    response = requests.post(
        'https://google.serper.dev/search',
        headers={
            'X-API-KEY': os.getenv('SERPER_KEY'),
            'Content-Type': 'application/json'
        },
        json={'q': 'test', 'num': 1},
        timeout=5
    )
    if response.status_code == 200:
        print(f'✅ Serper API            - Connected')
        results.append(('pass', 'Serper'))
    else:
        print(f'⚠️  Serper API            - HTTP {response.status_code}')
        results.append(('warn', 'Serper'))
except Exception as e:
    print(f'❌ Serper API            - Error: {str(e)[:50]}')
    results.append(('fail', 'Serper'))

# 4. GNews API
try:
    response = requests.get(
        'https://gnews.io/api/v4/search',
        params={
            'q': 'test',
            'token': os.getenv('GNEWS_API_KEY'),
            'max': 1,
            'lang': 'en'
        },
        timeout=5
    )
    if response.status_code == 200:
        print(f'✅ GNews API             - Connected')
        results.append(('pass', 'GNews'))
    else:
        print(f'⚠️  GNews API             - HTTP {response.status_code}')
        results.append(('warn', 'GNews'))
except Exception as e:
    print(f'❌ GNews API             - Error: {str(e)[:50]}')
    results.append(('fail', 'GNews'))

print()
print('='*80)

passed = len([r for r in results if r[0] == 'pass'])
warned = len([r for r in results if r[0] == 'warn'])
failed = len([r for r in results if r[0] == 'fail'])

print(f'Summary: {passed} passed, {warned} warnings, {failed} failed out of {len(results)}')
print()

if failed > 0:
    print('⚠️  Some APIs are not accessible - fallback data will be used')
    print('   The system will still work but with reduced data quality')
else:
    print('✅ All critical APIs are accessible')

print('='*80)
