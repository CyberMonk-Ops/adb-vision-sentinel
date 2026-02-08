# Sentinel: Autonomous Cross-Platform Agent 🤖👁️

> **"If your robot hits a wall, I probably predicted it."**

Sentinel is a **Computer Vision-guided Robotic Process Automation (RPA) agent** designed to navigate and interact with complex social platforms (LinkedIn, Instagram, X) on Android. Unlike traditional bots that rely on brittle API injection or web scraping, Sentinel operates entirely on the **Physical Layer** via ADB (Android Debug Bridge), simulating human bio-mechanics and decision-making.

---

## 🧠 Core Architecture

Sentinel follows a strict **See-Think-Act** loop, mirroring autonomous robotics control systems:

* **👁️ Perception (The Eyes):**
    * **XML Parsing:** Real-time DOM analysis of Android UI hierarchies to identify interactive elements (Buttons, TextFields) without relying on static coordinates.
    * **OCR / Text Extraction:** Scrapes semantic content (Post text, Job descriptions) to feed the cognitive engine.
    * **Dynamic Anchoring:** Uses relative spatial logic (e.g., "The Like button is 50px below the Post Text") to adapt to UI updates automatically.

* **🧠 Cognition (The Brain):**
    * **Local LLM Integration:** Processes screen content to generate context-aware, persona-driven responses.
    * **Persona Engine:** Currently running the "Cynical Engineer" profile—skeptical of buzzwords, focused on first-principles engineering (e.g., asking about battery density on robotics posts).
    * **Turing-Test Evasion:** Intentionally imperfect grammar and "human-like" skepticism to bypass bot detection filters.

* **🦾 Actuation (The Hands):**
    * **Stochastic Motion Planning:** Implements randomized "Human Jitter," variable scroll speeds, and non-linear swipe curves to defeat behavioral biometrics.
    * **ADB Input Bridge:** Direct shell command execution for low-latency taps and swipes.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Interface:** ADB (Android Debug Bridge)
* **Vision:** `xml.etree.ElementTree` (DOM Parsing)
* **Logic:** Custom Stochastic State Machine
* **Hardware Target:** Android 11+ (Emulated or Physical Device)

---

## 🚀 Key Features

* **Universal Compatibility:** Works on LinkedIn, Instagram, and X (Twitter) with minimal configuration changes.
* **Anti-Detection:**
    * Randomized sleep intervals (Poisson distribution).
    * "Drift" in tap coordinates (never taps the exact same pixel twice).
*
