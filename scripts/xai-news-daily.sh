#!/bin/bash
#
# xai-news-daily.sh - Daily AI news from xAI/Grok with voice narration
#
# Fetches AI news from Twitter/X using xAI API, generates a summary,
# creates voice narration with ElevenLabs (sag), and sends to Telegram.
#
# Usage (via Doppler):
#   doppler run --project mao-mao --config prd --command 'bash /Users/francescooddo/clawd/scripts/xai-news-daily.sh'
#
# Cron (runs daily at 9 AM CET):
#   0 8 * * * doppler run --project mao-mao --config prd --command 'bash /Users/francescooddo/clawd/scripts/xai-news-daily.sh' >> /var/log/xai-news-daily.log 2>&1
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/Library/Logs/clawdbot"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/xai-news-daily.log"
TEMP_DIR="/tmp/xai-news-daily-$$"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-904041730}"

# Ensure temp directory exists
mkdir -p "$TEMP_DIR"
trap "rm -rf $TEMP_DIR" EXIT

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting AI news daily summary..."

# Check required commands
CLAWDBOT_BIN="${CLAWDBOT_BIN:-/Users/francescooddo/.npm-global/bin/clawdbot}"

for cmd in curl jq sag; do
    if ! command -v "$cmd" &> /dev/null; then
        log "ERROR: Required command '$cmd' not found"
        exit 1
    fi
done

# Check clawdbot is available
if [ ! -f "$CLAWDBOT_BIN" ]; then
    log "ERROR: clawdbot not found at $CLAWDBOT_BIN"
    exit 1
fi

# Check for XAI_API_KEY
if [ -z "${XAI_API_KEY:-}" ]; then
    log "ERROR: XAI_API_KEY environment variable not set"
    exit 1
fi

# Step 1: Get yesterday's date
log "Calculating yesterday's date..."
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null)
if [ -z "$YESTERDAY" ]; then
    log "ERROR: Failed to calculate yesterday's date"
    exit 1
fi

log "Searching AI news from: $YESTERDAY"

# Step 2: Call xAI API to fetch AI news
log "Fetching AI news from xAI/Grok..."

XAI_RESPONSE="$TEMP_DIR/xai-response.json"

# Calculate date range (last 3 days for better coverage)
THREE_DAYS_AGO=$(date -v-3d +%Y-%m-%d 2>/dev/null || date -d "3 days ago" +%Y-%m-%d 2>/dev/null)

curl -s -X POST "https://api.x.ai/v1/responses" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $XAI_API_KEY" \
    -d "{
        \"model\": \"grok-4-1-fast\",
        \"input\": [
            {
                \"role\": \"user\",
                \"content\": \"Search X/Twitter for the most important AI news, announcements, and developments from the last 24-48 hours (focus on $YESTERDAY and today). Search posts from @OpenAI, @AnthropicAI, @GoogleAI, @GoogleDeepMind, @MetaAI, @xai, @sama, @demishassabis and other AI leaders.\\n\\nFocus on:\\n- New AI model releases and updates\\n- Major company announcements\\n- Significant AI research papers or breakthroughs\\n- AI product launches\\n- Important AI policy or regulation news\\n\\nProvide a concise summary of the top 5-8 most significant AI news items.\\n\\nIMPORTANT FORMATTING RULES (for Telegram):\\n- Do NOT use markdown headers (no # or ##)\\n- Do NOT use markdown links like [text](url)\\n- Use plain URLs on their own line\\n- Use emojis as bullet points (🔹, 📰, 🚀, etc.)\\n- For emphasis, use *bold* with single asterisks\\n- Keep each news item compact (2-3 lines max)\\n\\nFormat each item like this:\\n🔹 *Headline Here*\\nPosted by @account (Date) - Brief 1-line description of why significant.\\n🔗 https://x.com/...\\n\\nEnd with a sources section listing all URLs.\"
            }
        ],
        \"tools\": [
            {
                \"type\": \"x_search\",
                \"from_date\": \"$THREE_DAYS_AGO\"
            }
        ]
    }" > "$XAI_RESPONSE" 2>&1

if [ $? -ne 0 ]; then
    log "ERROR: Failed to call xAI API"
    cat "$XAI_RESPONSE" | tee -a "$LOG_FILE"
    exit 1
fi

# Step 3: Parse xAI response
log "Parsing xAI response..."

# Check if API returned an error
if jq -e '.error' "$XAI_RESPONSE" > /dev/null 2>&1; then
    ERROR_MSG=$(jq -r '.error.message // "Unknown error"' "$XAI_RESPONSE")
    log "ERROR: xAI API returned an error: $ERROR_MSG"
    cat "$XAI_RESPONSE" >> "$LOG_FILE"
    exit 1
fi

# Function to escape special characters for Telegram MarkdownV2
# Characters to escape: _ * [ ] ( ) ~ ` > # + - = | { } . !
escape_markdown_v2() {
    local text="$1"
    # Escape special characters (but preserve * for bold formatting)
    # We keep * unescaped since we want bold to work
    echo "$text" | sed -e 's/\([_\[\]()~`>#+=|{}.!-]\)/\\\1/g'
}

# Extract text content from xAI response (filter for message type, not tool calls)
SUMMARY_FILE="$TEMP_DIR/summary.txt"
FORMATTED_DATE=$(date -j -f "%Y-%m-%d" "$YESTERDAY" "+%B %d, %Y" 2>/dev/null || echo "$YESTERDAY")

# Header
cat > "$SUMMARY_FILE" << 'HEADER'
🤖 *AI News Daily*

HEADER
echo "📅 $FORMATTED_DATE" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Get text from message output (skip tool call outputs)
EXTRACTED_TEXT=$(jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | .text' "$XAI_RESPONSE" 2>/dev/null)
TTS_SOURCE=""

if [ -n "$EXTRACTED_TEXT" ] && [ "$EXTRACTED_TEXT" != "null" ]; then
    # Clean up the text for Telegram:
    # - Remove markdown citation links [[n]](url) notation
    # - Remove # headers and replace with emoji
    # - Remove [text](url) markdown links, keep just URL
    CLEAN_TEXT=$(echo "$EXTRACTED_TEXT" | \
        sed -E 's/\[\[[0-9]+\]\]\([^)]*\)//g' | \
        sed -E 's/\[([^]]+)\]\(([^)]+)\)/\1 \2/g' | \
        sed 's/^###* /🔹 /g' | \
        sed 's/^## /🔹 /g' | \
        sed 's/^# /🔹 /g' | \
        sed 's/\*\*\([^*]*\)\*\*/\*\1\*/g')

    echo "$CLEAN_TEXT" >> "$SUMMARY_FILE"
    TTS_SOURCE="$CLEAN_TEXT"

    # Extract source annotations (links to original posts)
    ANNOTATIONS=$(jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | .annotations[]? | .url // empty' "$XAI_RESPONSE" 2>/dev/null | sort -u)
    ANNOTATION_COUNT=$(echo "$ANNOTATIONS" | grep -c "http" 2>/dev/null || echo "0")

    if [ "$ANNOTATION_COUNT" -gt 0 ]; then
        echo "" >> "$SUMMARY_FILE"
        echo "━━━━━━━━━━━━━━━━━━━━" >> "$SUMMARY_FILE"
        echo "📎 *Sources* ($ANNOTATION_COUNT)" >> "$SUMMARY_FILE"
        echo "$ANNOTATIONS" | head -15 >> "$SUMMARY_FILE"
        log "Found $ANNOTATION_COUNT source links"
    else
        log "WARNING: No source annotations found in response"
    fi
else
    log "WARNING: No text content found in xAI response"
    jq '.' "$XAI_RESPONSE" >> "$SUMMARY_FILE"
fi

SUMMARY=$(cat "$SUMMARY_FILE")

if [ ${#SUMMARY} -lt 50 ]; then
    log "WARNING: Summary too short, might be incomplete"
fi

log "Summary generated (${#SUMMARY} chars)"

# Step 4: Generate voice narration
log "Generating voice narration with ElevenLabs..."

AUDIO_FILE="$TEMP_DIR/xai-news-summary.mp3"

# Truncate text for TTS (max ~1500 chars to avoid timeout)
MAX_TTS_CHARS=1500
if [ -z "$TTS_SOURCE" ]; then
    TTS_SOURCE="$SUMMARY"
fi

if [ ${#TTS_SOURCE} -gt $MAX_TTS_CHARS ]; then
    TTS_TEXT="${TTS_SOURCE:0:$MAX_TTS_CHARS}..."
    log "Truncating summary for TTS (${#TTS_SOURCE} -> $MAX_TTS_CHARS chars)"
else
    TTS_TEXT="$TTS_SOURCE"
fi

# Clean TTS text: only news title + description, no links/markdown/citations
TTS_CLEAN=$(echo "$TTS_TEXT" | \
    sed '/^🤖 /d' | \
    sed '/^📅 /d' | \
    sed '/^📎 /d' | \
    sed '/^━/d' | \
    sed '/^Sources/d' | \
    sed -E 's/\[\[[0-9]+\]\]\([^)]*\)//g' | \
    sed -E 's/\[[0-9]+\]//g' | \
    sed -E 's/\[([^]]+)\]\([^)]+\)/\1/g' | \
    sed -E 's|https://[^ ]*||g' | \
    sed -E 's|http://[^ ]*||g' | \
    sed -E 's|x\.com/[^ ]*||g' | \
    sed -E 's/^Posted by [^ -]+( \([^)]*\))? - //g' | \
    sed -E 's/\([^)]*[0-9][^)]*\)//g' | \
    sed -E 's/^🔹[[:space:]]*//g' | \
    sed -E 's/^[0-9]+\. //g' | \
    sed 's/[*_~`#]//g' | \
    sed 's/━//g' | \
    sed 's/🔗//g' | \
    tr -s ' ' | \
    tr -s '\n')

log "TTS text cleaned (${#TTS_CLEAN} chars)"

# Use sag CLI for TTS with faster model
# Use set +e to prevent script exit on TTS failure
set +e
echo "$TTS_CLEAN" | sag --model-id eleven_flash_v2_5 -o "$AUDIO_FILE" 2>&1
TTS_EXIT_CODE=$?
set -e

if [ $TTS_EXIT_CODE -ne 0 ] || [ ! -f "$AUDIO_FILE" ] || [ ! -s "$AUDIO_FILE" ]; then
    log "WARNING: Failed to generate voice narration (exit code: $TTS_EXIT_CODE), continuing without audio"
    AUDIO_FILE=""
else
    log "Audio generated: $AUDIO_FILE ($(stat -f%z "$AUDIO_FILE" 2>/dev/null || stat -c%s "$AUDIO_FILE" 2>/dev/null) bytes)"
fi

# Step 5: Send to Telegram
log "Sending to Telegram..."

# Send text message first (full summary without caption limit)
"$CLAWDBOT_BIN" message send --target "$TELEGRAM_CHAT_ID" --message "$SUMMARY" 2>&1
TEXT_RESULT=$?

if [ $TEXT_RESULT -eq 0 ]; then
    log "Text message sent successfully"
else
    log "ERROR: Failed to send text message to Telegram"
    exit 1
fi

# Send audio separately (avoids 1024 char caption limit)
if [ -n "$AUDIO_FILE" ] && [ -f "$AUDIO_FILE" ]; then
    "$CLAWDBOT_BIN" message send --target "$TELEGRAM_CHAT_ID" --message "🎙️ Audio summary" --media "$AUDIO_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "Audio sent successfully"
    else
        log "WARNING: Failed to send audio to Telegram"
    fi
fi

log "Successfully sent AI news summary to Telegram"

log "AI news daily summary completed successfully"
exit 0
