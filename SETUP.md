# Fast Setup Scroll

A step-by-step scroll to get **rattleGRIMOIRE** running on your computer.
No prior magic required.

---

## What You Will Need

Before you begin the ritual, gather the following:

1. **A computer** running Windows, macOS, or Linux
2. **An internet connection** (for summoning dependencies)
3. **A Rattle API key** (provided by your Rattle archmage)
4. **An AI provider key** (optional — only needed for casting AI spells)

---

## Step 1: Install Python

rattleGRIMOIRE requires **Python 3.10 or newer**.

### Check if Python is already installed

Open a terminal (see below) and type:

```
python3 --version
```

If you see something like `Python 3.12.4`, you are ready — skip to **Step 2**.

If you get an error like `command not found`, install Python first.

### How to open a terminal

| Operating System | How to Open |
|---|---|
| **Windows** | Press `Win + R`, type `cmd`, press Enter. Or search for "Command Prompt" in the Start menu. |
| **macOS** | Press `Cmd + Space`, type `Terminal`, press Enter. |
| **Linux** | Press `Ctrl + Alt + T`, or find "Terminal" in your applications menu. |

### Install Python

| Operating System | Instructions |
|---|---|
| **Windows** | Go to https://www.python.org/downloads/ and click the big yellow "Download Python" button. **Important:** During installation, check the box that says "Add Python to PATH". |
| **macOS** | Go to https://www.python.org/downloads/ and download the macOS installer. Run it and follow the prompts. |
| **Linux** | Run: `sudo apt update && sudo apt install python3 python3-pip python3-venv` (Ubuntu/Debian) or `sudo dnf install python3 python3-pip` (Fedora). |

After installing, close and reopen your terminal, then verify:

```
python3 --version
```

> **Windows note:** On Windows, you may need to use `python` instead of `python3`
> throughout this scroll. Try both and use whichever works.

---

## Step 2: Summon rattleGRIMOIRE

### Option A: Download as ZIP (easiest)

1. Go to https://github.com/mngapps/rattleGRIMOIRE
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to a folder you can find easily (e.g., your Desktop or Documents)

### Option B: Clone with Git (if you have Git installed)

```
git clone https://github.com/mngapps/rattleGRIMOIRE.git
```

### Navigate into the folder

In your terminal, navigate to the folder you just summoned:

```
cd rattleGRIMOIRE
```

> **Tip:** On Windows, you can type `cd ` (with a space) and then drag the
> folder from File Explorer into the terminal window to paste the path.

---

## Step 3: Prepare the Sanctum (Virtual Environment)

A virtual environment is a warded circle that keeps the Grimoire's dependencies
separate from other Python projects on your computer. This is a one-time ritual.

```
python3 -m venv .venv
```

Now activate the circle:

| Operating System | Command |
|---|---|
| **macOS / Linux** | `source .venv/bin/activate` |
| **Windows (Command Prompt)** | `.venv\Scripts\activate` |
| **Windows (PowerShell)** | `.venv\Scripts\Activate.ps1` |

After activation, your terminal prompt will show `(.venv)` at the beginning.
This means the sanctum is open.

> **Important:** You need to re-enter the sanctum every time you open a new
> terminal window before casting spells. Just run the activate command again.

---

## Step 4: Bind the Grimoire

Run this single incantation to install everything:

```
pip install -e ".[all-ai]"
```

Wait for the binding to finish. You will see a success message at the end.
This installs rattleGRIMOIRE together with all supported AI sigils
(OpenAI, Anthropic) so you can switch between them freely without re-binding.

---

## Step 5: Inscribe Your Sigils

### 5a: Create your `.env` scroll

```
cp .env.example .env
```

> **Windows (Command Prompt):** Use `copy .env.example .env` instead.

### 5b: Open the scroll in an editor

Open the `.env` file in any text editor:

| Operating System | Command |
|---|---|
| **Windows** | `notepad .env` |
| **macOS** | `open -e .env` |
| **Linux** | `nano .env` or `xdg-open .env` |

### 5c: Etch your Rattle API key

Find this line in the scroll:

```
RATTLE_API_KEY_ACME=your-api-key-here
```

Replace `your-api-key-here` with the API key you received from your Rattle
archmage. Replace `ACME` with your tenant name (in UPPERCASE):

```
RATTLE_API_KEY_MYCOMPANY=abc123-your-real-key-here
```

> **What is a tenant?** A tenant is your company or workspace name in Rattle.
> The part after `RATTLE_API_KEY_` becomes the name you use on the command line.
> For example, `RATTLE_API_KEY_MYCOMPANY=...` means you will use `mycompany`
> as the tenant name in commands.

### 5d: Etch your AI provider key (if casting AI spells)

Find the AI provider section and fill in the key for your chosen sigil:

**For OpenAI:**
```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

**For Anthropic:**
```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

**For Ollama (free, runs locally — no API key needed):**
```
AI_PROVIDER=ollama
```

### 5e: Save and close the scroll

---

## Step 6: Test the Binding

Verify the pact by running the connection test. Replace `mycompany`
with the tenant name you configured in Step 5c:

```
rattle mycompany test-connection
```

If the binding is true, you will see:

```
Connection OK for tenant 'mycompany'
```

### Troubleshooting

| Omen | Counter-ritual |
|---|---|
| `command not found: rattle` | Make sure your sanctum is active (Step 3). |
| `Unknown tenant 'mycompany'` | Check that `RATTLE_API_KEY_MYCOMPANY=...` is in your `.env` scroll and the key is correct. |
| `Connection FAILED` | Verify your API key is correct and you have internet access. |

---

## Step 7: Cast Your First Spell

Once the binding test passes, try an AI-powered incantation:

```bash
# Conjure product descriptions in German
rattle mycompany ai-describe --limit 3 --language de

# Classify products into hidden orders
rattle mycompany ai-classify --limit 5

# Divine insights about your product data
rattle mycompany ai-analyse --question "Which products have no description?"

# See which sigils are currently available
rattle mycompany ai-providers
```

---

## Quick Reference

### Spells you will cast often

| What you want to do | Incantation |
|---|---|
| Test the binding | `rattle <tenant> test-connection` |
| Conjure product descriptions | `rattle <tenant> ai-describe --limit 5` |
| Classify products | `rattle <tenant> ai-classify --limit 10` |
| Transmute data formats | `rattle <tenant> ai-transform datanorm rattle data.json` |
| Divine product data | `rattle <tenant> ai-analyse --question "your question"` |
| List available AI sigils | `rattle <tenant> ai-providers` |
| Reveal local data scrolls | `rattle <tenant> list-sources` |

Replace `<tenant>` with your tenant name (e.g., `mycompany`).

### Starting a new terminal session

Every time you open a new terminal, you need to:

1. Navigate to the Grimoire folder: `cd path/to/rattleGRIMOIRE`
2. Re-enter the sanctum:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`

Then you can cast `rattle` spells as normal.

---

## Getting Help

- Run `rattle --help` to see all available spells
- Run `rattle <tenant> <command> --help` to see options for a specific spell
- Report omens at https://github.com/mngapps/rattleGRIMOIRE/issues
