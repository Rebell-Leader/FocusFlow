# 🧪 FocusFlow Testing Checklist

## Quick Feature Verification Guide

### ✅ Pre-Flight Setup
- [ ] App starts without errors: `python app.py`
- [ ] MCP server URL appears: `http://localhost:5000/gradio_api/mcp/`
- [ ] Web UI loads at `http://localhost:5000`
- [ ] No Python errors in terminal

---

## 🎯 Tab 1: Home / Onboarding

### Project Onboarding Flow
- [ ] **Enter project description**: "Build a REST API for a todo app with user authentication"
- [ ] **Click "Generate Tasks"**
- [ ] **Verify**: 5-8 tasks appear in the output
- [ ] **Verify**: Tasks have titles, descriptions, and durations (15-30 mins)
- [ ] **Demo Mode Only**: Check if AI provider is Mock or Anthropic (shown in status)

**Expected Output Example:**
```
Task 1: Set up project structure
Task 2: Create user authentication endpoints
Task 3: Build todo CRUD operations
...
```

**Pass Criteria**: ✅ Tasks are generated and look relevant to the project

---

## 📋 Tab 2: Task Manager

### CRUD Operations

#### Create Task
- [ ] Click **"➕ Add Task"** button
- [ ] **Verify**: Form appears with Title, Description, Duration, Status fields
- [ ] **Fill in**: Title="Write unit tests", Description="Add pytest tests", Duration=25, Status="Todo"
- [ ] Click **"💾 Save"**
- [ ] **Verify**: Form collapses
- [ ] **Verify**: New task appears in task list below

#### Read Tasks
- [ ] **Verify**: Task list shows all tasks with ID, Title, Description, Duration, Status
- [ ] **Verify**: Progress bar shows percentage (e.g., "33% complete")

#### Update Task
- [ ] Click **"✏️"** (Edit) button on any task
- [ ] **Verify**: Form pre-fills with task data
- [ ] **Change**: Status to "In Progress"
- [ ] Click **"💾 Save"**
- [ ] **Verify**: Task status updates in list
- [ ] **Verify**: Progress bar percentage updates

#### Delete Task
- [ ] Click **"🗑️"** (Delete) button on any task
- [ ] **Verify**: Task disappears from list
- [ ] **Verify**: Progress bar percentage updates

#### Start Task (Active Task)
- [ ] Click **"▶️"** (Start) button on a task
- [ ] **Verify**: Task status changes to "In Progress"
- [ ] **Verify**: "Currently Working On" section shows the task details
- [ ] **Verify**: Only one task can be active at a time

**Pass Criteria**: ✅ All CRUD operations work without errors

---

## 👁️ Tab 3: Monitor

### Focus Monitoring

#### Demo Mode Test
- [ ] **Verify**: "Demo Workspace" text area is visible
- [ ] **Type**: "Working on authentication endpoints, created login route"
- [ ] Click **"🔍 Check Focus Now"**
- [ ] **Verify**: Focus check result appears (On Track, Distracted, or Idle)
- [ ] **Verify**: Duolingo-style message appears (e.g., "Great work! You're making solid progress! 🎯")
- [ ] **Verify**: Check is logged to history below

#### Distraction Detection
- [ ] **Clear text area**
- [ ] **Type**: "Checking Reddit and browsing Twitter"
- [ ] Click **"🔍 Check Focus Now"**
- [ ] **Verify**: Status shows "Distracted"
- [ ] **Verify**: Browser notification appears (if permissions enabled)
- [ ] **Verify**: Alert message is appropriately stern

#### Idle Detection
- [ ] **Clear text area** (leave empty)
- [ ] Click **"🔍 Check Focus Now"**
- [ ] **Verify**: Status shows "Idle"
- [ ] **Verify**: Message nudges to get back to work

#### Auto-Monitoring
- [ ] Click **"▶️ Start Monitoring"**
- [ ] **Verify**: Button changes to "⏸️ Pause Monitoring"
- [ ] **Wait**: 30 seconds (or check interval)
- [ ] **Verify**: New focus check appears automatically
- [ ] Click **"⏸️ Pause Monitoring"**
- [ ] **Verify**: Auto-checks stop

**Pass Criteria**: ✅ All three verdicts (On Track, Distracted, Idle) can be triggered

---

## 📊 Tab 4: Dashboard

### Metrics Visualization

#### Initial State (No Data)
- [ ] Click **Dashboard** tab
- [ ] **Verify**: Focus Score shows 0
- [ ] **Verify**: Current Streak shows 0
- [ ] **Verify**: Total Checks shows 0
- [ ] **Verify**: Charts render (even if empty)

#### After Focus Checks
- [ ] Go to **Monitor** tab
- [ ] Perform 3-5 focus checks with different results (On Track, Distracted, Idle)
- [ ] Return to **Dashboard** tab
- [ ] Click **"🔄 Refresh Dashboard"**
- [ ] **Verify**: Focus Score updates (0-100 range)
- [ ] **Verify**: Streak increases with consecutive "On Track" checks
- [ ] **Verify**: Total Checks shows correct count
- [ ] **Verify**: "Focus States Distribution" bar chart shows data
- [ ] **Verify**: Data matches actual check results

#### Weekly Trends
- [ ] **Verify**: "Weekly Focus Score Trend" line chart appears
- [ ] **Note**: May be empty if no historical data exists (expected on first run)

**Pass Criteria**: ✅ Dashboard updates after focus checks and shows accurate metrics

---

## 🍅 Tab 5: Pomodoro Timer

### Timer Functionality

#### Work Session
- [ ] Click **"▶️ Start Work Session"**
- [ ] **Verify**: Button changes to "⏸️ Pause"
- [ ] **Verify**: Timer counts down from 25:00
- [ ] **Verify**: Timer updates every second
- [ ] Click **"⏸️ Pause"**
- [ ] **Verify**: Timer stops counting
- [ ] Click **"▶️ Resume"**
- [ ] **Verify**: Timer continues from paused time

#### Reset Timer
- [ ] Click **"🔄 Reset"**
- [ ] **Verify**: Timer returns to 25:00
- [ ] **Verify**: Mode shows "Work Session"

#### Break Session
- [ ] Click **"☕ Start Break"**
- [ ] **Verify**: Timer sets to 5:00
- [ ] **Verify**: Mode shows "Break Time"
- [ ] **Verify**: Timer counts down

#### Timer Completion
- [ ] **Option A**: Wait for timer to reach 0:00 (25 minutes)
- [ ] **Option B**: Manually edit timer in browser dev tools
- [ ] **Verify**: Audio alert plays (ding sound)
- [ ] **Verify**: Browser notification appears (if enabled)

**Pass Criteria**: ✅ Timer starts/pauses/resets, audio plays on completion

---

## 🔗 MCP Integration Tests

### Prerequisites
- [ ] Claude Desktop installed
- [ ] `claude_desktop_config.json` configured with FocusFlow MCP server
- [ ] Claude Desktop restarted

### MCP Tools (via Claude Desktop)

#### Test 1: add_task
- [ ] Open Claude Desktop
- [ ] **Type**: "Add a task to implement OAuth2 authentication with 45 minute duration"
- [ ] **Verify**: Claude confirms task was added
- [ ] **Verify**: Task appears in FocusFlow Task Manager tab

#### Test 2: get_current_task
- [ ] In Claude: "What task should I work on now?"
- [ ] **Verify**: Claude returns the current active task details

#### Test 3: start_task
- [ ] In Claude: "Start task 2"
- [ ] **Verify**: Claude confirms task started
- [ ] **Verify**: Task shows as "In Progress" in FocusFlow UI

#### Test 4: mark_task_done
- [ ] In Claude: "Mark task 1 as done"
- [ ] **Verify**: Claude confirms completion
- [ ] **Verify**: Task shows as "Done" in FocusFlow UI
- [ ] **Verify**: Progress bar updates

#### Test 5: get_all_tasks
- [ ] In Claude: "Show me all my tasks"
- [ ] **Verify**: Claude lists all tasks with IDs and statuses

#### Test 6: get_productivity_stats
- [ ] In Claude: "How productive have I been today?"
- [ ] **Verify**: Claude returns focus score, streak, task completion rate

#### Test 7: delete_task
- [ ] In Claude: "Delete task 3"
- [ ] **Verify**: Claude confirms deletion
- [ ] **Verify**: Task removed from FocusFlow UI

#### Test 8: Error Handling
- [ ] In Claude: "Mark task 999 as done"
- [ ] **Verify**: Claude returns helpful error message (task not found)

### MCP Resources

#### Test 1: focusflow://tasks/all
- [ ] In Claude: "Read focusflow://tasks/all"
- [ ] **Verify**: Returns complete task list JSON

#### Test 2: focusflow://tasks/active
- [ ] In Claude: "Read focusflow://tasks/active"
- [ ] **Verify**: Returns current active task JSON

#### Test 3: focusflow://stats
- [ ] In Claude: "Read focusflow://stats"
- [ ] **Verify**: Returns productivity statistics JSON

**Pass Criteria**: ✅ All MCP tools and resources work through Claude Desktop

---

## 🎨 Demo Mode vs Local Mode

### Demo Mode (LAUNCH_MODE=demo)
- [ ] **Verify**: "Demo Workspace" text area visible in Monitor tab
- [ ] **Verify**: No file system watching messages
- [ ] **Verify**: Works without local file access

### Local Mode (LAUNCH_MODE=local)
- [ ] Set `LAUNCH_MODE=local` in environment
- [ ] Restart app
- [ ] **Verify**: Monitor tab shows "Watching directory" message
- [ ] **Verify**: File changes trigger automatic focus checks
- [ ] **Create/edit file** in project directory
- [ ] **Verify**: Focus check triggered automatically

**Pass Criteria**: ✅ Both modes work correctly

---

## 🤖 AI Provider Tests

### Mock AI (No API Keys)
- [ ] **Unset** all AI provider keys
- [ ] Restart app
- [ ] **Verify**: Status shows "Mock AI (Demo Mode)"
- [ ] **Verify**: Onboarding generates tasks (keyword-based)
- [ ] **Verify**: Focus checks cycle through verdicts

### Anthropic Claude (With API Key)
- [ ] Set `ANTHROPIC_API_KEY` or `DEMO_ANTHROPIC_API_KEY`
- [ ] Set `AI_PROVIDER=anthropic`
- [ ] Restart app
- [ ] **Verify**: Status shows "Anthropic Claude"
- [ ] **Verify**: Onboarding generates intelligent, context-aware tasks
- [ ] **Verify**: Focus checks provide detailed, relevant feedback

### OpenAI GPT-4 (With API Key)
- [ ] Set `OPENAI_API_KEY`
- [ ] Set `AI_PROVIDER=openai`
- [ ] Restart app
- [ ] **Verify**: Status shows "OpenAI GPT-4"
- [ ] **Verify**: All AI features work correctly

**Pass Criteria**: ✅ All AI providers work, graceful fallback to Mock

---

## 📊 Final Checks

### Data Persistence
- [ ] Create tasks, perform focus checks
- [ ] Close browser
- [ ] **Verify**: `focusflow.db` file exists
- [ ] Restart app
- [ ] **Verify**: All tasks and metrics persist

### Browser Compatibility
- [ ] Test in Chrome/Chromium
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] **Verify**: UI renders correctly in all browsers

### Mobile Responsiveness
- [ ] Open on mobile device or resize browser to mobile width
- [ ] **Verify**: UI adapts reasonably well

---

## 🏆 Success Criteria

All features pass if:
- ✅ No errors in console/logs
- ✅ All CRUD operations work
- ✅ Focus monitoring triggers all 3 verdicts
- ✅ Dashboard shows accurate metrics
- ✅ Pomodoro timer functions correctly
- ✅ MCP tools work through Claude Desktop
- ✅ Demo mode works without API keys
- ✅ Data persists across restarts

---

## 🐛 Bug Reporting Template

If you find issues, document them:

**Bug**: [Brief description]  
**Steps to Reproduce**: [1. Click X, 2. Enter Y, 3. ...]  
**Expected**: [What should happen]  
**Actual**: [What actually happened]  
**Environment**: [Demo/Local mode, AI provider, browser]  
**Severity**: [Critical/High/Medium/Low]
