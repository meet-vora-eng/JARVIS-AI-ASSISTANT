import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import urllib.parse
import urllib.request
from urllib.parse import urlparse, parse_qs
import subprocess
import threading
import time
import shutil
import tempfile
import json
import re
import html
from pathlib import Path

from ddgs import DDGS


# =========================================================
# INITIALIZATION
# =========================================================

recognizer = sr.Recognizer()
engine = pyttsx3.init()

MODEL = "qwen3:1.7b"


# =========================================================
# VOICE
# =========================================================

def speak(text):

    if not text:
        return

    print("Jarvis:", text)

    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print("Voice Error:", e)


# =========================================================
# AI BRAIN
# =========================================================

def ask_ai(command):

    prompt = f"""
You are Jarvis, a smart personal computer assistant.

The user can speak English, Hindi, or Hinglish.

Understand the user's REAL meaning.

Return ONLY valid JSON in this format:

{{
    "action": "ACTION",
    "query": "VALUE"
}}

Allowed actions:

OPEN_WEBSITE
SEARCH_WEB
LIVE_SEARCH
PLAY_YOUTUBE
OPEN_APP
CHAT
STOP


RULES:

1. If the user asks a normal question or asks you to explain
something, use CHAT.

2. If the user asks about CURRENT or LATEST information,
use LIVE_SEARCH.

Examples:
- latest news
- today's news
- trading news
- stock market
- Nifty
- Sensex
- today's market
- latest technology news
- latest sports news
- current events

3. If the user wants to play ANY song,
use PLAY_YOUTUBE.

4. If the user wants to open a website,
use OPEN_WEBSITE.

5. If the user wants to search Google,
use SEARCH_WEB.

6. If the user wants to open an application,
use OPEN_APP.

7. If the user says stop, exit or quit,
use STOP.

8. Understand Hindi, English and Hinglish.

9. Ignore the word "Jarvis".

10. For PLAY_YOUTUBE, return the complete song query.

11. For LIVE_SEARCH, return a clear search query.


EXAMPLES:

User:
"Please tell me what Python is"

Answer:
{{"action":"CHAT","query":"Explain Python simply."}}


User:
"Python kya hai mujhe bata"

Answer:
{{"action":"CHAT","query":"Explain Python in simple Hinglish."}}


User:
"Mujhe AI samjha"

Answer:
{{"action":"CHAT","query":"Explain artificial intelligence in simple Hinglish."}}


User:
"Aaj ki trading news bata"

Answer:
{{"action":"LIVE_SEARCH","query":"latest Indian stock market trading news today"}}


User:
"Nifty ki latest news kya hai"

Answer:
{{"action":"LIVE_SEARCH","query":"Nifty latest news India today"}}


User:
"Market mein aaj kya scene hai"

Answer:
{{"action":"LIVE_SEARCH","query":"Indian stock market latest news today"}}


User:
"Latest AI news bata"

Answer:
{{"action":"LIVE_SEARCH","query":"latest artificial intelligence news today"}}


User:
"Krishna Krishna ka koi song baja"

Answer:
{{"action":"PLAY_YOUTUBE","query":"Krishna Krishna song"}}


User:
"Arijit Singh ka Husn baja"

Answer:
{{"action":"PLAY_YOUTUBE","query":"Arijit Singh Husn"}}


User:
"YouTube kholo"

Answer:
{{"action":"OPEN_WEBSITE","query":"youtube"}}


User:
"Google open kar"

Answer:
{{"action":"OPEN_WEBSITE","query":"google"}}


User:
"Chrome kholo"

Answer:
{{"action":"OPEN_APP","query":"chrome"}}


User:
"Notepad khol"

Answer:
{{"action":"OPEN_APP","query":"notepad"}}


User:
"Google pe Python course search kar"

Answer:
{{"action":"SEARCH_WEB","query":"Python course"}}


User:
"Stop Jarvis"

Answer:
{{"action":"STOP","query":""}}


Return ONLY JSON.
Do not use markdown.
Do not explain the JSON.

User command:
{command}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# =========================================================
# EXTRACT JSON
# =========================================================

def extract_json(text):

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    match = re.search(
        r'\{.*\}',
        text,
        re.DOTALL
    )

    if match:
        return json.loads(match.group(0))

    raise ValueError("AI returned invalid JSON")


# =========================================================
# OPEN WEBSITE
# =========================================================

def open_website(query):

    websites = {

        "google": "https://www.google.com",

        "youtube": "https://www.youtube.com",

        "facebook": "https://www.facebook.com",

        "instagram": "https://www.instagram.com",

        "linkedin": "https://www.linkedin.com",

        "github": "https://github.com",

        "chatgpt": "https://chatgpt.com"
    }

    query = query.lower().strip()

    if query in websites:

        speak(f"Opening {query}")

        webbrowser.open(
            websites[query]
        )

    else:

        speak(f"Searching for {query}")

        webbrowser.open(
            "https://www.google.com/search?q="
            + urllib.parse.quote(query)
        )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def search_web(query):

    speak(
        f"Searching for {query}"
    )

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url, new=0)


# =========================================================
# YOUTUBE
# =========================================================

def play_youtube(query):

    speak(
        f"Searching YouTube for {query}"
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url)


# =========================================================
# OPEN WINDOWS APP
# =========================================================

def open_app(app):

    app = app.lower().strip()


    if app == "chrome":

        speak("Opening Chrome")

        subprocess.Popen(
            "start chrome",
            shell=True
        )

        return


    if app == "edge":

        speak("Opening Microsoft Edge")

        subprocess.Popen(
            "start msedge",
            shell=True
        )

        return


    if app == "notepad":

        speak("Opening Notepad")

        subprocess.Popen(
            "notepad.exe"
        )

        return


    if app in ["calculator", "calc"]:

        speak("Opening Calculator")

        subprocess.Popen(
            "calc.exe"
        )

        return


    if app == "paint":

        speak("Opening Paint")

        subprocess.Popen(
            "mspaint.exe"
        )

        return


    speak(
        f"I don't know how to open {app} yet."
    )

# =========================================================
# SMART LIVE SEARCH
# VIDEO + CHART + DETAILED ARTICLE + VOICE
# =========================================================

def smart_search(query, max_results=8):
    try:
        return list(
            DDGS().text(
                query,
                max_results=max_results
            )
        )
    except Exception as e:
        print("Search error:", e)
        return []


def get_url(result):
    """Return a URL from common DDGS/search result shapes."""
    if not result:
        return ""

    value = (
        result.get("href")
        or result.get("url")
        or result.get("content")
        or result.get("link")
        or ""
    )

    if isinstance(value, str):
        match = re.search(r"https?://[^\s)]+", value)
        if match:
            return match.group(0).rstrip(".,")
        return value.strip()

    return ""


def get_domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def find_domain_result(results, domains):
    generic_titles = {
        "home - youtube",
        "youtube",
        "markets today — quotes, charts, and events — tradingview",
        "markets today - quotes, charts, and events - tradingview",
        "tradingview",
    }

    for result in results:
        domain = get_domain(get_url(result))
        title = result.get("title", "").strip().lower()

        if any(d in domain for d in domains):
            if title in generic_titles:
                continue
            return result

    return None


def youtube_embed_url(url):
    """Convert a YouTube watch/short URL into an embeddable URL."""
    try:
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)

        if "youtube.com" in parsed.netloc:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?autoplay=1"

        if "youtu.be" in parsed.netloc:
            video_id = parsed.path.strip("/")
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?autoplay=1"

    except Exception:
        pass

    return ""


def tradingview_symbol(query, chart_url=""):
    """Pick a useful TradingView symbol for common Indian instruments."""
    q = query.lower()

    # Common index mappings.
    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"

    if "nifty" in q and "midcap" not in q:
        return "NSE:NIFTY1!"

    if "sensex" in q:
        return "BSE:SENSEX"

    # Try to extract a TradingView NSE/BSE symbol from the result URL.
    match = re.search(
        r"/symbols/(?:NSE|BSE)-([A-Z0-9_-]+)",
        chart_url,
        re.IGNORECASE
    )

    if match:
        exchange = "NSE" if "/symbols/NSE-" in chart_url.upper() else "BSE"
        symbol = match.group(1).replace("-", "")
        return f"{exchange}:{symbol}"

    return "NSE:NIFTY1!"


def extract_youtube_video_id(url):
    """Extract a YouTube watch/short URL video ID."""
    if not url:
        return None

    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if "youtu.be" in host:
            video_id = parsed.path.strip("/").split("/")[0]
            return video_id or None

        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
                return parts[1]

    except Exception:
        pass

    return None



def get_market_data_symbol(query):
    """Map the user's common Indian-market wording to Yahoo Finance symbols."""
    q = (query or "").lower()

    if "bank nifty" in q or "banknifty" in q:
        return "^NSEBANK", "NIFTY BANK"

    if "sensex" in q:
        return "^BSESN", "SENSEX"

    if "reliance" in q:
        return "RELIANCE.NS", "RELIANCE"

    if "tcs" in q:
        return "TCS.NS", "TCS"

    if "infosys" in q or "infy" in q:
        return "INFY.NS", "INFOSYS"

    if "hdfc" in q:
        return "HDFCBANK.NS", "HDFC BANK"

    if "icici" in q:
        return "ICICIBANK.NS", "ICICI BANK"

    return "^NSEI", "NIFTY 50"


def fetch_yahoo_chart_data(query, interval="5m", range_="1d"):
    """
    Fetch OHLCV data from Yahoo Finance's chart endpoint using stdlib only.
    No API key or extra pip package is required.
    """
    symbol, display_name = get_market_data_symbol(query)

    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        + urllib.parse.quote(symbol, safe="")
        + "?"
        + urllib.parse.urlencode({
            "interval": interval,
            "range": range_,
            "includePrePost": "false",
            "events": "div,splits"
        })
    )

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/142 Safari/537.36"
                )
            }
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))

        result = payload.get("chart", {}).get("result") or []
        if not result:
            raise RuntimeError("Yahoo Finance returned no chart data.")

        result = result[0]
        timestamps = result.get("timestamp") or []
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]

        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        volumes = quote.get("volume") or []

        candles = []
        volume = []

        for i, ts in enumerate(timestamps):
            try:
                o = opens[i]
                h = highs[i]
                l = lows[i]
                c = closes[i]
                v = volumes[i] if i < len(volumes) else None

                if None in (o, h, l, c):
                    continue

                candles.append({
                    "x": int(ts) * 1000,
                    "y": [
                        float(o),
                        float(h),
                        float(l),
                        float(c)
                    ]
                })

                volume.append({
                    "x": int(ts) * 1000,
                    "y": float(v or 0)
                })
            except (IndexError, TypeError, ValueError):
                continue

        if len(candles) < 5:
            raise RuntimeError("Not enough market bars returned.")

        return {
            "ok": True,
            "symbol": symbol,
            "name": display_name,
            "candles": candles[-400:],
            "volume": volume[-400:],
            "source": "Yahoo Finance"
        }

    except Exception as exc:
        return {
            "ok": False,
            "symbol": symbol,
            "name": display_name,
            "candles": [],
            "volume": [],
            "source": "Yahoo Finance",
            "error": str(exc)
        }


def get_chart_symbol(query):
    """
    Pick a useful TradingView symbol for common Indian-market requests.
    Falls back to NSE:NIFTY1! (NIFTY continuous futures) for generic Indian trading requests.
    """
    q = query.lower()

    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"

    if "sensex" in q:
        return "BSE:SENSEX"

    if "reliance" in q:
        return "NSE:RELIANCE"

    if "tcs" in q:
        return "NSE:TCS"

    if "infosys" in q or "infy" in q:
        return "NSE:INFY"

    if "hdfc" in q:
        return "NSE:HDFCBANK"

    if "icici" in q:
        return "NSE:ICICIBANK"

    # Default: use the embeddable NSE continuous NIFTY futures symbol.
    return "NSE:NIFTY1!"


def extract_youtube_video_id(url):
    """Extract a YouTube watch/short URL video ID."""
    if not url:
        return None

    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if "youtu.be" in host:
            return parsed.path.strip("/").split("/")[0] or None

        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
                return parts[1]

    except Exception:
        pass

    return None


def get_chart_symbol(query):
    q = query.lower()

    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"

    if "sensex" in q:
        return "BSE:SENSEX"

    if "reliance" in q:
        return "NSE:RELIANCE"

    if "tcs" in q:
        return "NSE:TCS"

    if "infosys" in q or "infy" in q:
        return "NSE:INFY"

    if "hdfc" in q:
        return "NSE:HDFCBANK"

    if "icici" in q:
        return "NSE:ICICIBANK"

    return "NSE:NIFTY1!"

import speech_recognition as sr
import pyttsx3
import ollama
import webbrowser
import urllib.parse
from urllib.parse import urlparse, parse_qs
import subprocess
import threading
import time
import shutil
import tempfile
import json
import re
import html
from pathlib import Path

from ddgs import DDGS


# =========================================================
# INITIALIZATION
# =========================================================

recognizer = sr.Recognizer()
engine = pyttsx3.init()

MODEL = "qwen3:1.7b"


# =========================================================
# VOICE
# =========================================================

def speak(text):

    if not text:
        return

    print("Jarvis:", text)

    try:
        engine.stop()
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print("Voice Error:", e)


# =========================================================
# AI BRAIN
# =========================================================

def ask_ai(command):

    prompt = f"""
You are Jarvis, a smart personal computer assistant.

The user can speak English, Hindi, or Hinglish.

Understand the user's REAL meaning.

Return ONLY valid JSON in this format:

{{
    "action": "ACTION",
    "query": "VALUE"
}}

Allowed actions:

OPEN_WEBSITE
SEARCH_WEB
LIVE_SEARCH
PLAY_YOUTUBE
OPEN_APP
CHAT
STOP


RULES:

1. If the user asks a normal question or asks you to explain
something, use CHAT.

2. If the user asks about CURRENT or LATEST information,
use LIVE_SEARCH.

Examples:
- latest news
- today's news
- trading news
- stock market
- Nifty
- Sensex
- today's market
- latest technology news
- latest sports news
- current events

3. If the user wants to play ANY song,
use PLAY_YOUTUBE.

4. If the user wants to open a website,
use OPEN_WEBSITE.

5. If the user wants to search Google,
use SEARCH_WEB.

6. If the user wants to open an application,
use OPEN_APP.

7. If the user says stop, exit or quit,
use STOP.

8. Understand Hindi, English and Hinglish.

9. Ignore the word "Jarvis".

10. For PLAY_YOUTUBE, return the complete song query.

11. For LIVE_SEARCH, return a clear search query.


EXAMPLES:

User:
"Please tell me what Python is"

Answer:
{{"action":"CHAT","query":"Explain Python simply."}}


User:
"Python kya hai mujhe bata"

Answer:
{{"action":"CHAT","query":"Explain Python in simple Hinglish."}}


User:
"Mujhe AI samjha"

Answer:
{{"action":"CHAT","query":"Explain artificial intelligence in simple Hinglish."}}


User:
"Aaj ki trading news bata"

Answer:
{{"action":"LIVE_SEARCH","query":"latest Indian stock market trading news today"}}


User:
"Nifty ki latest news kya hai"

Answer:
{{"action":"LIVE_SEARCH","query":"Nifty latest news India today"}}


User:
"Market mein aaj kya scene hai"

Answer:
{{"action":"LIVE_SEARCH","query":"Indian stock market latest news today"}}


User:
"Latest AI news bata"

Answer:
{{"action":"LIVE_SEARCH","query":"latest artificial intelligence news today"}}


User:
"Krishna Krishna ka koi song baja"

Answer:
{{"action":"PLAY_YOUTUBE","query":"Krishna Krishna song"}}


User:
"Arijit Singh ka Husn baja"

Answer:
{{"action":"PLAY_YOUTUBE","query":"Arijit Singh Husn"}}


User:
"YouTube kholo"

Answer:
{{"action":"OPEN_WEBSITE","query":"youtube"}}


User:
"Google open kar"

Answer:
{{"action":"OPEN_WEBSITE","query":"google"}}


User:
"Chrome kholo"

Answer:
{{"action":"OPEN_APP","query":"chrome"}}


User:
"Notepad khol"

Answer:
{{"action":"OPEN_APP","query":"notepad"}}


User:
"Google pe Python course search kar"

Answer:
{{"action":"SEARCH_WEB","query":"Python course"}}


User:
"Stop Jarvis"

Answer:
{{"action":"STOP","query":""}}


Return ONLY JSON.
Do not use markdown.
Do not explain the JSON.

User command:
{command}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# =========================================================
# EXTRACT JSON
# =========================================================

def extract_json(text):

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    match = re.search(
        r'\{.*\}',
        text,
        re.DOTALL
    )

    if match:
        return json.loads(match.group(0))

    raise ValueError("AI returned invalid JSON")


# =========================================================
# OPEN WEBSITE
# =========================================================

def open_website(query):

    websites = {

        "google": "https://www.google.com",

        "youtube": "https://www.youtube.com",

        "facebook": "https://www.facebook.com",

        "instagram": "https://www.instagram.com",

        "linkedin": "https://www.linkedin.com",

        "github": "https://github.com",

        "chatgpt": "https://chatgpt.com"
    }

    query = query.lower().strip()

    if query in websites:

        speak(f"Opening {query}")

        webbrowser.open(
            websites[query]
        )

    else:

        speak(f"Searching for {query}")

        webbrowser.open(
            "https://www.google.com/search?q="
            + urllib.parse.quote(query)
        )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def search_web(query):

    speak(
        f"Searching for {query}"
    )

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url)


# =========================================================
# YOUTUBE
# =========================================================

def play_youtube(query):

    speak(
        f"Searching YouTube for {query}"
    )

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )

    webbrowser.open(url)


# =========================================================
# OPEN WINDOWS APP
# =========================================================

def open_app(app):

    app = app.lower().strip()


    if app == "chrome":

        speak("Opening Chrome")

        subprocess.Popen(
            "start chrome",
            shell=True
        )

        return


    if app == "edge":

        speak("Opening Microsoft Edge")

        subprocess.Popen(
            "start msedge",
            shell=True
        )

        return


    if app == "notepad":

        speak("Opening Notepad")

        subprocess.Popen(
            "notepad.exe"
        )

        return


    if app in ["calculator", "calc"]:

        speak("Opening Calculator")

        subprocess.Popen(
            "calc.exe"
        )

        return


    if app == "paint":

        speak("Opening Paint")

        subprocess.Popen(
            "mspaint.exe"
        )

        return


    speak(
        f"I don't know how to open {app} yet."
    )

# =========================================================
# SMART LIVE SEARCH
# VIDEO + CHART + DETAILED ARTICLE + VOICE
# =========================================================

def smart_search(query, max_results=8):
    try:
        return list(
            DDGS().text(
                query,
                max_results=max_results
            )
        )
    except Exception as e:
        print("Search error:", e)
        return []


def get_url(result):
    """Return a URL from common DDGS/search result shapes."""
    if not result:
        return ""

    value = (
        result.get("href")
        or result.get("url")
        or result.get("content")
        or result.get("link")
        or ""
    )

    if isinstance(value, str):
        match = re.search(r"https?://[^\s)]+", value)
        if match:
            return match.group(0).rstrip(".,")
        return value.strip()

    return ""


def get_domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def find_domain_result(results, domains):
    generic_titles = {
        "home - youtube",
        "youtube",
        "markets today — quotes, charts, and events — tradingview",
        "markets today - quotes, charts, and events - tradingview",
        "tradingview",
    }

    for result in results:
        domain = get_domain(get_url(result))
        title = result.get("title", "").strip().lower()

        if any(d in domain for d in domains):
            if title in generic_titles:
                continue
            return result

    return None


def youtube_embed_url(url):
    """Convert a YouTube watch/short URL into an embeddable URL."""
    try:
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)

        if "youtube.com" in parsed.netloc:
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?autoplay=1"

        if "youtu.be" in parsed.netloc:
            video_id = parsed.path.strip("/")
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?autoplay=1"

    except Exception:
        pass

    return ""


def tradingview_symbol(query, chart_url=""):
    """Pick a useful TradingView symbol for common Indian instruments."""
    q = query.lower()

    # Common index mappings.
    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"

    if "nifty" in q and "midcap" not in q:
        return "NSE:NIFTY1!"

    if "sensex" in q:
        return "BSE:SENSEX"

    # Try to extract a TradingView NSE/BSE symbol from the result URL.
    match = re.search(
        r"/symbols/(?:NSE|BSE)-([A-Z0-9_-]+)",
        chart_url,
        re.IGNORECASE
    )

    if match:
        exchange = "NSE" if "/symbols/NSE-" in chart_url.upper() else "BSE"
        symbol = match.group(1).replace("-", "")
        return f"{exchange}:{symbol}"

    return "NSE:NIFTY1!"


def extract_youtube_video_id(url):
    """Extract a YouTube watch/short URL video ID."""
    if not url:
        return None

    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if "youtu.be" in host:
            video_id = parsed.path.strip("/").split("/")[0]
            return video_id or None

        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
                return parts[1]

    except Exception:
        pass

    return None


def get_chart_symbol(query):
    """
    Pick a useful TradingView symbol for common Indian-market requests.
    Falls back to NSE:NIFTY1! (NIFTY continuous futures) for generic Indian trading requests.
    """
    q = query.lower()

    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"

    if "sensex" in q:
        return "BSE:SENSEX"

    if "reliance" in q:
        return "NSE:RELIANCE"

    if "tcs" in q:
        return "NSE:TCS"

    if "infosys" in q or "infy" in q:
        return "NSE:INFY"

    if "hdfc" in q:
        return "NSE:HDFCBANK"

    if "icici" in q:
        return "NSE:ICICIBANK"

    # Default: use the embeddable NSE continuous NIFTY futures symbol.
    return "NSE:NIFTY1!"


def extract_youtube_video_id(url):
    """Extract a YouTube watch/short URL video ID."""
    if not url:
        return None

    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()

        if "youtu.be" in host:
            return parsed.path.strip("/").split("/")[0] or None

        if "youtube.com" in host:
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
                return parts[1]

    except Exception:
        pass

    return None


def get_chart_symbol(query):
    q = query.lower()

    if "bank nifty" in q or "banknifty" in q:
        return "NSE:BANKNIFTY"
    if "sensex" in q:
        return "BSE:SENSEX"
    if "reliance" in q:
        return "NSE:RELIANCE"
    if "tcs" in q:
        return "NSE:TCS"
    if "infosys" in q or "infy" in q:
        return "NSE:INFY"
    if "hdfc" in q:
        return "NSE:HDFCBANK"
    if "icici" in q:
        return "NSE:ICICIBANK"

    return "NSE:NIFTY1!"


def find_direct_youtube_video(query):
    """
    Try to obtain a real YouTube watch URL for embedding.
    Uses yt-dlp if installed. Returns None if unavailable/fails.
    """
    try:
        if not shutil.which("yt-dlp"):
            return None

        search_query = (
            "ytsearch1:"
            + query
            + " latest news explanation"
        )

        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--print",
                "webpage_url",
                "--skip-download",
                search_query,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )

        for line in result.stdout.splitlines():
            line = line.strip()
            if "youtube.com/watch" in line or "youtu.be/" in line:
                return line

    except Exception as e:
        print("yt-dlp video lookup error:", e)

    return None




def download_video_for_local_playback(video_url):
    """
    Download a small, browser-friendly MP4 copy to the Jarvis Temp folder.

    This is intentionally used instead of YouTube's iframe player. That means
    government/region/embed restrictions shown by the YouTube iframe cannot
    break the Jarvis player. A local HTTP URL is then used by the dashboard.
    """
    if not video_url or not shutil.which("yt-dlp"):
        return None

    try:
        video_dir = (
            Path.home()
            / "AppData"
            / "Local"
            / "Temp"
            / "jarvis_video"
        )
        video_dir.mkdir(parents=True, exist_ok=True)

        output = video_dir / "latest_news.mp4"

        # Remove the previous video so the dashboard always plays the newly
        # selected story.
        try:
            if output.exists():
                output.unlink()
        except Exception:
            pass

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--retries", "2",
            "--fragment-retries", "2",
            "--socket-timeout", "12",
            "-f",
            "best[height<=480][ext=mp4]/best[height<=480]/best",
            "--merge-output-format", "mp4",
            "-o", str(output),
            video_url,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=45,
        )

        if result.returncode == 0 and output.exists() and output.stat().st_size > 100_000:
            return output

        print("Local video download failed:", result.stderr.strip()[-700:])
        return None

    except subprocess.TimeoutExpired:
        print("Local video download timed out.")
        return None
    except Exception as e:
        print("Local video download error:", e)
        return None


def get_direct_video_stream(video_url):
    """
    Resolve a selected YouTube watch URL to a browser-playable direct media URL.

    This avoids relying on YouTube's iframe/embed player. The CDN URL is
    time-limited, so it is resolved when the dashboard is generated.
    """
    if not video_url or not shutil.which("yt-dlp"):
        return None

    try:
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--get-url",
            "-f",
            "best[ext=mp4][vcodec!=none][acodec!=none]/"
            "best[vcodec!=none][acodec!=none]/"
            "best",
            video_url,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=18,
        )

        if result.returncode != 0:
            print("Direct video stream error:", result.stderr.strip()[-400:])
            return None

        urls = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip().startswith(("http://", "https://"))
        ]

        return urls[0] if urls else None

    except Exception as e:
        print("Direct video stream lookup error:", e)
        return None



def find_youtube_results(query, max_results=6):
    """Return several real YouTube watch results for the in-page picker."""
    results_out = []
    seen = set()

    def add_result(result):
        if not result:
            return
        url = get_url(result)
        vid = extract_youtube_video_id(url)
        if not vid or vid in seen:
            return
        seen.add(vid)
        results_out.append({
            "title": result.get("title", "YouTube video"),
            "href": url,
            "body": (
                result.get("description")
                or result.get("body")
                or result.get("snippet")
                or ""
            )
        })

    try:
        results = list(
            DDGS().videos(
                query + " latest news",
                max_results=max_results
            )
        )
        for result in results:
            add_result(result)
    except Exception as e:
        print("YouTube picker search error:", e)

    if len(results_out) < max_results:
        try:
            results = smart_search(
                f"site:youtube.com/watch {query} latest news video",
                max_results=max_results * 2
            )
            for result in results:
                add_result(result)
                if len(results_out) >= max_results:
                    break
        except Exception as e:
            print("YouTube picker text-search error:", e)

    return results_out[:max_results]


def find_video_result(query):
    """
    Find a real YouTube watch URL.

    DDGS video search sometimes returns the generic YouTube homepage.  We
    therefore validate the URL and then use a normal web search for explicit
    youtube.com/watch URLs before falling back to yt-dlp.
    """
    try:
        results = list(
            DDGS().videos(
                query + " latest news explanation",
                max_results=12
            )
        )

        for result in results:
            url = get_url(result)
            if extract_youtube_video_id(url):
                return {
                    "title": result.get("title", "YouTube news video"),
                    "href": url,
                    "body": result.get(
                        "description",
                        result.get("body", "")
                    )
                }
    except Exception as e:
        print("DDGS video search error:", e)

    # Text search is often more reliable than the video endpoint for
    # obtaining an actual YouTube watch URL.
    try:
        results = smart_search(
            f"site:youtube.com/watch {query} latest news explanation",
            max_results=12
        )

        for result in results:
            url = get_url(result)
            if extract_youtube_video_id(url):
                return {
                    "title": result.get("title", "YouTube news video"),
                    "href": url,
                    "body": (
                        result.get("body")
                        or result.get("description")
                        or ""
                    )
                }
    except Exception as e:
        print("YouTube text-search fallback error:", e)

    # Last fallback: yt-dlp. Install with:
    # python -m pip install yt-dlp
    try:
        direct = find_direct_youtube_video(query)
        if direct:
            return {
                "title": "YouTube news video",
                "href": direct,
                "body": ""
            }
    except Exception as e:
        print("yt-dlp fallback error:", e)

    return None



def create_research_dashboard(query, video, chart, article, summary='', news_results=None, video_results=None):
    """
    Interactive Jarvis Research Hub.

    - Scrollable page.
    - YouTube video plays INSIDE the page when embedding is allowed.
    - TradingView Advanced Chart widget is interactive INSIDE the page when the selected symbol is supported.
    - Right side contains the full Jarvis summary plus individual important
      news cards so the user can read each development, not just one paragraph.
    """

    dashboard_path = (
        Path.home()
        / "AppData"
        / "Local"
        / "Temp"
        / "jarvis_research_hub.html"
    )

    dashboard_data_path = (
        Path.home()
        / "AppData"
        / "Local"
        / "Temp"
        / "jarvis_research_data.json"
    )

    chart_symbol = get_chart_symbol(query)
    market_data = fetch_yahoo_chart_data(query)
    market_data_json = json.dumps(market_data, ensure_ascii=False)


    # -------------------------
    # Video picker
    # -------------------------
    # The topic is already searched by Jarvis. The user only selects a video.
    # The selected video is embedded into this SAME dashboard area.
    picker_results = video_results or []
    if video and not any(
        extract_youtube_video_id(get_url(v)) ==
        extract_youtube_video_id(get_url(video))
        for v in picker_results
    ):
        picker_results.insert(0, video)

    picker_results = picker_results[:6]

    video_items_html = ""
    for idx, item in enumerate(picker_results):
        vid = extract_youtube_video_id(get_url(item))
        if not vid:
            continue

        title = html.escape(
            item.get("title", "YouTube news video")
        )
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

        video_items_html += f"""
        <button class="yt-result"
                type="button"
                data-video-id="{html.escape(vid)}">
            <img src="{thumb}"
                 alt=""
                 loading="lazy">
            <span class="yt-result-title">{title}</span>
            <span class="yt-play">▶</span>
        </button>
        """

    if not video_items_html:
        video_items_html = """
        <div class="yt-empty">
            Jarvis could not find YouTube videos for this topic.
        </div>
        """

    initial_vid = extract_youtube_video_id(get_url(video)) if video else ""

    if initial_vid:
        initial_player = f"""
        <div class="yt-player-wrap">
            <iframe
                id="jarvisYoutubePlayer"
                src="https://www.youtube.com/embed/{html.escape(initial_vid)}?rel=0&playsinline=1"
                title="Jarvis selected news video"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen>
            </iframe>
        </div>
        """
    else:
        initial_player = """
        <div class="yt-player-wrap yt-player-empty"
             id="jarvisYoutubePlayerBox">
            <div>🎬 Select a video below</div>
        </div>
        """

    video_embed = f"""
    <div class="youtube-picker">
        <div class="yt-player" id="jarvisYoutubePlayerArea">
            {initial_player}
        </div>

        <div class="yt-selected-title" id="jarvisYoutubeSelectedTitle">
            {html.escape(video.get("title", "Select a video") if video else "Select a video")}
        </div>

        <div class="yt-results-label">
            YouTube results for: <strong>{html.escape(query)}</strong>
        </div>

        <div class="yt-results" id="jarvisYoutubeResults">
            {video_items_html}
        </div>
    </div>

    <script>
    (function () {{
        const results = document.querySelectorAll(".yt-result");
        const playerArea = document.getElementById("jarvisYoutubePlayerArea");
        const selectedTitle = document.getElementById("jarvisYoutubeSelectedTitle");

        results.forEach(function (button) {{
            button.addEventListener("click", function () {{
                const id = button.dataset.videoId;
                const titleNode = button.querySelector(".yt-result-title");
                const title = titleNode ? titleNode.textContent : "Selected video";

                if (!id || !playerArea) return;

                playerArea.innerHTML =
                    '<div class="yt-player-wrap">' +
                    '<iframe id="jarvisYoutubePlayer" ' +
                    'src="https://www.youtube.com/embed/' +
                    encodeURIComponent(id) +
                    '?autoplay=1&rel=0&playsinline=1" ' +
                    'title="Jarvis selected news video" ' +
                    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" ' +
                    'allowfullscreen></iframe></div>';

                if (selectedTitle) selectedTitle.textContent = title;

                results.forEach(function (other) {{
                    other.classList.remove("selected");
                }});
                button.classList.add("selected");
            }});
        }});
    }})();
    </script>
    """

    # -------------------------
    # News cards
    # -------------------------
    clean_news = []
    seen_urls = set()

    for item in (news_results or []):
        if not item:
            continue

        title = (item.get("title") or "").strip()
        body = (
            item.get("body")
            or item.get("description")
            or item.get("snippet")
            or ""
        ).strip()
        url = get_url(item)

        if not title or not body:
            continue

        key = url or title.lower()
        if key in seen_urls:
            continue

        seen_urls.add(key)
        clean_news.append((title, body, url))

        if len(clean_news) >= 8:
            break

    news_cards = ""

    for idx, (title, body, url) in enumerate(clean_news, start=1):
        source_host = get_domain(url) if url else "Search source"
        link = f"""
        <div class="source-inline">
            Source: {html.escape(source_host)}
        </div>
        """

        news_cards += f"""
        <article class="news-card">
            <div class="news-number">{idx}</div>
            <div class="news-content">
                <h3>{html.escape(title)}</h3>
                <p>{html.escape(body)}</p>
                {link}
            </div>
        </article>
        """

    if not news_cards:
        news_cards = """
        <div class="empty-news">
            No individual news snippets were available.
        </div>
        """

    # -------------------------
    # Summary
    # -------------------------
    display_summary = (
        summary.strip()
        if summary and summary.strip()
        else "No detailed Jarvis summary was generated."
    )

    article_title = (
        article.get("title", "Primary source")
        if article else "Primary source"
    )
    article_url = get_url(article) if article else ""

    article_link = ""
    if article_url:
        article_link = f"""
        <a class="news-link"
           href="{html.escape(article_url)}"
           target="_self">
           Open primary source ↗
        </a>
        """

    safe_query = html.escape(query)
    safe_summary = html.escape(display_summary)
    safe_chart_symbol = html.escape(chart_symbol)
    safe_video_title = html.escape(video.get("title", "Important news video") if video else "Important news video")

    tradingview_symbol_json = json.dumps(chart_symbol)

    live_poll_script = '\n<script>\n(function () {\n    function esc(value) {\n        return String(value == null ? "" : value)\n            .replace(/&/g, "&amp;")\n            .replace(/</g, "&lt;")\n            .replace(/>/g, "&gt;")\n            .replace(/"/g, "&quot;")\n            .replace(/\'/g, "&#039;");\n    }\n\n    function renderNews(items) {\n        if (!Array.isArray(items) || items.length === 0) {\n            return \'<div class="empty-news">No individual news snippets were available.</div>\';\n        }\n\n        return items.map(function(item, index) {\n            var title = esc(item.title || "Untitled story");\n            var body = esc(item.body || "");\n            var url = item.url || "";\n\n            var link = url\n                ? \'<a class="news-link" href="\' + esc(url) + \'" target="_self">Read full story ↗</a>\'\n                : "";\n\n            return \'<article class="news-card">\' +\n                \'<div class="news-number">\' + (index + 1) + \'</div>\' +\n                \'<div class="news-content">\' +\n                \'<h3>\' + title + \'</h3>\' +\n                \'<p>\' + body + \'</p>\' +\n                link +\n                \'</div></article>\';\n        }).join("");\n    }\n\n    async function refreshJarvisData() {\n        try {\n            var response = await fetch(\n                "/jarvis_research_data.json?t=" + Date.now(),\n                { cache: "no-store" }\n            );\n\n            if (!response.ok) return;\n\n            var data = await response.json();\n\n            if (data.summary !== undefined) {\n                document.getElementById("summaryText").textContent =\n                    data.summary;\n            }\n\n            if (Array.isArray(data.news_results)) {\n                document.getElementById("newsList").innerHTML =\n                    renderNews(data.news_results);\n            }\n\n            if (data.article_title !== undefined) {\n                document.getElementById("sourceTitle").textContent =\n                    data.article_title || "Primary source";\n            }\n\n            var sourceLink = document.getElementById("sourceLink");\n\n            if (data.article_url) {\n                sourceLink.innerHTML =\n                    \'<a class="news-link" href="\' + esc(data.article_url) +\n                    \'" target="_self">Open primary source ↗</a>\';\n            } else {\n                sourceLink.innerHTML = "";\n            }\n        } catch (e) {\n            // One failed poll must not break the dashboard.\n        }\n    }\n\n    refreshJarvisData();\n    setInterval(refreshJarvisData, 1000);\n})();\n</script>\n'

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="referrer" content="strict-origin-when-cross-origin">

<title>Jarvis Research Hub</title>

<style>
* {{
    box-sizing: border-box;
}}

html {{
    min-height: 100%;
    background: #0b0d10;
}}

body {{
    margin: 0;
    min-height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    font-family: Arial, Helvetica, sans-serif;
    background: #0b0d10;
    color: #f1f3f5;
}}

.header {{
    position: sticky;
    top: 0;
    z-index: 50;
    min-height: 64px;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 22px;
    background: rgba(20, 23, 28, .97);
    border-bottom: 1px solid #2b3038;
    backdrop-filter: blur(10px);
}}

.logo {{
    font-size: 21px;
    font-weight: 800;
}}

.badge {{
    padding: 6px 10px;
    border-radius: 20px;
    background: #252b34;
    color: #9fb1c7;
    font-size: 12px;
}}

.query {{
    color: #8e9aaa;
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.main {{
    width: min(1800px, 100%);
    margin: 0 auto;
    padding: 10px;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 10px;
    align-items: start;
}}

.left {{
    min-width: 0;
    display: grid;
    grid-template-rows: minmax(480px, 55vh) minmax(360px, 45vh);
    gap: 10px;
}}

.right {{
    min-width: 0;
}}

.card {{
    min-width: 0;
    background: #15181d;
    border: 1px solid #2b3038;
    border-radius: 12px;
    overflow: hidden;
}}

.card-head {{
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    background: #1b1f25;
    border-bottom: 1px solid #2b3038;
}}

.card-title {{
    font-size: 15px;
    font-weight: 800;
}}

.card-sub {{
    color: #7f8b9a;
    font-size: 12px;
}}

.chart-card {{
    height: 100%;
}}

.chart-body {{
    height: calc(100% - 48px);
    min-height: 420px;
    background: #0d0f12;
}}

.market-chart {{
    width: 100%;
    height: 100%;
    min-height: 420px;
    background: #0d0f12;
}}

.chart-toolbar {{
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #2b3038;
    background: #111419;
}}

.chart-toolbar-title {{
    font-size: 12px;
    color: #c6cfda;
}}

.chart-source {{
    font-size: 11px;
    color: #7f8b9a;
}}

#marketChart {{
    width: 100%;
    height: calc(100% - 42px);
    min-height: 378px;
}}

.chart-error {{
    height: calc(100% - 42px);
    min-height: 378px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 30px;
    color: #9ba6b5;
    line-height: 1.6;
}}


.youtube-search-panel {{
    min-height: 360px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 34px;
    background: #0d0f12;
}}

.youtube-search-heading {{
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 20px;
}}

.youtube-search-row {{
    display: flex;
    gap: 10px;
    width: 100%;
    max-width: 760px;
}}

.youtube-search-row input {{
    flex: 1;
    min-width: 0;
    height: 50px;
    padding: 0 16px;
    border-radius: 10px;
    border: 1px solid #3a414c;
    background: #171a20;
    color: #fff;
    font-size: 16px;
    outline: none;
}}

.youtube-search-row input:focus {{
    border-color: #ff3347;
}}

.youtube-search-row button,
.youtube-open-button {{
    border: 0;
    border-radius: 10px;
    background: #ff0033;
    color: white;
    font-weight: 800;
    cursor: pointer;
    padding: 0 22px;
    min-height: 50px;
}}

.youtube-search-help {{
    max-width: 760px;
    margin: 16px 0 20px;
    color: #a9b2bf;
    line-height: 1.6;
}}

.youtube-open-button {{
    align-self: flex-start;
    background: #222831;
    border: 1px solid #3b4450;
}}

.youtube-picker {{
    padding: 14px;
    background: #0b0d10;
}}

.yt-player {{
    width: 100%;
    aspect-ratio: 16 / 9;
    min-height: 300px;
    background: #050608;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #252b34;
}}

.yt-player-wrap,
.yt-player-wrap iframe {{
    width: 100%;
    height: 100%;
    border: 0;
}}

.yt-player-empty {{
    display: flex;
    align-items: center;
    justify-content: center;
    color: #aab4c2;
    font-size: 20px;
}}

.yt-selected-title {{
    font-size: 16px;
    font-weight: 700;
    margin: 12px 4px;
    color: #f4f6f8;
}}

.yt-results-label {{
    color: #8e9aaa;
    margin: 8px 4px 10px;
    font-size: 13px;
}}

.yt-results {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    max-height: 190px;
    overflow-y: auto;
    padding-right: 4px;
}}

.yt-result {{
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 7px;
    text-align: left;
    padding: 7px;
    border: 1px solid #2a313b;
    border-radius: 9px;
    background: #15181d;
    color: #f1f3f5;
    cursor: pointer;
}}

.yt-result:hover,
.yt-result.selected {{
    border-color: #ff3347;
    background: #1b1f26;
}}

.yt-result img {{
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 6px;
    background: #080a0d;
}}

.yt-result-title {{
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-size: 12px;
    line-height: 1.35;
}}

.yt-play {{
    position: absolute;
    right: 12px;
    top: 76px;
    background: rgba(255,0,51,.92);
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.yt-empty {{
    padding: 30px;
    text-align: center;
    color: #8792a2;
}}

.video-card {{
    min-height: 360px;
}}

.video-body {{
    min-height: 360px;
    background: #080a0d;
    display: flex;
    flex-direction: column;
}}

.video-wrap {{
    width: 100%;
    aspect-ratio: 16 / 9;
    background: #000;
}}

.video-wrap iframe {{
    display: block;
    width: 100%;
    height: 100%;
    border: 0;
}}

.video-note {{
    padding: 9px 13px;
    font-size: 12px;
    color: #7f8b9a;
}}

.video-note a {{
    color: #5ba7ff;
}}

.video-placeholder {{
    min-height: 360px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 14px;
    color: #8e9aaa;
}}

.big-icon {{
    font-size: 52px;
}}

.primary-button {{
    display: inline-block;
    padding: 10px 15px;
    border-radius: 8px;
    background: #2d8cff;
    color: #fff;
    text-decoration: none;
    font-weight: 700;
    font-size: 13px;
}}

.summary-card {{
    min-height: 520px;
}}

.summary {{
    padding: 24px;
}}

.summary h1 {{
    margin: 0 0 18px;
    font-size: 27px;
}}

.summary-text {{
    white-space: pre-wrap;
    font-size: 16px;
    line-height: 1.75;
    color: #e8e8e8;
}}

.section-title {{
    margin-top: 32px;
    margin-bottom: 12px;
    font-size: 18px;
    font-weight: 800;
}}

.news-list {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.news-card {{
    display: grid;
    grid-template-columns: 38px minmax(0, 1fr);
    gap: 12px;
    padding: 15px;
    border: 1px solid #2b3038;
    border-radius: 10px;
    background: #111419;
}}

.news-number {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #263142;
    color: #a9c8ff;
    font-weight: 800;
}}

.news-content h3 {{
    margin: 0 0 8px;
    font-size: 15px;
    line-height: 1.4;
}}

.news-content p {{
    margin: 0;
    color: #b9c1cc;
    font-size: 13px;
    line-height: 1.55;
}}

.news-link {{
    display: inline-block;
    margin-top: 10px;
    color: #5ba7ff;
    text-decoration: none;
    font-weight: 700;
    font-size: 12px;
}}

.source-box {{
    margin-top: 26px;
    padding-top: 18px;
    border-top: 1px solid #30353d;
}}

.source-label {{
    color: #7f8b9a;
    font-size: 11px;
    margin-bottom: 7px;
    letter-spacing: .8px;
}}

.source-title {{
    font-weight: 700;
    line-height: 1.45;
}}

.empty-news {{
    padding: 18px;
    color: #7f8b9a;
    border: 1px dashed #333944;
    border-radius: 10px;
}}

@media (max-width: 900px) {{
    .main {{
        grid-template-columns: 1fr;
    }}

    .left {{
        grid-template-rows: 520px 420px;
    }}

    .header {{
        position: relative;
    }}
}}
</style>
</head>

<body>

<header class="header">
    <div class="logo">🤖 Jarvis Research Hub</div>
    <div class="badge">LIVE RESEARCH</div>
    <div class="query">{safe_query}</div>
</header>

<main class="main">

<section class="left">

    <!-- REAL INTERACTIVE TRADINGVIEW CHART -->
    <section class="card chart-card">

        <div class="card-head">
            <div class="card-title">📈 Live Market Chart / Pattern</div>
            <div class="card-sub">{safe_chart_symbol}</div>
        </div>

        <div class="chart-body">
            <div class="market-chart">
                <div class="chart-toolbar">
                    <div class="chart-toolbar-title">
                        📊 {html.escape(market_data.get("name", "NIFTY 50"))} — Live Market Chart
                    </div>
                    <div class="chart-source">Yahoo Finance</div>
                </div>
                <div id="marketChart"></div>
            </div>
        </div>        </div>

    </section>


    <!-- REAL YOUTUBE PLAYER -->
    <section class="card video-card">

        <div class="card-head">
            <div class="card-title">🎥 Important News Video</div>
            <div class="card-sub">YouTube</div>
        </div>

        <div class="video-body">
            {video_embed}
        </div>

    </section>

</section>


<section class="right">

    <section class="card summary-card">

        <div class="card-head">
            <div class="card-title">🧠 Jarvis Detailed Analysis</div>
            <div class="card-sub">AI analysis</div>
        </div>

        <div class="summary">

            <h1>What you need to know</h1>

            <div id="summaryText" class="summary-text">{safe_summary}</div>

            <div class="section-title">
                📰 Important News — Read Each Story
            </div>
            <div style="color:#7f8b9a;font-size:12px;margin-bottom:12px;">Read full story opens in this same Jarvis page/tab.</div>

            <div id="newsList" class="news-list">
                {news_cards}
            </div>

            <div class="source-box">
                <div class="source-label">PRIMARY SOURCE</div>
                <div id="sourceTitle" class="source-title">
                    {html.escape(article_title)}
                </div>
                {article_link}
            </div>

        </div>

    </section>

</section>

</main>

{live_poll_script}

<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.54.1"></script>
<script>
(function () {{
    const marketData = {market_data_json};
    const container = document.getElementById("marketChart");

    if (!container) return;

    if (!marketData.ok || !marketData.candles.length) {{
        container.innerHTML =
            '<div class="chart-error">Live market data is temporarily unavailable.<br>' +
            '<small>' + String(marketData.error || "No data returned") + '</small></div>';
        return;
    }}

    const options = {{
        chart: {{
            type: "candlestick",
            height: "100%",
            background: "#0d0f12",
            foreColor: "#aeb8c5",
            animations: {{ enabled: false }},
            toolbar: {{
                show: true,
                tools: {{
                    download: true,
                    selection: false,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true,
                    reset: true
                }}
            }},
            zoom: {{
                enabled: true,
                type: "x",
                autoScaleYaxis: true
            }}
        }},
        series: [{{
            name: marketData.name,
            data: marketData.candles
        }}],
        plotOptions: {{
            candlestick: {{
                colors: {{
                    upward: "#22b573",
                    downward: "#ef5350"
                }},
                wick: {{ useFillColor: true }}
            }}
        }},
        xaxis: {{
            type: "datetime",
            labels: {{ datetimeUTC: false }},
            axisBorder: {{ color: "#303641" }},
            axisTicks: {{ color: "#303641" }}
        }},
        yaxis: {{
            tooltip: {{ enabled: true }},
            decimalsInFloat: 2,
            forceNiceScale: true
        }},
        grid: {{
            borderColor: "#242a32",
            strokeDashArray: 3
        }},
        tooltip: {{
            shared: false,
            theme: "dark",
            x: {{ format: "dd MMM HH:mm" }}
        }},
        theme: {{ mode: "dark" }}
    }};

    const chart = new ApexCharts(container, options);
    chart.render();

    // Refresh only once per minute; no full-page reload.
    setInterval(async function () {{
        try {{
            const response = await fetch(
                "/jarvis_market_data.json?t=" + Date.now(),
                {{cache: "no-store"}}
            );
            if (!response.ok) return;
            const latest = await response.json();

            if (latest.ok && latest.candles && latest.candles.length) {{
                chart.updateSeries([{{
                    name: latest.name,
                    data: latest.candles
                }}], false);
            }}
        }} catch (_) {{}}
    }}, 60000);
}})();
</script>
<script>
(function () {{
    const marketData = {market_data_json};

    const container = document.getElementById("marketChart");

    if (!container) return;

    if (!marketData.ok || !marketData.candles.length) {{
        container.innerHTML =
            '<div class="chart-error">' +
            'Market chart data could not be loaded right now.<br>' +
            'Source: Yahoo Finance<br><small>' +
            String(marketData.error || "No data returned") +
            '</small></div>';
        return;
    }}

    const options = {{
        chart: {{
            type: "candlestick",
            height: "100%",
            background: "#0d0f12",
            foreColor: "#9ba6b5",
            toolbar: {{
                show: true,
                tools: {{
                    download: true,
                    selection: true,
                    zoom: true,
                    zoomin: true,
                    zoomout: true,
                    pan: true,
                    reset: true
                }}
            }},
            zoom: {{
                enabled: true,
                type: "x",
                autoScaleYaxis: true
            }}
        }},
        series: [{{
            name: marketData.name,
            data: marketData.candles
        }}],
        plotOptions: {{
            candlestick: {{
                colors: {{
                    upward: "#20b26b",
                    downward: "#ef5350"
                }},
                wick: {{
                    useFillColor: true
                }}
            }}
        }},
        xaxis: {{
            type: "datetime",
            labels: {{
                datetimeUTC: false
            }}
        }},
        yaxis: {{
            tooltip: {{
                enabled: true
            }},
            decimalsInFloat: 2
        }},
        grid: {{
            borderColor: "#252a31"
        }},
        tooltip: {{
            shared: false,
            theme: "dark"
        }},
        theme: {{
            mode: "dark"
        }}
    }};

    const chart = new ApexCharts(container, options);
    chart.render();

    // Refresh the market data periodically without reloading the Jarvis page.
    setInterval(async function () {{
        try {{
            const response = await fetch(
                "/jarvis_market_data.json?t=" + Date.now(),
                {{cache: "no-store"}}
            );

            if (!response.ok) return;

            const latest = await response.json();

            if (latest.ok && latest.candles && latest.candles.length) {{
                chart.updateSeries([{{
                    name: latest.name,
                    data: latest.candles
                }}], true);
            }}
        }} catch (e) {{
            // Keep the current chart if a refresh fails.
        }}
    }}, 60000);
}})();
</script>

</body>
</html>
"""

    safe_news = []
    for item in (news_results or []):
        if not item:
            continue
        safe_news.append({
            "title": str(item.get("title", "")),
            "body": str(
                item.get("body")
                or item.get("description")
                or item.get("snippet")
                or ""
            ),
            "url": str(get_url(item) or "")
        })

    live_data = {
        "summary": display_summary,
        "news_results": safe_news[:8],
        "article_title": str(article_title),
        "article_url": str(article_url or ""),
        "updated": time.time()
    }

    dashboard_data_path.write_text(
        json.dumps(live_data, ensure_ascii=False),
        encoding="utf-8"
    )

    market_data_path = (
        Path.home()
        / "AppData"
        / "Local"
        / "Temp"
        / "jarvis_market_data.json"
    )

    market_data_path.write_text(
        json.dumps(market_data, ensure_ascii=False),
        encoding="utf-8"
    )

    dashboard_path.write_text(html_content, encoding="utf-8")
    return dashboard_path



_jarvis_http_server = None
_jarvis_http_thread = None


def open_research_dashboard(
    query,
    video,
    chart,
    article,
    summary='',
    news_results=None,
    video_results=None
):
    """Serve the Jarvis dashboard and its locally downloaded MP4 over localhost.
    No YouTube iframe is required for video playback."""
    global _jarvis_http_server, _jarvis_http_thread

    try:
        dashboard = create_research_dashboard(
            query,
            video,
            chart,
            article,
            summary,
            news_results,
            video_results
        )

        import functools
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

        root = dashboard.parent

        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        if _jarvis_http_server is None:
            handler = functools.partial(
                QuietHandler,
                directory=str(root)
            )

            _jarvis_http_server = ThreadingHTTPServer(
                ("127.0.0.1", 8765),
                handler
            )

            _jarvis_http_thread = threading.Thread(
                target=_jarvis_http_server.serve_forever,
                daemon=True
            )
            _jarvis_http_thread.start()

        url = (
            "http://127.0.0.1:8765/"
            + dashboard.name
        )

        print("\nOpening ONE interactive Jarvis Research Hub:")
        print(url)

        # IMPORTANT: do not use noreferrer. YouTube requires an HTTP
        # Referer or equivalent client identification for embedded players.
        webbrowser.open(url)

        return True

    except Exception as e:
        print("Dashboard error:", e)
        return False



def print_selected_result(result, label):
    if result:
        print(f"\n{label}:")
        print("Title:", result.get("title", ""))
        print("URL:", get_url(result))


def live_search(query):
    """
    For a current/latest-information request:
      1. Find a relevant explanatory video.
      2. Find a relevant chart page when the topic is chartable.
      3. Find a detailed article.
      4. Put them into ONE local research dashboard.
      5. Give Qwen the collected text and speak a short summary.

    It does NOT open Google Images or three separate tabs.
    """

    print("\n================================")
    print("SMART LIVE SEARCH")
    print("================================")
    print("Topic:", query)

    speak(
        "I'm finding a useful video, chart and detailed article."
    )

    try:
        # -------------------------------------------------
        # VIDEO
        # -------------------------------------------------
        print("\nSearching for a video...")

        video_results = find_youtube_results(query, max_results=6)

        if video_results:
            video = video_results[0]
        else:
            video = find_video_result(query)
            video_results = [video] if video else []

        # -------------------------------------------------
        # CHART
        # -------------------------------------------------
        print("Searching for a chart...")

        chart_symbol = get_chart_symbol(query)

        # Never trust a generic TradingView search result (e.g. VIEW).
        # The dashboard chooses the symbol from the user's query.
        chart = {
            "title": f"TradingView — {chart_symbol}",
            "href": (
                "https://www.tradingview.com/chart/?symbol="
                + urllib.parse.quote(chart_symbol, safe=":")
            ),
            "body": (
                f"Live interactive TradingView chart for {chart_symbol}."
            )
        }
        chart_results = [chart]

        # -------------------------------------------------
        # DETAILED ARTICLE
        # -------------------------------------------------
        print("Searching for a detailed article...")

        article_results = smart_search(
            f"{query} latest detailed news analysis"
        )

        article = find_domain_result(
            article_results,
            [
                "reuters.com",
                "moneycontrol.com",
                "economictimes.indiatimes.com",
                "livemint.com",
                "business-standard.com",
                "thehindu.com",
                "ndtv.com",
                "indiatoday.in"
            ]
        )

        if not article and article_results:
            article = article_results[0]

        # -------------------------------------------------
        # PREPARE THE THREE TABS
        # -------------------------------------------------

        video_url = get_url(video) if video else (
            "https://www.youtube.com/results?search_query="
            + urllib.parse.quote(query + " latest news explanation")
        )

        chart_url = get_url(chart)

        article_url = get_url(article) if article else (
            "https://news.google.com/search?q="
            + urllib.parse.quote(query)
        )

        print_selected_result(video, "VIDEO")
        print_selected_result(chart, "CHART")
        print_selected_result(article, "DETAILED ARTICLE")

        # Open the dashboard immediately. It starts with a preparing
        # message and polls the local JSON file while Qwen works.
        dashboard_opened = open_research_dashboard(
            query,
            video,
            chart,
            article,
            "Jarvis is analyzing the latest news. Please wait a moment...",
            article_results[:8]
        )

        if not dashboard_opened:
            print("Dashboard could not be opened.")

        speak(
            "I found the sources. I'm preparing your detailed summary now."
        )

        # -------------------------------------------------
        # COLLECT SEARCH INFORMATION FOR QWEN
        # -------------------------------------------------
        information = ""

        selected = [
            ("VIDEO", video),
            ("CHART", chart),
            ("ARTICLE", article)
        ]

        for label, result in selected:
            if result:
                information += f"""
{label}

TITLE:
{result.get("title", "")}

DETAILS:
{result.get("body", "")}

URL:
{get_url(result)}
"""

        # Give Qwen concrete headlines/snippets rather than only
        # generic publisher landing-page descriptions.
        for i, result in enumerate(article_results[:8], start=1):
            information += f"""
SEARCH RESULT {i}

TITLE:
{result.get("title", "")}

DETAILS:
{result.get("body", result.get("description", ""))}

URL:
{get_url(result)}
"""

        # -------------------------------------------------
        # QWEN SUMMARY
        # -------------------------------------------------
        print("\nJarvis is analyzing the information...")

        summary_prompt = f"""
You are Jarvis, a factual news assistant.

USER QUESTION:
{query}

FRESH SEARCH MATERIAL:
{information}

Identify the actual events in the supplied headlines/snippets.
Do NOT summarize the existence of news websites.

Return ONLY a concise briefing:

IMPORTANT NEWS TODAY:
- Pick the 3 most important concrete developments.
- For each: 1 short sentence saying WHAT happened + 1 short sentence saying WHY it matters.

WHAT TO WATCH:
- 3 short bullet points.

Rules:
- Maximum 180 words total.
- Never invent facts, numbers, dates or quotes.
- Use only concrete events supported by the supplied search material.
- Ignore generic homepage text such as "breaking news", "latest headlines", and publisher descriptions.
- Prefer specific headlines and snippets.
- If the material lacks specific events, say that clearly.
- For trading/market questions, facts only; no financial advice.
- English -> English.
- Hindi -> Hindi.
- Hinglish -> Hinglish.
- Keep it natural enough to speak while preserving all four sections.
"""


        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
        )

        answer = response["message"]["content"].strip()

        print("\n================================")
        print("JARVIS SUMMARY")
        print("================================")
        print(answer)

        # -------------------------------------------------
        # UPDATE THE ALREADY-OPEN DASHBOARD
        # -------------------------------------------------
        create_research_dashboard(
            query,
            video,
            chart,
            article,
            answer,
            article_results[:8],
            video_results
        )

        print("Jarvis Research Hub updated in the existing tab.")

        # Speak the same summary that is now visible on screen.
        speak(answer)

    except Exception as e:
        print("\nSmart Search Error:", e)
        speak(
            "I found some information, but I had trouble organizing it."
        )


# =========================================================
# NORMAL AI CHAT
# =========================================================

def chat(query):

    print(
        "\nJarvis is thinking..."
    )

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": f"""
You are Jarvis.

Answer the user's question naturally.

User:
{query}

Rules:

- English question → English answer.
- Hindi question → Hindi answer.
- Hinglish question → Hinglish answer.
- Be helpful.
- Keep the answer reasonably short because it will be spoken aloud.
"""
            }
        ]
    )

    answer = response[
        "message"
    ][
        "content"
    ].strip()


    print(
        "\nAI Answer:",
        answer
    )

    speak(answer)


# =========================================================
# PROCESS COMMAND
# =========================================================

def process_command(command):

    print(
        "\nThinking..."
    )

    try:

        # Ask Qwen what the user wants
        result = ask_ai(
            command
        )

        print(
            "AI:",
            result
        )


        # Convert AI JSON to Python dictionary
        data = extract_json(
            result
        )


        action = data.get(
            "action",
            ""
        )

        query = data.get(
            "query",
            ""
        )


        print(
            "Action:",
            action
        )

        print(
            "Query:",
            query
        )


        # =========================================
        # OPEN WEBSITE
        # =========================================

        if action == "OPEN_WEBSITE":

            open_website(
                query
            )


        # =========================================
        # GOOGLE SEARCH
        # =========================================

        elif action == "SEARCH_WEB":

            search_web(
                query
            )


        # =========================================
        # LIVE INTERNET SEARCH
        # =========================================

        elif action == "LIVE_SEARCH":

            live_search(
                query
            )


        # =========================================
        # YOUTUBE
        # =========================================

        elif action == "PLAY_YOUTUBE":

            play_youtube(
                query
            )


        # =========================================
        # WINDOWS APP
        # =========================================

        elif action == "OPEN_APP":

            open_app(
                query
            )


        # =========================================
        # NORMAL CHAT
        # =========================================

        elif action == "CHAT":

            chat(
                query
            )


        # =========================================
        # STOP
        # =========================================

        elif action == "STOP":

            speak(
                "Okay, stopping Jarvis."
            )

            return False


        # =========================================
        # UNKNOWN ACTION
        # =========================================

        else:

            print(
                "Unknown action:",
                action
            )

            speak(
                "I don't know how to do that yet."
            )


    except Exception as e:

        print(
            "\nCommand Error:",
            e
        )

        speak(
            "Sorry, I had trouble understanding that command."
        )


    return True


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    speak(
        "Initializing Jarvis."
    )


    while True:

        try:

            print(
                "\nListening for Jarvis..."
            )


            # -----------------------------------------
            # LISTEN FOR WAKE WORD
            # -----------------------------------------

            with sr.Microphone() as source:

                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=4
                )


            word = recognizer.recognize_google(
                audio
            )


            print(
                "You said:",
                word
            )


            # =========================================
            # WAKE WORD
            # =========================================

            if "jarvis" in word.lower():

                speak(
                    "Yes, I'm listening."
                )


                # -------------------------------------
                # LISTEN FOR COMMAND
                # -------------------------------------

                with sr.Microphone() as source:

                    print(
                        "Jarvis Active..."
                    )

                    audio = recognizer.listen(
                        source,
                        timeout=5,
                        phrase_time_limit=10
                    )


                command = recognizer.recognize_google(
                    audio
                )


                print(
                    "Command:",
                    command
                )


                # -------------------------------------
                # PROCESS COMMAND
                # -------------------------------------

                running = process_command(
                    command
                )


                if not running:

                    break


        # =============================================
        # TIMEOUT
        # =============================================

        except sr.WaitTimeoutError:

            print(
                "No command detected."
            )


        # =============================================
        # SPEECH NOT UNDERSTOOD
        # =============================================

        except sr.UnknownValueError:

            print(
                "I could not understand that."
            )


        # =============================================
        # GOOGLE SPEECH ERROR
        # =============================================

        except sr.RequestError as e:

            print(
                "Speech recognition error:",
                e
            )


        # =============================================
        # CTRL + C
        # =============================================

        except KeyboardInterrupt:

            print(
                "\nJarvis stopped."
            )

            break


        # =============================================
        # OTHER ERROR
        # =============================================

        except Exception as e:

            print(
                "Error:",
                e
            )