"""Quick smoke test for the intelligence layer – no API keys needed."""
import sys, asyncio
sys.path.insert(0, '.')

from app.intelligence.scorer import compute_opportunity_score, score_breakdown
from app.intelligence.llm_client import LLMClient

def test_scorer():
    news = [{'title': 'Nike launches campaign'}, {'title': 'Nike faces lawsuit'}]
    events = [{'source_url': 'x'}]
    competitors = [{'name': 'Adidas', 'recent_activity': ['launch']}]
    contacts = [{'name': 'Jane Smith', 'email_guesses': ['j@nike.com'], 'linkedin_url': 'https://li.com'}]

    score = compute_opportunity_score(news, events, competitors, contacts)
    bd = score_breakdown(news, events, competitors, contacts)
    assert 0 <= score <= 100, f"Score out of range: {score}"
    assert 'base' in bd
    print(f"Scorer OK – score={score} breakdown={bd}")

async def test_mock_llm():
    client = LLMClient.__new__(LLMClient)
    client._backend = 'mock'
    cases = [
        ('generate company overview about text', True),
        ('identify strategic watchout risk', True),
        ('write linkedin message', True),
        ('write email draft', True),
        # competitor mock returns a JSON placeholder, not the [LLM not configured] tag
        ('analyze competitor gap', False),
    ]
    for prompt, should_have_tag in cases:
        result = client._mock(prompt)
        has_tag = '[LLM not configured]' in result
        status = 'OK' if has_tag == should_have_tag else 'FAIL'
        print(f"  [{status}] mock prompt='{prompt[:35]}' -> tag_present={has_tag}")
        assert has_tag == should_have_tag

if __name__ == '__main__':
    test_scorer()
    asyncio.run(test_mock_llm())
    print("All intelligence smoke tests passed.")
