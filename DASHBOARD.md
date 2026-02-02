# Web Dashboard

AI Digest includes a modern, responsive web dashboard that provides complete control over all system features without using the CLI. Access the dashboard directly in your browser to manage digests, configure adapters, set schedules, and monitor system status.

## Table of Contents

- [Quick Start](#quick-start)
- [Dashboard Overview](#dashboard-overview)
- [Features](#features)
- [Dashboard Tabs](#dashboard-tabs)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Access the Dashboard

1. **Start the Flask server:**
   ```bash
   python src/server.py
   ```

2. **Open your browser to:**
   ```
   http://localhost:5000
   ```

The dashboard loads automatically. No additional setup required.

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Network connection to localhost:5000

## Dashboard Overview

The dashboard is organized into 8 main tabs:

1. **📊 Overview** - System status and quick actions
2. **⚙️ Pipeline** - Run digests manually
3. **🕐 Schedule** - Configure automated scheduling
4. **📧 Delivery** - Set up email and Telegram delivery
5. **🔔 Webhooks** - Configure Slack, Discord, and HTTP webhooks
6. **🔌 Adapters** - Enable/disable content sources
7. **📝 Logging** - Configure logging settings
8. **📚 Digests** - Browse digest history

## Features

### Real-time System Status
- Server health indicator (green/red dot)
- Live activity log showing all actions
- Auto-refresh every 30 seconds
- One-click status refresh

### Configuration Management
- Update settings without restarting server
- Instant feedback on configuration changes
- Validation with helpful error messages
- All changes persisted to `config.json`

### Pipeline Execution
- Run digest generation on demand
- Optional automatic delivery
- Progress tracking and status messages
- No CLI required

### Scheduler Control
- Set daily digest time (hour and minute in UTC)
- Start/stop scheduler from dashboard
- View active scheduled jobs
- Automatic delivery toggle

### Delivery Configuration
- Enable/disable email delivery
- Enter recipient email address
- Telegram chat ID configuration
- Settings saved immediately

### Adapter Management
- Visual cards for each content adapter (Reddit, RSS, etc.)
- Toggle adapters on/off with single click
- View adapter-specific settings
- Status indicators (enabled/disabled)

### Logging Control
- Change log level without restart
- Toggle file and console output
- Real-time effect
- Monitor logging configuration

### Digest History
- Browse all generated digests
- View creation time and duration
- Delete unwanted digests
- Pagination support

## Dashboard Tabs

### 📊 Overview Tab

**Purpose:** Quick system status and common actions

**Contents:**
- **System Status Card** - Scheduler running status, active jobs, delivery status, log level
- **Quick Actions** - Run pipeline, refresh status buttons
- **Activity Log** - Real-time log of all dashboard actions (last 50 entries)

**Common Actions:**
- Run a manual digest immediately
- Check if scheduler is running
- Monitor recent activity

### ⚙️ Pipeline Tab

**Purpose:** Execute digest generation manually

**Features:**
- **Deliver After Generation** - Checkbox to enable automatic delivery
- **Execute Pipeline Now** - Large blue button to trigger pipeline
- **Status Message** - Shows success/error from execution
- **Pipeline Information** - System info about pipeline version and status

**Use Cases:**
- Test digest generation before scheduling
- Generate digests on demand
- Verify adapter configurations work
- Deliver digests outside scheduled time

**Example:**
1. Check the "Deliver after generation" checkbox
2. Click "Execute Pipeline Now"
3. Wait for success message (2-5 seconds)
4. Check your email/Telegram for the digest

### 🕐 Schedule Tab

**Purpose:** Configure automated daily digest generation

**Controls:**
- **Hour** - Set UTC hour (0-23)
- **Minute** - Set UTC minute (0-59)
- **Deliver Automatically** - Checkbox
- **Save Schedule** - Persists settings
- **Start/Stop Scheduler** - Control scheduler execution

**Current Status:**
- Shows if scheduler is running
- Displays current schedule time
- Lists active scheduled jobs

**Use Cases:**
- Schedule daily 6 AM digest (6:00 UTC)
- Generate at different time
- Enable/disable automatic delivery
- Monitor scheduled jobs

**Example - Set Daily 8 AM UTC Digest:**
1. Set Hour to: 8
2. Set Minute to: 0
3. Check "Deliver Automatically"
4. Click "Save Schedule"
5. Click "Start" button
6. Scheduler will run daily at 8 AM UTC

**Timezone Conversion:**
- UTC 6 AM = EST 1 AM / PST 10 PM (previous day)
- UTC 8 AM = EST 3 AM / PST 12 AM / CET 10 AM
- UTC 12 PM = EST 7 AM / PST 4 AM / CET 2 PM
- UTC 8 PM = EST 3 PM / PST 12 PM / CET 8 PM

### 📧 Delivery Tab

**Purpose:** Configure how digests are delivered

**Email Settings:**
- **Enable Email** - Checkbox to activate email delivery
- **Email Address** - Input field for recipient (e.g., user@example.com)

**Telegram Settings:**
- **Enable Telegram** - Checkbox to activate Telegram delivery
- **Chat ID** - Your Telegram chat ID

**Getting Telegram Chat ID:**
1. Start a chat with [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. Bot replies with your chat ID
4. Copy and paste into the Chat ID field

**Save Process:**
1. Configure your preferences
2. Click "Save Settings"
3. Success message appears
4. Settings take effect immediately

**Validation:**
- Email address format is validated
- Chat ID should be numeric
- At least one delivery method recommended

### � Webhooks Tab

**Purpose:** Configure webhook notifications to external services

**Supported Services:**
- **Slack** - Send formatted messages to Slack channels
- **Discord** - Send embedded messages to Discord channels
- **Generic** - Send JSON payloads to any HTTP endpoint

**Webhook List (Left Panel):**
- All configured webhooks with status indicators
- **Edit** - Modify webhook settings
- **Test** - Send test notification immediately
- **Enable/Disable** - Toggle webhook without deleting
- **Delete** - Remove webhook permanently

**Create/Edit Form (Right Panel):**
- **ID** - Unique webhook identifier (required, immutable after creation)
- **Name** - Human-readable webhook name (required)
- **Type** - Select: slack, discord, or generic (required)
- **URL** - Webhook endpoint URL (required, HTTPS recommended)
- **Headers** - Optional custom HTTP headers (JSON format)
- **Payload Template** - Optional JSON overlay for custom fields

**Common Actions:**
1. Create Slack webhook → Enter Slack incoming webhook URL
2. Test webhook → Click **Test** button, check external service
3. Edit webhook → Click **Edit**, modify fields, click **Save Changes**
4. Disable temporarily → Click **Disable** (re-enable anytime)
5. Delete webhook → Click **Delete**, confirm in dialog

**Integration:**
- Webhooks trigger automatically on digest delivery
- Multiple webhooks send in parallel
- Success/failure logged to activity log
- Metrics tracked: `trigger_count`, `last_triggered_at`

**Documentation:** See [WEBHOOKS.md](WEBHOOKS.md) for detailed setup guides and examples

### �🔌 Adapters Tab

**Purpose:** Manage content source adapters

**Visual Layout:**
- Adapter cards arranged in a responsive grid
- Color-coded borders (green=enabled, gray=disabled)
- Toggle switches on each card
- Adapter-specific settings displayed

**Available Adapters:**
- **Reddit** - Subreddit aggregation
- **RSS** - RSS feed sources
- **ProductHunt** - Product discoveries
- **IndieHackers** - Startup updates
- **HackerNews** - Tech news
- **Twitter/X** - Tweet aggregation
- **ArXiv** - Research papers

**Actions:**
1. Click the toggle switch to enable/disable
2. View adapter settings in JSON format
3. Settings persist immediately
4. Disabled adapters are skipped during pipeline run

**Customization:**
Edit `config.json` directly for advanced adapter settings:
```json
{
  "reddit": {
    "enabled": true,
    "settings": {
      "subreddits": ["python", "programming"],
      "limit": 20,
      "time_filter": "day"
    }
  }
}
```

### 📝 Logging Tab

**Purpose:** Configure system logging behavior

**Settings:**
- **Log Level** - Dropdown: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Write to File** - Enable/disable file logging
- **Console Output** - Enable/disable console output
- **File Path** - Display of log file location

**Log Levels Explained:**
- **DEBUG** - Very detailed, for development/troubleshooting
- **INFO** - Normal operations, important events
- **WARNING** - Potential issues, missing configs
- **ERROR** - Failures that affected functionality
- **CRITICAL** - System cannot continue

**Use Cases:**
- Set to DEBUG to troubleshoot issues
- Set to WARNING for production (less noise)
- Enable file logging to review past events
- Disable console for cleaner output

**Log File Location:**
```
logs/ai_digest.log
```

Logs are rotated when they reach 10MB (5 backups kept).

### 📚 Digests Tab

**Purpose:** Browse and manage generated digests

**Controls:**
- **Limit** - Number of digests to show (1-100)
- **Offset** - Pagination offset (0 = first page)
- **Load Digests** - Fetch list with current settings

**Digest Information:**
- Digest ID (format: YYYYMMDD_HHMMSS)
- Generation timestamp
- Execution duration in seconds

**Actions Per Digest:**
- **View** - See digest content
- **Delete** - Remove digest permanently

**Pagination Example:**
- First page: limit=10, offset=0
- Second page: limit=10, offset=10
- Third page: limit=10, offset=20

## Common Tasks

### Task 1: Configure Email Delivery

**Objective:** Receive digests by email

**Steps:**
1. Go to **📧 Delivery** tab
2. Check "Enable Email"
3. Enter your email address (e.g., john@example.com)
4. Click "Save Settings"
5. Verify success message appears
6. Test with Pipeline tab → "Execute Pipeline Now"

**Requirements:**
- Gmail App Password (if using Gmail)
- SMTP credentials in environment variables or .env file

### Task 2: Schedule Daily Digest at 9 AM UTC

**Objective:** Automatic digest every morning

**Steps:**
1. Go to **🕐 Schedule** tab
2. Set Hour to: 9
3. Set Minute to: 0
4. Check "Deliver Automatically"
5. Click "Save Schedule"
6. Click "Start" button (green)
7. Verify "Scheduler Status" shows running

**Verification:**
- Status shows "✅ Running"
- View active jobs listed
- Check back at 9 AM UTC for digest

### Task 3: Enable Reddit Adapter

**Objective:** Add Reddit content to digests

**Steps:**
1. Go to **🔌 Adapters** tab
2. Find "reddit" card
3. Click the toggle switch to turn on
4. Card border changes from gray to green
5. Test with **⚙️ Pipeline** → "Execute Pipeline Now"

**Optional - Customize Subreddits:**
1. Edit `config.json`:
   ```json
   {
     "adapters": {
       "reddit": {
         "enabled": true,
         "settings": {
           "subreddits": ["python", "programming", "machinelearning"],
           "limit": 30,
           "time_filter": "week"
         }
       }
     }
   }
   ```
2. Restart server or run pipeline again

### Task 4: Change Log Level for Debugging

**Objective:** Get detailed logs for troubleshooting

**Steps:**
1. Go to **📝 Logging** tab
2. Change "Log Level" dropdown from INFO to DEBUG
3. Click "Save Settings"
4. Go to **⚙️ Pipeline** tab
5. Click "Execute Pipeline Now"
6. Check `logs/ai_digest.log` for detailed output

**View Logs:**
```bash
tail -f logs/ai_digest.log
```

### Task 5: Delete Old Digests

**Objective:** Clean up digest history

**Steps:**
1. Go to **📚 Digests** tab
2. Click "Load Digests" (shows most recent first)
3. Find digest to delete
4. Click "Delete" button
5. Confirm deletion when prompted
6. Digest removed from history

## Troubleshooting

### Dashboard Won't Load

**Issue:** Page shows blank or "Cannot reach server"

**Solutions:**
1. Check Flask server is running:
   ```bash
   python src/server.py
   ```
2. Verify URL is correct: `http://localhost:5000`
3. Check firewall allows localhost:5000
4. Try different browser
5. Clear browser cache (Ctrl+Shift+Delete)

### Settings Won't Save

**Issue:** "Save Settings" button clicked but no success message

**Solutions:**
1. Check browser console for errors (F12)
2. Verify Flask server is running
3. Check for validation errors in form
4. Review error message in status box
5. Check network tab in browser dev tools

### Scheduler Won't Start

**Issue:** "Start" button doesn't work or shows error

**Solutions:**
1. Check if scheduler is already running
2. Click "Stop" first, then "Start"
3. Check log level set to INFO or higher
4. Verify system time is correct (scheduler uses UTC)
5. Check server logs: `tail -f logs/ai_digest.log`

### Delivery Not Working

**Issue:** Digests generated but not delivered

**Solutions:**
1. **Email:** Verify email is enabled and address is correct
2. **Telegram:** Confirm Chat ID from @userinfobot
3. Check credentials in `.env` file
4. Test with **⚙️ Pipeline** tab first
5. Review `logs/ai_digest.log` for delivery errors

### Adapters Not Producing Content

**Issue:** Enabled adapters but no content in digest

**Solutions:**
1. Check adapter is enabled (green border in Adapters tab)
2. Verify API credentials (.env file or config)
3. Test with "Execute Pipeline" button
4. Check adapter-specific settings in config.json
5. Review logs for adapter errors

### Performance Issues

**Issue:** Dashboard is slow or freezes

**Solutions:**
1. Reduce "Limit" in Digests tab (fewer items to load)
2. Close other browser tabs
3. Restart Flask server: `Ctrl+C` then run again
4. Check server logs for errors
5. Try different browser or incognito mode

### Browser Compatibility

**Supported Browsers:**
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Required:**
- JavaScript enabled
- Cookies enabled
- Modern CSS support

## Keyboard Shortcuts

Coming in future version - can already navigate with Tab key.

## Mobile Support

The dashboard is responsive and works on tablets and large phones:
- Touch-friendly buttons
- Responsive grid layout
- Mobile-optimized navigation

**Best Experience:** Desktop browser (1024px+ width)

## Advanced Usage

### Direct API Access

The dashboard is built on REST APIs. You can also call them directly:

```bash
# Get current configuration
curl http://localhost:5000/api/config

# Update scheduler
curl -X POST http://localhost:5000/api/config/scheduler \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"hour":9,"minute":0,"delivery_enabled":true}'

# Run pipeline
curl -X POST http://localhost:5000/api/pipeline/run \
  -d '{"deliver":true}'
```

See [API.md](API.md) for complete REST reference.

### Automating Dashboard Tasks

Use browser DevTools Console to automate:

```javascript
// Run pipeline
await API.runPipeline(true);

// Get current config
const config = await API.getConfig();

// Update scheduler
await API.updateSchedulerConfig({
    enabled: true,
    hour: 9,
    minute: 0,
    delivery_enabled: true
});
```

## Appearance & Customization

The dashboard uses a professional light theme with:
- Blue primary color (#2563eb)
- Responsive grid layouts
- Accessible contrast ratios
- Hover effects on interactive elements

### Customizing Colors

Edit `static/style.css` to change color scheme:

```css
:root {
    --primary-color: #2563eb;      /* Main blue */
    --success-color: #059669;       /* Green */
    --danger-color: #dc2626;        /* Red */
    /* ... other colors ... */
}
```

## Security Notes

- Dashboard runs on localhost only by default
- No authentication required (add if needed)
- All API calls are HTTP (use HTTPS in production)
- Credentials stored in environment variables, not dashboard

### For Production Deployment

1. Use HTTPS/SSL certificates
2. Add API authentication (JWT/API keys)
3. Implement rate limiting
4. Use reverse proxy (nginx)
5. Add access logs

## Support & Feedback

For issues, questions, or feature requests:
- Check [Troubleshooting](#troubleshooting) section
- Review server logs: `logs/ai_digest.log`
- Check [API.md](API.md) for REST API details
- Review [CONFIGURATION.md](CONFIGURATION.md) for settings

---

**Version:** 0.1.0  
**Last Updated:** 2024  
**See Also:** [API.md](API.md), [CONFIGURATION.md](CONFIGURATION.md), [DEPLOYMENT.md](DEPLOYMENT.md)
