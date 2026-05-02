from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
import requests
from datetime import datetime
import yfinance as yf
from ...intelligence.competitor_mapper import CompetitorMapper
from ...intelligence.company_profiler import CompanyProfiler
from ...core.cache import cache_manager

router = APIRouter(prefix="/comparison", tags=["comparison"])

# Initialize intelligence modules
competitor_mapper = CompetitorMapper()
company_profiler = CompanyProfiler()

@router.get("/competitors/{company_name}")
async def get_competitors(
    company_name: str,
    category: Optional[str] = Query(None, description="Industry category (e.g., tech, automotive, finance)")
):
    """Get competitors for a company with detailed analysis"""
    try:
        # Check cache first
        cache_key = f"competitors_{company_name}_{category or 'general'}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        # Auto-detect category if not provided
        if not category:
            category = await _detect_company_category(company_name)
        
        # Get competitors using intelligence engine
        competitors = competitor_mapper.discover_competitors(
            company_name=company_name,
            category=category,
            max_results=6
        )
        
        # Analyze competitor strengths/weaknesses
        competitors = competitor_mapper.analyze_competitor_strengths(competitors)
        
        # Get market data for each competitor (if they have stock symbols)
        enriched_competitors = []
        for comp in competitors:
            competitor_data = {
                "name": comp.name,
                "domain": comp.domain,
                "relevance_score": comp.relevance_score,
                "strengths": comp.strengths,
                "weaknesses": comp.weaknesses,
                "market_data": None,
                "stock_symbol": None
            }
            
            # Try to find stock symbol and get market data
            stock_symbol = await _find_stock_symbol(comp.name)
            if stock_symbol:
                competitor_data["stock_symbol"] = stock_symbol
                try:
                    market_data = await _get_market_data_for_competitor(stock_symbol)
                    competitor_data["market_data"] = market_data
                except:
                    pass
            
            enriched_competitors.append(competitor_data)
        
        result = {
            "success": True,
            "data": {
                "company": company_name,
                "category": category,
                "competitors": enriched_competitors,
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        # Cache for 30 minutes
        cache_manager.set(cache_key, result, ttl=1800)
        
        return result
        
    except Exception as e:
        print(f"Error getting competitors for {company_name}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get competitors: {str(e)}")

@router.get("/analyze/{company_name}")
async def analyze_company_comprehensive(company_name: str):
    """Get comprehensive company analysis including profile, competitors, and market position"""
    try:
        # Check cache first
        cache_key = f"company_analysis_{company_name}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        # Get company profile
        profile = company_profiler.create_profile(company_name)
        
        # Get competitors
        competitors_response = await get_competitors(company_name, profile.industry)
        competitors_data = competitors_response.get("data", {}).get("competitors", [])
        
        # Get market data for the main company
        main_company_symbol = await _find_stock_symbol(company_name)
        main_company_market_data = None
        if main_company_symbol:
            try:
                main_company_market_data = await _get_market_data_for_competitor(main_company_symbol)
            except:
                pass
        
        # Calculate market position
        market_position = _calculate_market_position(
            main_company_market_data,
            [comp for comp in competitors_data if comp.get("market_data")]
        )
        
        result = {
            "success": True,
            "data": {
                "company": {
                    "name": company_name,
                    "profile": {
                        "industry": profile.industry,
                        "size": profile.size,
                        "description": profile.description,
                        "key_products": profile.key_products,
                        "target_market": profile.target_market,
                        "business_model": profile.business_model,
                        "competitive_advantages": profile.competitive_advantages
                    },
                    "stock_symbol": main_company_symbol,
                    "market_data": main_company_market_data
                },
                "competitors": competitors_data,
                "market_position": market_position,
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        # Cache for 1 hour
        cache_manager.set(cache_key, result, ttl=3600)
        
        return result
        
    except Exception as e:
        print(f"Error analyzing company {company_name}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze company: {str(e)}")

async def _detect_company_category(company_name: str) -> str:
    """Auto-detect company category using LLM"""
    try:
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            return "technology"  # Default fallback
        
        from groq import Groq
        client = Groq(api_key=groq_key)
        
        prompt = f"""What industry category does "{company_name}" belong to? 
        
Choose ONE from: technology, automotive, finance, healthcare, retail, energy, telecommunications, aerospace, manufacturing, media, real_estate, consumer_goods, pharmaceuticals, food_beverage, transportation

Respond with just the category name, nothing else."""
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        
        category = response.choices[0].message.content.strip().lower()
        return category if category else "technology"
        
    except Exception as e:
        print(f"Error detecting category: {e}")
        return "technology"

async def _find_stock_symbol(company_name: str) -> Optional[str]:
    """Find stock symbol for a company name"""
    try:
        # Common company name to symbol mappings
        symbol_map = {
            "apple": "AAPL",
            "microsoft": "MSFT", 
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "meta": "META",
            "facebook": "META",
            "nvidia": "NVDA",
            "netflix": "NFLX",
            "adobe": "ADBE",
            "salesforce": "CRM",
            "oracle": "ORCL",
            "intel": "INTC",
            "cisco": "CSCO",
            "ibm": "IBM",
            "walmart": "WMT",
            "jpmorgan": "JPM",
            "visa": "V",
            "mastercard": "MA",
            "johnson": "JNJ",
            "procter": "PG",
            "coca cola": "KO",
            "pepsi": "PEP",
            "disney": "DIS",
            "nike": "NKE",
            "mcdonald": "MCD",
            "boeing": "BA",
            "ford": "F",
            "general motors": "GM",
            "exxon": "XOM",
            "chevron": "CVX"
        }
        
        # Check direct mapping first
        company_lower = company_name.lower()
        for key, symbol in symbol_map.items():
            if key in company_lower:
                return symbol
        
        # Try yfinance search
        try:
            # Try the company name as a symbol first
            ticker = yf.Ticker(company_name.upper())
            info = ticker.info
            if info and info.get('symbol'):
                return info['symbol']
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"Error finding stock symbol for {company_name}: {e}")
        return None

async def _get_market_data_for_competitor(symbol: str) -> dict:
    """Get market data for a competitor's stock symbol"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if hist.empty:
            return None
        
        info = ticker.info
        current_price = hist['Close'].iloc[-1]
        
        return {
            "symbol": symbol,
            "price": float(current_price),
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', 0),
            "revenue": info.get('totalRevenue', 0),
            "employees": info.get('fullTimeEmployees', 0),
            "currency": info.get('currency', 'USD')
        }
        
    except Exception as e:
        print(f"Error getting market data for {symbol}: {e}")
        return None

def _calculate_market_position(main_company_data: dict, competitors_with_data: list) -> dict:
    """Calculate market position relative to competitors"""
    try:
        if not main_company_data or not competitors_with_data:
            return {
                "market_cap_rank": "Unknown",
                "relative_size": "Unknown",
                "competitive_strength": "Medium"
            }
        
        # Compare market caps
        main_market_cap = main_company_data.get('market_cap', 0)
        competitor_market_caps = [
            comp['market_data']['market_cap'] 
            for comp in competitors_with_data 
            if comp['market_data'].get('market_cap', 0) > 0
        ]
        
        if not competitor_market_caps:
            return {
                "market_cap_rank": "Unknown",
                "relative_size": "Unknown", 
                "competitive_strength": "Medium"
            }
        
        # Calculate rank
        all_market_caps = [main_market_cap] + competitor_market_caps
        all_market_caps.sort(reverse=True)
        rank = all_market_caps.index(main_market_cap) + 1
        
        # Determine relative size
        avg_competitor_cap = sum(competitor_market_caps) / len(competitor_market_caps)
        if main_market_cap > avg_competitor_cap * 1.5:
            relative_size = "Larger than average"
        elif main_market_cap < avg_competitor_cap * 0.5:
            relative_size = "Smaller than average"
        else:
            relative_size = "Similar to average"
        
        # Determine competitive strength
        if rank <= 2:
            strength = "Strong"
        elif rank <= len(all_market_caps) // 2:
            strength = "Medium"
        else:
            strength = "Emerging"
        
        return {
            "market_cap_rank": f"#{rank} of {len(all_market_caps)}",
            "relative_size": relative_size,
            "competitive_strength": strength
        }
        
    except Exception as e:
        print(f"Error calculating market position: {e}")
        return {
            "market_cap_rank": "Unknown",
            "relative_size": "Unknown",
            "competitive_strength": "Medium"
        }