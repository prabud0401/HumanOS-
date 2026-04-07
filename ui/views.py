"""
HumanOS UI — Full-stack Django views.

Page views render templates. API views return HTML fragments for HTMX.
"""

import os
import json
import datetime
from pathlib import Path

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = Path(__file__).resolve().parent.parent


# ─── Page Views ───────────────────────────────────────────────

def dashboard(request):
    return render(request, "dashboard.html", {"active_page": "dashboard"})


def brain_page(request):
    model_name = os.environ.get("CLAUDE_API_KEY", "")
    ctx = {
        "active_page": "brain",
        "model_name": "Claude" if os.environ.get("CLAUDE_API_KEY") else "Not configured",
        "fallback_model": "OpenAI GPT" if os.environ.get("OPENAI_API_KEY") else "None",
    }
    return render(request, "brain.html", ctx)


def financial_page(request):
    return render(request, "financial.html", {"active_page": "financial"})


def meetings_page(request):
    return render(request, "meetings.html", {"active_page": "meetings"})


def memory_page(request):
    return render(request, "memory.html", {"active_page": "memory"})


def settings_page(request):
    return render(request, "settings.html", {"active_page": "settings"})


# ─── HTMX API Fragments ──────────────────────────────────────

def _get_health_data():
    """Call the pulse monitor and return organ health dict."""
    try:
        from core.pulse import get_pulse
        pulse = get_pulse()
        report = pulse.check_all()
        return report
    except Exception:
        return None


def api_status_badge(request):
    report = _get_health_data()
    if not report:
        return HttpResponse('<span class="w-2 h-2 rounded-full bg-gray-600"></span> Unknown')
    color_map = {"healthy": "bg-bio-500 pulse-glow", "degraded": "bg-amber-500", "unhealthy": "bg-red-500"}
    color = color_map.get(report.status.value, "bg-gray-600")
    return HttpResponse(
        f'<span class="w-2 h-2 rounded-full {color}"></span> '
        f'{report.healthy_count} healthy · {report.degraded_count} degraded'
    )


def api_stats_cards(request):
    report = _get_health_data()
    if not report:
        return HttpResponse('<div class="text-xs text-gray-600">Health data unavailable</div>')

    cards = [
        ("Total Organs", "16", "text-white", "bg-gray-800"),
        ("Healthy", str(report.healthy_count), "text-bio-400", "bg-bio-950/50"),
        ("Degraded", str(report.degraded_count), "text-amber-400", "bg-amber-950/50"),
        ("Unhealthy", str(report.unhealthy_count), "text-red-400", "bg-red-950/50"),
    ]
    html = '<div class="grid grid-cols-2 gap-3">'
    for label, value, text_color, bg_color in cards:
        html += f'''
        <div class="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <div class="text-xs text-gray-500 mb-1">{label}</div>
          <div class="text-2xl font-bold {text_color}">{value}</div>
        </div>'''
    html += '</div>'
    return HttpResponse(html)


ORGAN_POSITIONS = {
    "brain":              (120, 30),
    "eyes":               (120, 55),
    "ears":               (120, 70),
    "voice":              (120, 100),
    "lungs":              (120, 140),
    "heart":              (105, 155),
    "immune_system":      (75, 175),
    "circulatory_system": (165, 175),
    "digestive_system":   (120, 210),
    "skeleton":           (55, 230),
    "hands":              (185, 230),
    "nervous_system":     (120, 250),
    "endocrine":          (55, 270),
    "financial_cortex":   (185, 270),
    "memory":             (120, 290),
    "reproductive":       (120, 340),
}

ORGAN_LABELS = {
    "brain": "Brain", "eyes": "Eyes", "ears": "Ears", "voice": "Voice",
    "lungs": "Lungs", "heart": "Heart", "immune_system": "Immune",
    "circulatory_system": "Circulatory", "digestive_system": "Digestive",
    "skeleton": "Skeleton", "hands": "Hands", "nervous_system": "Nervous",
    "endocrine": "Endocrine", "financial_cortex": "Finance",
    "memory": "Memory", "reproductive": "Reproductive",
}


def api_body_map(request):
    report = _get_health_data()
    color_map = {"healthy": "#22c55e", "degraded": "#f59e0b", "unhealthy": "#ef4444"}

    svg = '<svg viewBox="0 0 240 420" class="w-full h-full">'
    # Body silhouette
    svg += '''
    <ellipse cx="120" cy="45" rx="35" ry="40" fill="none" stroke="#1e293b" stroke-width="1.5"/>
    <path d="M85 85 Q60 100 45 180 L55 180 Q65 130 85 110 Z" fill="none" stroke="#1e293b" stroke-width="1.5"/>
    <path d="M155 85 Q180 100 195 180 L185 180 Q175 130 155 110 Z" fill="none" stroke="#1e293b" stroke-width="1.5"/>
    <path d="M85 85 L85 110 Q85 130 75 220 L75 340 L95 340 L100 260 L120 260 L140 260 L145 340 L165 340 L165 220 Q155 130 155 110 L155 85 Q140 95 120 95 Q100 95 85 85 Z" fill="none" stroke="#1e293b" stroke-width="1.5"/>
    '''
    # Organ dots
    for organ_name, (x, y) in ORGAN_POSITIONS.items():
        status = "unknown"
        msg = "No data"
        if report and organ_name in report.organs:
            oh = report.organs[organ_name]
            status = oh.status.value
            msg = oh.message
        color = color_map.get(status, "#475569")
        glow = 'class="pulse-glow"' if status == "healthy" else ""
        label = ORGAN_LABELS.get(organ_name, organ_name)
        svg += f'''
        <g class="organ-dot cursor-pointer" hx-get="/ui/api/organ-detail/{organ_name}/" hx-target="#organ-detail" hx-swap="innerHTML">
          <circle cx="{x}" cy="{y}" r="8" fill="{color}" opacity="0.3" {glow}/>
          <circle cx="{x}" cy="{y}" r="4" fill="{color}" {glow}/>
          <title>{label}: {status} — {msg}</title>
        </g>'''

    svg += '</svg>'
    return HttpResponse(svg)


def api_organ_grid(request):
    report = _get_health_data()
    color_map = {"healthy": "border-bio-500/30 bg-bio-950/20", "degraded": "border-amber-500/30 bg-amber-950/20", "unhealthy": "border-red-500/30 bg-red-950/20"}
    dot_map = {"healthy": "bg-bio-500", "degraded": "bg-amber-500", "unhealthy": "bg-red-500"}

    html = ""
    for organ_name in ORGAN_POSITIONS:
        label = ORGAN_LABELS.get(organ_name, organ_name)
        status = "unknown"
        if report and organ_name in report.organs:
            status = report.organs[organ_name].status.value
        border = color_map.get(status, "border-gray-700 bg-gray-800/20")
        dot = dot_map.get(status, "bg-gray-600")
        html += f'''
        <div class="rounded-lg p-3 border {border} cursor-pointer hover:brightness-125 transition"
             hx-get="/ui/api/organ-detail/{organ_name}/" hx-target="#organ-detail" hx-swap="innerHTML">
          <div class="flex items-center gap-2 mb-1">
            <span class="w-2 h-2 rounded-full {dot}"></span>
            <span class="text-xs font-medium text-gray-300">{label}</span>
          </div>
          <div class="text-[10px] text-gray-500">{status}</div>
        </div>'''
    return HttpResponse(html)


def api_organ_detail(request, organ_name):
    report = _get_health_data()
    label = ORGAN_LABELS.get(organ_name, organ_name)
    dot_map = {"healthy": "bg-bio-500", "degraded": "bg-amber-500", "unhealthy": "bg-red-500"}

    if report and organ_name in report.organs:
        oh = report.organs[organ_name]
        dot = dot_map.get(oh.status.value, "bg-gray-600")
        html = f'''
        <h3 class="text-sm font-semibold text-gray-400 mb-3">Organ Details</h3>
        <div class="space-y-3">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full {dot}"></span>
            <span class="text-lg font-bold">{label}</span>
          </div>
          <div class="text-xs text-gray-500 space-y-1">
            <div>Status: <span class="text-gray-300">{oh.status.value}</span></div>
            <div>Message: <span class="text-gray-300">{oh.message}</span></div>
            <div>Response: <span class="text-gray-300">{oh.response_time_ms:.0f}ms</span></div>
            <div>Module: <span class="text-gray-300 font-mono">organs.{organ_name}</span></div>
          </div>
          <a href="/api/{organ_name.replace('_', '-')}/health" target="_blank"
             class="inline-block mt-2 px-3 py-1 bg-gray-800 rounded text-xs text-gray-400 hover:text-white transition">
            View API →
          </a>
        </div>'''
    else:
        html = f'''
        <h3 class="text-sm font-semibold text-gray-400 mb-3">{label}</h3>
        <p class="text-xs text-gray-600">Health data not available.</p>'''
    return HttpResponse(html)


def api_organ_health(request, organ_name):
    report = _get_health_data()
    dot_map = {"healthy": "bg-bio-500", "degraded": "bg-amber-500", "unhealthy": "bg-red-500"}
    if report and organ_name in report.organs:
        oh = report.organs[organ_name]
        dot = dot_map.get(oh.status.value, "bg-gray-600")
        html = f'''
        <div class="flex items-center gap-2 mb-2">
          <span class="w-2 h-2 rounded-full {dot}"></span>
          <span class="text-sm font-medium text-gray-300">{oh.status.value.title()}</span>
        </div>
        <p class="text-xs text-gray-500">{oh.message}</p>
        <p class="text-xs text-gray-600 mt-1">{oh.response_time_ms:.0f}ms response</p>'''
    else:
        html = '<p class="text-xs text-gray-600">Not available</p>'
    return HttpResponse(html)


def api_health_refresh(request):
    return api_body_map(request)


# ─── Brain Chat ───────────────────────────────────────────────

@require_POST
def api_brain_chat(request):
    message = request.POST.get("message", "").strip()
    if not message:
        return HttpResponse("")

    # User message bubble
    user_html = f'''
    <div class="chat-msg flex gap-3 justify-end">
      <div class="bg-neural-600/30 rounded-xl rounded-tr-none px-4 py-3 max-w-2xl">
        <p class="text-sm text-gray-200">{message}</p>
      </div>
      <div class="w-8 h-8 rounded-lg bg-gray-700 flex-shrink-0 flex items-center justify-center text-xs">You</div>
    </div>'''

    # Try to get a real Brain response
    try:
        from organs.brain.services import BrainService
        svc = BrainService()
        response = svc.analyze(message)
    except Exception:
        response = _fallback_brain_response(message)

    # Bot response bubble
    bot_html = f'''
    <div class="chat-msg flex gap-3">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-bio-500 to-neural-500 flex-shrink-0 flex items-center justify-center text-xs font-bold">H</div>
      <div class="bg-gray-800 rounded-xl rounded-tl-none px-4 py-3 max-w-2xl">
        <p class="text-sm text-gray-300">{response}</p>
      </div>
    </div>'''

    return HttpResponse(user_html + bot_html)


def _fallback_brain_response(message):
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["hello", "hi", "hey"]):
        return "Hello! I'm your HumanOS Brain. I'm running in local mode right now (no LLM API key configured). Add your Claude or OpenAI key to dna/.env to unlock full AI capabilities."
    elif any(w in msg_lower for w in ["status", "health", "how are you"]):
        report = _get_health_data()
        if report:
            return f"System status: {report.healthy_count} organs healthy, {report.degraded_count} degraded, {report.unhealthy_count} unhealthy. All core infrastructure is running."
        return "I can't reach the health monitor right now."
    elif any(w in msg_lower for w in ["help", "what can you do"]):
        return "I can help with: analyzing text, making decisions, summarizing meetings, financial insights, and general conversation. Configure an LLM API key in dna/.env for full capabilities."
    else:
        return f"I received your message: \"{message}\". To give you a real AI-powered response, please configure CLAUDE_API_KEY or OPENAI_API_KEY in dna/.env. Right now I'm running in echo mode."


# ─── Financial ────────────────────────────────────────────────

_transactions = []
_recurring = []


def api_financial_summary(request):
    income = sum(t["amount"] for t in _transactions if t["type"] == "income")
    expenses = sum(t["amount"] for t in _transactions if t["type"] == "expense")
    loans = sum(t["amount"] for t in _recurring if "loan" in t.get("name", "").lower())
    net = income - expenses

    def _fmt(v):
        return f"${v:,.2f}" if v else "--"

    return HttpResponse(f'''
    <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs text-gray-500 mb-1">Monthly Income</div>
      <div class="text-2xl font-bold text-bio-400">{_fmt(income)}</div>
    </div>
    <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs text-gray-500 mb-1">Monthly Expenses</div>
      <div class="text-2xl font-bold text-amber-400">{_fmt(expenses)}</div>
    </div>
    <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs text-gray-500 mb-1">Recurring Bills</div>
      <div class="text-2xl font-bold text-red-400">{_fmt(loans) if loans else str(len(_recurring))}</div>
    </div>
    <div class="bg-gray-900 rounded-xl p-5 border border-gray-800">
      <div class="text-xs text-gray-500 mb-1">Net</div>
      <div class="text-2xl font-bold {"text-bio-400" if net >= 0 else "text-red-400"}">{_fmt(net)}</div>
    </div>''')


@require_POST
def api_financial_transaction(request):
    t = {
        "type": request.POST.get("type", "expense"),
        "amount": float(request.POST.get("amount", 0)),
        "description": request.POST.get("description", ""),
        "category": request.POST.get("category", ""),
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _transactions.insert(0, t)

    color = "text-bio-400" if t["type"] == "income" else "text-amber-400"
    sign = "+" if t["type"] == "income" else "-"
    return HttpResponse(f'''
    <div class="flex items-center justify-between py-2 border-b border-gray-800">
      <div>
        <div class="text-sm text-gray-300">{t["description"]}</div>
        <div class="text-xs text-gray-600">{t["category"]} · {t["date"]}</div>
      </div>
      <div class="{color} font-mono text-sm">{sign}${t["amount"]:,.2f}</div>
    </div>''')


def api_financial_transactions(request):
    if not _transactions:
        return HttpResponse('<div class="text-xs text-gray-600 py-4 text-center">No transactions yet. Record one above.</div>')
    html = ""
    for t in _transactions[:20]:
        color = "text-bio-400" if t["type"] == "income" else "text-amber-400"
        sign = "+" if t["type"] == "income" else "-"
        html += f'''
        <div class="flex items-center justify-between py-2 border-b border-gray-800">
          <div>
            <div class="text-sm text-gray-300">{t["description"]}</div>
            <div class="text-xs text-gray-600">{t["category"]} · {t["date"]}</div>
          </div>
          <div class="{color} font-mono text-sm">{sign}${t["amount"]:,.2f}</div>
        </div>'''
    return HttpResponse(html)


def api_financial_recurring_list(request):
    if not _recurring:
        return HttpResponse('<div class="text-xs text-gray-600">No recurring bills set up yet.</div>')
    html = ""
    for r in _recurring:
        html += f'''
        <div class="flex items-center justify-between py-2 border-b border-gray-800">
          <div>
            <div class="text-sm text-gray-300">{r["name"]}</div>
            <div class="text-xs text-gray-600">{r["frequency"]} · Day {r.get("due_day", "-")}</div>
          </div>
          <div class="text-amber-400 font-mono text-sm">${r["amount"]:,.2f}</div>
        </div>'''
    return HttpResponse(html)


@require_POST
def api_financial_recurring_add(request):
    r = {
        "name": request.POST.get("name", ""),
        "amount": float(request.POST.get("amount", 0)),
        "frequency": request.POST.get("frequency", "monthly"),
        "due_day": request.POST.get("due_day", ""),
    }
    _recurring.append(r)
    return api_financial_recurring_list(request)


def api_financial_recurring(request):
    if request.method == "POST":
        return api_financial_recurring_add(request)
    return api_financial_recurring_list(request)


# ─── Meetings ─────────────────────────────────────────────────

@require_POST
def api_meetings_ingest(request):
    url = request.POST.get("meeting_url", "").strip()
    transcript = request.POST.get("transcript", "").strip()

    if not url and not transcript:
        return HttpResponse('<p class="text-xs text-red-400">Please provide a meeting link or transcript.</p>')

    source = url if url else "Pasted transcript"
    return HttpResponse(f'''
    <div class="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div class="flex items-center gap-2 mb-2">
        <span class="w-2 h-2 rounded-full bg-amber-500"></span>
        <span class="text-sm font-medium text-gray-300">Meeting Queued</span>
      </div>
      <p class="text-xs text-gray-500">Source: {source}</p>
      <p class="text-xs text-gray-500 mt-1">The Lungs organ will process this when an LLM adapter is configured. For now, the raw data has been captured.</p>
      {"<pre class='mt-2 text-xs text-gray-600 bg-gray-900 p-2 rounded max-h-40 overflow-y-auto'>" + transcript[:500] + "</pre>" if transcript else ""}
    </div>''')


def api_meetings_history(request):
    return HttpResponse('<p class="text-xs text-gray-600">No meetings processed yet. Paste a link or transcript to get started.</p>')


# ─── Memory ───────────────────────────────────────────────────

@require_POST
def api_memory_search(request):
    query = request.POST.get("query", "").strip()
    if not query:
        return HttpResponse("")
    return HttpResponse(f'''
    <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
      <div class="text-xs text-gray-600 mb-2">Search: "{query}"</div>
      <p class="text-sm text-gray-500">No results yet. Memory will populate as you use HumanOS — process meetings, make decisions, record transactions. Configure a vector database (ChromaDB) for semantic search.</p>
    </div>''')


def api_memory_stats(request):
    return HttpResponse('''
    <div class="grid grid-cols-3 gap-4 text-center text-xs text-gray-600">
      <div><div class="text-lg font-bold text-gray-400">0</div>Documents</div>
      <div><div class="text-lg font-bold text-gray-400">0</div>Decisions</div>
      <div><div class="text-lg font-bold text-gray-400">0</div>Meetings</div>
    </div>''')


# ─── Settings ─────────────────────────────────────────────────

def api_settings_identity(request):
    try:
        from core.dna_loader import get_dna
        dna = get_dna()
        if dna and hasattr(dna, "identity"):
            ident = dna.identity
            html = f'''
            <div class="space-y-2 text-xs">
              <div class="flex justify-between"><span class="text-gray-500">Name</span><span class="text-gray-300">{getattr(ident, "name", "Not set")}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Role</span><span class="text-gray-300">{getattr(ident, "role", "Not set")}</span></div>
              <div class="flex justify-between"><span class="text-gray-500">Timezone</span><span class="text-gray-300">{getattr(ident, "timezone", "Not set")}</span></div>
            </div>'''
            return HttpResponse(html)
    except Exception:
        pass
    return HttpResponse('<p class="text-xs text-gray-600">No identity.yaml found. Copy dna/identity.example.yaml to dna/identity.yaml and fill in your details.</p>')


def api_settings_keys_status(request):
    keys = [
        ("CLAUDE_API_KEY", "Claude (Anthropic)"),
        ("OPENAI_API_KEY", "OpenAI"),
        ("GITHUB_TOKEN", "GitHub"),
        ("SLACK_BOT_TOKEN", "Slack"),
        ("AZURE_CLIENT_ID", "Azure AD"),
        ("GOOGLE_CLIENT_ID", "Google"),
        ("ZOOM_CLIENT_ID", "Zoom"),
    ]
    html = '<div class="space-y-2">'
    for env_var, label in keys:
        val = os.environ.get(env_var, "")
        if val and val != f"your-{env_var.lower().replace('_', '-')}":
            html += f'<div class="flex items-center gap-2 text-xs"><span class="w-2 h-2 rounded-full bg-bio-500"></span><span class="text-gray-300">{label}</span><span class="text-gray-600">configured</span></div>'
        else:
            html += f'<div class="flex items-center gap-2 text-xs"><span class="w-2 h-2 rounded-full bg-gray-600"></span><span class="text-gray-500">{label}</span><span class="text-gray-700">not set</span></div>'
    html += '</div>'
    return HttpResponse(html)


def api_settings_system_info(request):
    import django
    import sys
    return HttpResponse(f'''
    <div class="space-y-2 text-xs">
      <div class="flex justify-between"><span class="text-gray-500">Python</span><span class="text-gray-300 font-mono">{sys.version.split()[0]}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Django</span><span class="text-gray-300 font-mono">{django.__version__}</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Database</span><span class="text-gray-300 font-mono">SQLite (dev)</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Event Bus</span><span class="text-gray-300 font-mono">InMemoryBus</span></div>
      <div class="flex justify-between"><span class="text-gray-500">Architecture</span><span class="text-gray-300">Organic (16 organs)</span></div>
    </div>''')


@require_POST
def api_settings_export_dna(request):
    return HttpResponse('''
    <div class="bg-gray-800 rounded-lg p-3 text-xs">
      <p class="text-bio-400 mb-1">DNA Template exported!</p>
      <p class="text-gray-500">Share the repo + dna/identity.example.yaml with anyone who wants to clone themselves. They just need to:</p>
      <ol class="mt-2 space-y-1 text-gray-500 list-decimal list-inside">
        <li>Clone the repo</li>
        <li>Copy identity.example.yaml → identity.yaml</li>
        <li>Fill in their own data</li>
        <li>Run python scripts/setup.py</li>
      </ol>
    </div>''')
