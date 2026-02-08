
import time
import subprocess
from ppadb.client import Client as AdbClient
import random
import os
import xml.etree.ElementTree as ET
from ppadb.client import Client as AdbClient


import brain

# --- CONFIGURATION ---
# ADB runs on port 5037 by default
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037

# App Package Names (The "DNA" of the apps)
APPS = {
    "instagram": "com.instagram.android",
    "linkedin": "com.linkedin.android",
    "whatsapp": "com.whatsapp",
    "twitter" : "com.twitter.android"
}

class SentinelMotor:
    def __init__(self):
        print("[*] Initializing Sentinel Motor Cortex...")
        self.client = AdbClient(host=ADB_HOST, port=ADB_PORT)
        self.device = self._get_device()

        self.anchor_y = 800

    def _get_device(self):
        """Finds the connected vessel."""
        devices = self.client.devices()
        if not devices:
            print("[!] CRITICAL: No device found. Is the cable plugged in?")
            print("[!] HINT: Run 'adb devices' in terminal to check.")
            exit(1)
        
        device = devices[0]
        print(f"[*] Connected to Vessel: {device.serial}")
        return device

    def wake_up0(self):
        """Wakes the screen if it's sleeping."""
        print("[*] Sending Wake Signal...")
        if not self.device.is_screen_on():
            self.device.shell("input keyevent 26") # Power Button
            time.sleep(1)
            self.device.shell("input keyevent 82") # Unlock/Menu
            print("[*] Screen is AWAKE.")
        else:
            print("[*] Screen was already awake.")


    def wake_up(self):
        """Wakes the screen using raw system dumps."""
        print("[*] Checking screen state...")
        
        # We ask Android: "Are you awake?"
        # 'dumpsys power' gives us the power manager state
        result = self.device.shell("dumpsys power")
        
        # Check for the magic string
        if "mWakefulness=Awake" in result:
            print("[*] Screen is already AWAKE. Skipping toggle.")
        else:
            print("[*] Screen is ASLEEP. Sending Wake Signal...")
            self.device.shell("input keyevent 26") # Power Button
            time.sleep(1)
            self.device.shell("input keyevent 82") # Menu/Unlock Key
            print("[*] Screen should be awake now.")
            

    def launch_app(self, app_name):
        """Launches an app by its package name."""
        package = APPS.get(app_name)
        if not package:
            print(f"[!] Unknown app: {app_name}")
            return
        
        print(f"[*] Launching {app_name.upper()}...")
        # The 'monkey' command is a built-in Android tool to launch apps
        self.device.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        time.sleep(3) # Wait for splash screen

    def scroll_feed0(self, swipes=3):
        """Simulates the 'Doom Scroll'."""
        print(f"[*] Engaging scroll protocol ({swipes} swipes)...")
        # Get screen size to calculate swipe coordinates dynamically
        wm_size = self.device.shell("wm size") # output: Physical size: 1080x2400
        # (We will just use hardcoded safe values for now to test)
        
        # Swipe from Bottom (80%) to Top (20%)
        start_x = random.uniform(100,500)
        start_y = random.uniform(1100,1600)
        end_x = random.uniform(300,550)
        end_y = random.uniform(150,400)
        
        for i in range(swipes):
            print(f"   -> Swipe {i+1}/{swipes}")
            self.device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} 300")
            time.sleep(random.uniform(4.5,10)) # Wait for content to load


    def scroll_feed(self):
        """
        Simulates a thumb dragging up the screen.
        Adds 'Drift' (X-axis wobble) and 'Speed Variance' so it looks real.
        """
        print(">> 📜 Scrolling (Human Style)...")
        
        # 1. SCREEN DIMENSIONS (Approx for most phones, or fetch dynamically)
        # Center is roughly x=500 for a 1080p screen.
        screen_width = 720
        screen_height = 1461
        
        # 2. RANDOMIZE START POINT (Bottom of screen)
        # Humans don't start at exactly pixel 1500. We start at 1500 +/- 50.
        start_x = random.randint(screen_width // 2 - 100, screen_width // 2 + 100)
        start_y = random.randint(int(screen_height * 0.6), int(screen_height * 0.8)) # Lower half
        
        # 3. RANDOMIZE END POINT (Top of screen)
        # Humans swipe slightly diagonal (The "Thumb Arc").
        # If I am right-handed, I swipe slightly Left.
        drift = random.randint(-50, 50) 
        end_x = start_x + drift
        end_y = random.randint(int(screen_height * 0.2), int(screen_height * 0.4)) # Upper half
        
        # 4. RANDOMIZE DURATION (Speed)
        # Fast scroll = 100ms. Slow read scroll = 500ms.
        duration = random.randint(300, 700) 

        # 5. EXECUTE
        self.device.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} 300")
        time.sleep(random.uniform(4.5,10))
        #cmd = f"adb -s {self.device_id} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}"
        #subprocess.run(cmd, shell=True)
        
        # 6. THE "READING PAUSE"
        # After swiping, we stop to "look" at the tweet.
        time.sleep(random.uniform(1.5, 4.0))



    def scalpel(self):
        print("[*] VISION: Dumping UI Hierarchy (The Scalpel)...")
        
        # 1. Tell Android to dump the XML to its own storage
        # This takes 1-2 seconds. It is slow but precise.
        self.device.shell("uiautomator dump /sdcard/window_dump.xml")
        
        # 2. Pull the file to your laptop ("The Harvest")
        self.device.pull("/sdcard/window_dump.xml", "ui_dump.xml")
        
        return "ui_dump.xml"


    def double_tap_like(self):
        """Hunts for the specific ID of the Like button."""
        print("[*] ACTION: Hunting for Heart ID...")
        
        # 1. Search for the EXACT Resource ID
        # We search for "button_like" because the full ID is "com.instagram...:id/row_feed_button_like"
        coords = self.find_element_coordinates("button_like")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
        if not coords:
            print("[-] Heart hidden. Trying to find 'Comment' button...")
            comment_coords = self.find_element_coordinates("button_comment")
            if comment_coords:
                # If we find Comment, the Like button is usually ~130 pixels to the LEFT
                print("[*] Found Comment button! Calculating offset for Like...")
                coords = (comment_coords[0] - 130, comment_coords[1])

        if not coords:
            print("[-] Heart hidden. Trying to find 'save_feed_btn' button...")
            comment_coords = self.find_element_coordinates("button_save")
            if comment_coords:
                # If we find Comment, the Like button is usually ~130 pixels to the LEFT
                print("[*] Found Comment button! Calculating offset for Like...")
                coords = (comment_coords[0] - 600, comment_coords[1])
        
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5)
            final_y = y + random.randint(-5, 5)
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed()
            

    def double_tap_like0(self):
        """Double taps the center of the screen to like a post."""
        print("[*] DETECTED: Content worthy of acknowledgment.")
        print("[*] ACTION: Double-Tap (Like)")
        
        # Coordinates for the center of the screen (Adjust based on your 'wm size')
        # Assuming 1080x2400 screen -> Center is roughly 540, 1000
        center_x = 360
        center_y = 730

        center_x, center_y = self.find_element_coordinates("like")
        
        # Tap twice quickly
        #self.device.shell(f"input tap {random.uniform(center_x-10,center_x+10)} {center_y}")
        #time.sleep(random.uniform(0.01,0.05)) # 100ms gap
        #self.device.shell(f"input tap {center_x} {center_y}")
        #cmd = f""

        x1 = center_x + random.randint(-0.5, 0.5)
        y1 = center_y + random.randint(-0.5, 0.5)

        # Tap 2: Slightly different from Tap 1 (The Human Tremor)
        x2 = center_x + random.randint(-5, 5)
        y2 = center_y + random.randint(-5, 5)
        
        # The Command: Tap 1 -> (Process Lag) -> Tap 2
        # We use the separate coordinates to look organic
        cmd = f"input tap {x1} {y1} " #&& input tap {x2} {y2}"
        
        self.device.shell(cmd)
        
        time.sleep(random.uniform(1,2)) # Wait for animation

    def tap_comment_btn(self):
        coords = self.find_element_coordinates("button_comment")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
        if not coords:
            print("[-] Heart hidden. Trying to find 'Comment' button...")
            comment_coords = self.find_element_coordinates("button_like")
            if comment_coords:
                # If we find Comment, the Like button is usually ~130 pixels to the LEFT
                print("[*] Found Comment button! Calculating offset for Like...")
                coords = (comment_coords[0] + 130, comment_coords[1])

        if not coords:
            print("[-] Heart hidden. Trying to find 'save_feed_btn' button...")
            comment_coords = self.find_element_coordinates("button_save")
            if comment_coords:
                # If we find Comment, the Like button is usually ~130 pixels to the LEFT
                print("[*] Found Comment button! Calculating offset for Like...")
                coords = (comment_coords[0] - 500, comment_coords[1])
        
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5)
            final_y = y + random.randint(-5, 5)
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed(1)


    def find_element_coordinates(self, text_identifier):
        """
        Scans XML for a button containing specific text (e.g., 'Like', 'Comment')
        and returns its EXACT center X,Y.
        """
        xml_file = self.scalpel() # Dump the UI
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print(f"[*] SCALPEL: Searching for element '{text_identifier}'...")
        
        for node in root.iter('node'):
            # Check content-desc (often used for icons like 'Like') or text
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower()
            res_id = node.attrib.get('resource-id', '').lower()
            
            if text_identifier in desc or text_identifier in text or text_identifier in res_id:
                # FOUND IT! Now extract bounds: "[140,1600][280,1740]"
                bounds = node.attrib.get('bounds')
                if bounds:
                    # Parse the string "[x1,y1][x2,y2]"
                    coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)
                    
                    # Calculate Center
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    print(f"[+] FOUND '{text_identifier}' at {center_x}, {center_y}")
                    return center_x, center_y
                    
        print(f"[-] Element '{text_identifier}' NOT FOUND.")
        return None




    def expand_caption(self):
        """
        1. Finds 'more'.
        2. If it's too low, drags it to the top.
        3. Clicks it.
        """
        found_more = False

        coords = None
        coords2 = 0,0


        #coords = self.find_element_coordinates("more")


        xml_file = self.scalpel() # Dump the UI
        tree = ET.parse(xml_file)
        root = tree.getroot()
        text_identifier= "more"
        
        print(f"[*] SCALPEL: Searching for element '{text_identifier}'...")
        
        for node in root.iter('node'):
            # Check content-desc (often used for icons like 'Like') or text
            desc = node.attrib.get('content-desc', '').lower().strip()
            text = node.attrib.get('text', '').lower().strip()
            res_id = node.attrib.get('resource-id', '').lower()
            
            if "three_dot_menu" in res_id:
                continue

            if  text_identifier in desc or text_identifier in text or text_identifier in res_id:
                # FOUND IT! Now extract bounds: "[140,1600][280,1740]"
                bounds = node.attrib.get('bounds')
                if bounds:
                    # Parse the string "[x1,y1][x2,y2]"
                    coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)

                    
                    if x2<700:
                    # Calculate Center
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                    
                        print(f"[+] FOUND '{text_identifier}' at {center_x}, {center_y}")
                        coords2 = center_x, center_y
                    
                        
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
       
        
        # 3. Execution Logic
        if coords2:
            x, y = coords2
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-1, 1)
            final_y = y + random.randint(-1, 1)
            
            #self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
            found_more = True
        else:
            print("[!] TARGET LOST. could not found more...")
            #self.scroll_feed(1)

        if final_y > 4000:
            final_y2= random.uniform(300,450)

            offsett = random.uniform(-3,3)

            final_x2=final_x+offsett
            final_x3 = final_x2 + offsett//10

            print(f"[*] ACTION: Adjusting position (Pulling Y={final_y} to Y={final_y2})...")
                        # Swipe UP to bring the button UP
                        # Logic: Swipe from Button Y to Target Y
            self.device.shell(f"input swipe {final_x2} {final_y} {final_x3} {final_y2} 300")
            #device_obj.shell(f"input swipe {final_x2} {final_y} {final_x3} {final_y2} 300")
            time.sleep(random.uniform(3,5)) # Wait for scroll physics to settle

            for node in root.iter('node'):
            # Check content-desc (often used for icons like 'Like') or text
                desc = node.attrib.get('content-desc', '').lower().strip()
                text = node.attrib.get('text', '').lower().strip()
                res_id = node.attrib.get('resource-id', '').lower()
            
                if "three_dot_menu" in res_id:
                    continue

                if  text_identifier in desc or text_identifier in text or text_identifier in res_id:
                 # FOUND IT! Now extract bounds: "[140,1600][280,1740]"
                    bounds = node.attrib.get('bounds')
                    if bounds:
                        # Parse the string "[x1,y1][x2,y2]"
                        coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                        x1, y1, x2, y2 = map(int, coords)

                    
                        if x2<700:
                    # Calculate Center
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                    
                            print(f"[+] FOUND '{text_identifier}' at {center_x}, {center_y}")
                            coords2 = center_x, center_y
                    
                                    
                        # UPDATE: Since we moved the screen, the button is now at Y=500!
            #final_y = 500 
                    
            if coords2:
                x, y = coords2
                print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
                # Add Jitter (Stealth)
                final_x = x + random.randint(-1, 1)
                final_y = y + random.randint(-1, 1)        # Now Click the (hopefully visible) button
                print(f"[*] ACTION: Clicking 'more' at {final_x},{final_y2}")
                self.device.shell(f"input tap {final_x} {final_y2}")
                    #device_obj.shell(f"input tap {center_x} {center_y}")
                time.sleep(1) 
                    
            #found_more = True
            
        if found_more == True and final_y<4000:
            print(f"[*] ACTION: Clicking 'more' at second {final_x},{final_y}")
            self.device.shell(f"input tap {final_x} {final_y}")
                    #device_obj.shell(f"input tap {center_x} {center_y}")
            time.sleep(1) 

        
        return found_more

        
        
   

    
    def extract_intelligence(self):
        """
        The Ultimate Text Harvester.
        1. Scans UI.
        2. Hunts for 'more' button & clicks it.
        3. If NO text found, does a 'Blind Micro-Scroll' and scans again.
        4. Returns the best text candidate.
        """
        print("[*] VISION: Initiating Intelligence Harvest...")

        coord = self.find_element_coordinates("button_comment")
        anchor_x,anchor_yy = coord

        min_y = anchor_yy-500
        max_y = anchor_yy
        
        # --- PHASE 1: INITIAL SCAN ---
        xml_file = self.scalpel() 
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Check 1: Is there a "more" button?
        # (We reuse the logic to scroll-to-focus and click it)
        expanded = self.expand_caption()
        
        if expanded:
            print("[*] VISION: Caption expanded. Re-scanning...")
            # If we clicked 'more', we MUST dump again to see the new text
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
        # --- PHASE 2: EVALUATE CANDIDATES ---
        candidates = self._parse_text_from_root(root)
        
        # --- PHASE 3: THE BLIND MICRO-SCROLL (Fail-Safe) ---
        # If we found NOTHING (and didn't expand), the caption might be off-screen.
        if not candidates and not expanded:
            print("[!] VISION: Zero intelligence found. Caption might be below fold.")
            print("[*] ACTION: Engaging Blind Micro-Scroll (200px)...")
            
            # Swipe UP just a little bit to peek below
            # From Y=1500 to Y=1300 (adjust based on your screen height)
            self.device.shell("input swipe 500 1500 500 1200 300")
            time.sleep(1.5) # Wait for physics to settle
            
            # Re-Dump
            print("[*] VISION: Re-scanning new sector...")
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Try to get text again
            candidates = self._parse_text_from_root(root)

        # --- PHASE 4: RETURN BEST RESULT ---
        if candidates:
            # We want the longest text block (usually the caption)
            best_candidate = max(candidates, key=len)
            print(f"[+] INTELLIGENCE ACQUIRED: '{best_candidate[:500]}...'")
            return best_candidate
        else:
            print("[-] VISION: No usable text found (Post is likely just a video).")
            return None

    def _parse_text_from_root(self, root):
        """Helper to extract clean text candidates from an XML root."""
        candidates = []
        for node in root.iter('node'):
            text = node.attrib.get('text')
            desc = node.attrib.get('content-desc')
            
            content = ""
            if text: content += text + " "
            if desc: content += desc
            
            # Filter trash
            if content and len(content) > 15:
                lower_content = content.lower()
                if "battery" in lower_content or "wifi" in lower_content or "time" in lower_content:
                    continue
                candidates.append(content.strip())
        return candidates
        
        
        

    def type_human(self, text):
        """
        Types text in 'bursts' to simulate human speed without choking ADB.
        """
        print(f"[*] HUMAN TYPING: '{text}'")
        
        # 1. Tap the text field to ensure focus (Critical!)
        # self.device.shell("input tap X Y") # Ensure you tapped before calling this
        
        # 2. Split text into chunks of 3-5 characters
        # Humans don't type "c-a-t", they type "cat " then pause.
        chunks = []
        i = 0
        while i < len(text):
            chunk_size = random.randint(3, 6)
            chunks.append(text[i : i + chunk_size])
            i += chunk_size
            
        # 3. Type each chunk with a jitter delay
        for chunk in chunks:
            # Escape spaces and quotes for ADB
            clean_chunk = chunk.replace(" ", "%s").replace("'", r"\'").replace('"', r'\"')
            
            self.device.shell(f"input text {clean_chunk}")
            
            # The "Human Pause" (0.1s to 0.5s)
            time.sleep(random.uniform(0.1, 0.5))
            
        print("[*] TYPING COMPLETE.")
        time.sleep(1)


    def post_comment(self, comment_text):
        """
        Full Sequence: Open Comments -> Type -> Find Send -> Escape.
        """
        print("[*] ACTION: Engaging Discourse Protocol...")
        
        # 1. Click the Comment Icon (You already have this part)
        # Assuming you used the 'triangulate' method to click the comment bubble
        # self.tap_comment_icon() 
        #self.tap_comment_btn()
        
        time.sleep(3) # WAIT for keyboard to pop up! Critical!
        
        # 2. Type the thought
        self.type_human(comment_text)
        
        # 3. Find and Click "Post" (The Blue Arrow)
        print("[*] SCALPEL: Hunting for 'Post' button...")
        
        # Use your Scalpel to find the button named "Post" or "Send"
        # In Instagram, it is often 'content-desc="Post"' or ID 'row_thread_composer_button_send'
        coords = self.find_element_coordinates("post_button_icon") 
        if not coords:
             coords = self.find_element_coordinates("post")
             
        if coords:
            x, y = coords
            print(f"[+] SENDING at {x}, {y}")
            self.device.shell(f"input tap {x} {y}")
        else:
            print("[!] PANIC: Cannot find Send button. Blind firing...")
            # Fallback: Right edge, just above keyboard (approx Y=1100-1200 usually)
            self.device.shell("input tap 630 790") 
            
        time.sleep(2) # Wait for comment to post
        
        # 4. THE ESCAPE (The "Run Away" Move)
        print("[*] ESCAPE: Returning to Void...")
        
        # Press BACK once to close Keyboard
        self.device.shell("input keyevent 4") 
        time.sleep(1)
        
        # Press BACK again to exit Comment Thread
        self.device.shell("input keyevent 4")
        time.sleep(1)
        
        print("[*] MISSION COMPLETE. Back in Feed.")


   
    def clean_text_for_adb(self, text):
        """
        Removes characters that crash Selenium (Non-BMP emojis).
        Also strips asterisks ** because WhatsApp doesn't need Markdown bolding from bots.
        """
        # 1. Strip Non-BMP characters (The complex emojis that caused the crash)
        cleaned = "".join(c for c in text if c <= "\uFFFF")

        # 2. Remove Markdown bolding (The **GitHub** stuff looked robotic)
        cleaned = cleaned.replace("**", "").replace("##", "")
    
        return cleaned
        
        
        
    def start_insta_bot(self):
        try:
            for i in range(10): # Do this 10 times then stop
                print(f"\n--- Cycle {i+1}/10 ---")
            
            # A. Scroll (The Hunt)
                bot.scroll_feed()

             # ... inside loop ...
    
            # 1. Scroll
                bot.scroll_feed()

                if random.choice([True, False]):
    
            # 2. Read
                    text = bot.extract_intelligence()
    
            # 3. Decide
                    if text != None :
                # 4. Click Comment Button (Triangulation)
            # Note: You need a function that specifically clicks the comment icon, 
            # NOT the heart. Use the offset logic we discussed!
                        bot.tap_comment_btn() 
                        print("tapped on comment btn")

                        reply_text =  brain.query_llm(text)

                        clean_text = bot.clean_text_for_adb(reply_text)
        
                # 5. Execute the Speech
                        bot.post_comment(clean_text)
        
                    else:
            # Just Like
                        bot.double_tap_like()
            
            # B. Human Pause (The Observation)
            # Sleep between 5 to 12 seconds (Randomly)
                sleep_time = random.uniform(5, 12)
                print(f"[*] Watching content for {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            
            # C. The Like (The Approval)
            # 50% chance to like the post (Humans don't like EVERYTHING)
                if random.choice([True, False]):
                    bot.double_tap_like()
                else:
                    print("[*] Skipping like (Human behavior simulation).")
        except KeyboardInterrupt:
            print("\n[!] Manual Override. Shutting down.")



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#linkedin-------------------------------------------------linkdn----------------------------------------


    def post_comment_lkdn(self, comment_text):
        """
        Full Sequence: Open Comments -> Type -> Find Send -> Escape.
        """
        print("[*] ACTION: Engaging Discourse Protocol...")
        
        # 1. Click the Comment Icon (You already have this part)
        # Assuming you used the 'triangulate' method to click the comment bubble
        # self.tap_comment_icon() 
        #self.tap_comment_btn()
        
        time.sleep(3) # WAIT for keyboard to pop up! Critical!
        
        # 2. Type the thought
        self.type_human(comment_text)
        
        # 3. Find and Click "Post" (The Blue Arrow)
        print("[*] SCALPEL: Hunting for 'Post' button...")
        
        # Use your Scalpel to find the button named "Post" or "Send"
        # In Instagram, it is often 'content-desc="Post"' or ID 'row_thread_composer_button_send'
        coords = None #self.find_element_coordinates("comment") 
        
             
        if coords:
            x, y = coords
            print(f"[+] SENDING at {x}, {y}")
            self.device.shell(f"input tap {x} {y}")
        else:
            print("[!] PANIC: Cannot find Send button. Blind firing...")
            # Fallback: Right edge, just above keyboard (approx Y=1100-1200 usually)
            self.device.shell("input tap 630 790") 
            
        time.sleep(2) # Wait for comment to post
        
        # 4. THE ESCAPE (The "Run Away" Move)
        print("[*] ESCAPE: Returning to Void...")
        
        # Press BACK once to close Keyboard
        self.device.shell("input keyevent 4") 
        time.sleep(1)
        
        # Press BACK again to exit Comment Thread
        self.device.shell("input keyevent 4")
        time.sleep(1)
        
        print("[*] MISSION COMPLETE. Back in Feed.")


   
   
        
        


    def find_element_coordinates_lkdn_comment(self, text_identifier):
        """
        Scans XML for a button. 
        FIX: Ignores buttons at the very top (previous post) 
        and picks the one closest to the center of the screen.
        """
        xml_file = self.scalpel() 
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print(f"[*] SCALPEL: Searching for best '{text_identifier}'...")
        
        # Define Screen Center (approx for 2400px height)
        SCREEN_CENTER_Y = 1200 
        
        best_coords = None
        min_dist_to_center = 9999
        
        for node in root.iter('node'):
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower()
            res_id = node.attrib.get('resource-id', '').lower()
            
            if text_identifier in desc or text_identifier in text or text_identifier in res_id:
                bounds = node.attrib.get('bounds')
                if bounds:
                    coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    # --- THE FIX ---
                    # 1. Ignore "Phantom" buttons at the very top (Previous Post)
                    if center_y < 300 or center_y > 1400 :
                        continue 
                        
                    # 2. Find the one closest to the middle
                    dist = abs(center_y - SCREEN_CENTER_Y)
                    if dist < min_dist_to_center:
                        min_dist_to_center = dist
                        best_coords = (center_x, center_y)

        if best_coords:
            print(f"[+] LOCKED BEST TARGET '{text_identifier}' at {best_coords}")
            return best_coords
                    
        print(f"[-] Element '{text_identifier}' NOT FOUND.")
        return None





    def expand_caption_lkdn(self):
        """
        1. Finds 'more'.
        2. If it's too low, drags it to the top.
        3. Clicks it.
        """
        found_more = True

       

        
        return found_more

        
        



    def extract_intelligence_lkdn(self):
        """
        The Ultimate Text Harvester.
        1. Scans UI.
        2. Hunts for 'more' button & clicks it.
        3. If NO text found, does a 'Blind Micro-Scroll' and scans again.
        4. Returns the best text candidate.
        """
        print("[*] VISION: Initiating Intelligence Harvest...")

        #coord = self.find_element_coordinates("button_comment")
        #anchor_x,anchor_yy = coord

        #min_y = anchor_yy-500
        #max_y = anchor_yy

        footer_y = None
        min_dist_to_center = 9999
        screen_center_y = 800 # Approx center
        
        # --- PHASE 1: INITIAL SCAN ---
        xml_file = self.scalpel() 
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Check 1: Is there a "more" button?
        # (We reuse the logic to scroll-to-focus and click it)
        expanded = self.expand_caption_lkdn()
        
        if expanded:
            print("[*] VISION: Caption expanded. Re-scanning...")
            # If we clicked 'more', we MUST dump again to see the new text
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()


            comment_buttons = []
            profile_headers = []
        
        for node in root.iter('node'):
            res_id = node.attrib.get('resource-id', '').lower()
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower().strip()
            bounds = node.attrib.get('bounds')
            
            if not bounds: continue

            # Parse Y coords
            coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
            y_center = (int(coords[1]) + int(coords[3])) // 2
            
            # Identify Footer (Comment Button)
            if "react" in res_id or "react" in desc or "react" in text:
                comment_buttons.append(y_center)
                
            # Identify Header (Profile Name)
            # Based on your logs: "row_feed_photo_profile_name"
            if "profile_name" in res_id:
                profile_headers.append(y_center)

        # Pick the Footer closest to screen center (The "Active" Post)
        if not comment_buttons:
            print("[-] No Footer found. Scrolling...")
            return None
            
        footer_y = min(comment_buttons, key=lambda y: abs(y - screen_center_y))
        print(f"[*] LOCKED FOOTER (Bottom Bread) at Y={footer_y}")

        # --- STEP 2: FIND THE HEADER (Top Bread) ---
        # We want the profile header that is ABOVE the footer, but CLOSEST to it.
        # Filter headers where Y < footer_y
        valid_headers = [y for y in profile_headers if y < footer_y]
        
        if not valid_headers:
            print("[-] No Header found. Assuming top of screen is boundary.")
            header_y = 0 
        else:
            # The closest one above the footer is the max of the valid list
            header_y = max(valid_headers)
            print(f"[*] LOCKED HEADER (Top Bread) at Y={header_y}")

        # --- STEP 3: EXTRACT THE MEAT ---
        candidates = []
            
        # --- PHASE 2: EVALUATE CANDIDATES ---
        candidates = self._parse_text_from_root(root)
        
        # --- PHASE 3: THE BLIND MICRO-SCROLL (Fail-Safe) ---
        # If we found NOTHING (and didn't expand), the caption might be off-screen.
        if not candidates and not expanded:
            print("[!] VISION: Zero intelligence found. Caption might be below fold.")
            print("[*] ACTION: Engaging Blind Micro-Scroll (200px)...")
            
            # Swipe UP just a little bit to peek below
            # From Y=1500 to Y=1300 (adjust based on your screen height)
            self.device.shell("input swipe 500 1500 500 1200 300")
            time.sleep(1.5) # Wait for physics to settle
            
            # Re-Dump
            print("[*] VISION: Re-scanning new sector...")
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Try to get text again
            candidates = self._parse_text_from_root(root, header_y, footer_y)

        # --- PHASE 4: RETURN BEST RESULT ---
        if candidates:
            # We want the longest text block (usually the caption)
            best_candidate = max(candidates, key=len)
            print(f"[+] INTELLIGENCE ACQUIRED: '{best_candidate[:5000]}...'")
            return best_candidate
        else:
            print("[-] VISION: No usable text found (Post is likely just a video).")
            return None

    def _parse_text_from_root_lkdn(self, root, header_yy , footer_yy):
        """Helper to extract clean text candidates from an XML root."""
        
        candidates = []
        for node in root.iter('node'):
            text = node.attrib.get('text')
            desc = node.attrib.get('content-desc')
            bounds = node.attrib.get('bounds')
            if bounds:
                coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                node_y_center = (int(coords[1]) + int(coords[3])) // 2
                if header_yy < node_y_center < footer_yy:
            
                    content = ""
                    if text: content += text + " "
                    if desc: content += desc
            
            # Filter trash
                    if content and len(content) > 15:
                        lower_content = content.lower()
                        if "battery" in lower_content or "wifi" in lower_content or "time" in lower_content:
                            continue
                        candidates.append(content.strip())
        return candidates


    def find_element_coordinates_lkdn(self, text_identifier):
        """
        Scans XML for a button containing specific text (e.g., 'Like', 'Comment')
        and returns its EXACT center X,Y.
        """
        xml_file = self.scalpel() # Dump the UI
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print(f"[*] SCALPEL: Searching for element '{text_identifier}'...")
        
        for node in root.iter('node'):
            # Check content-desc (often used for icons like 'Like') or text
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower()
            res_id = node.attrib.get('resource-id', '').lower()
            
            if text_identifier in desc or text_identifier in text or text_identifier in res_id:
                # FOUND IT! Now extract bounds: "[140,1600][280,1740]"
                bounds = node.attrib.get('bounds')
                if bounds:
                    # Parse the string "[x1,y1][x2,y2]"
                    coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)
                    
                    # Calculate Center
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    print(f"[+] FOUND '{text_identifier}' at {center_x}, {center_y}")
                    return center_x, center_y
                    
        print(f"[-] Element '{text_identifier}' NOT FOUND.")
        return None




    def double_tap_like_lkdn(self):
        """Double taps the center of the screen to like a post."""
        print("[*] DETECTED: Content worthy of acknowledgment.")
        print("[*] ACTION: Double-Tap (Like)")

        coords = self.find_element_coordinates_lkdn_comment("react")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
       
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5) - 101
            final_y = y + random.randint(-5, 5) + 101
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed()
        
        
        
        time.sleep(random.uniform(1,2)) # Wait for animation

    




    def start_linkdn(self):

        try:
            for i in range(10): # Do this 10 times then stop
                print(f"\n--- Cycle {i+1}/10 ---")
                bot.launch_app("linkedin")

                time.sleep(random.uniform(4,7))


                bot.scroll_feed()

                time.sleep(random.uniform(3,2))

                bot.scroll_feed()

                try:


                    x,y = bot.find_element_coordinates_lkdn("react")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")


                time.sleep(random.uniform(4,7))



                
                sleep_time = random.uniform(5, 12)


                if random.choice([True, False]):
    
            # 2. Read
                    text = bot.extract_intelligence_lkdn()
    
            # 3. Decide
                    if text != None :
                # 4. Click Comment Button (Triangulation)
            # Note: You need a function that specifically clicks the comment icon, 
            # NOT the heart. Use the offset logic we discussed!
                        bot.tap_comment_btn_lkdn() 
                        print("tapped on comment btn")

                        reply_text =  brain.query_llm(text)

                        clean_text = bot.clean_text_for_adb(reply_text)
        
                # 5. Execute the Speech
                        bot.post_comment_lkdn(clean_text)
        
                    else:
            # Just Like
                        bot.double_tap_like()
            
            # B. Human Pause (The Observation)
            # Sleep between 5 to 12 seconds (Randomly)
                        sleep_time = random.uniform(5, 12)


                # 3. Scroll to look human
    #bot.scroll_feed(swipes=5)
            time.sleep(random.uniform(4,7))

        except KeyboardInterrupt:
            print("\n[!] Manual Override. Shutting down.")


    def tap_comment_btn_lkdn(self):
        coords = self.find_element_coordinates_lkdn_comment("react")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
       
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5) 
            final_y = y + random.randint(-5, 5) + 101
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed()


  
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#xxxxxxxxx------------------xxxxxxxxxxx-------------------------------------------------------------------------
    def find_element_coordinates_x_equal(self, text_identifier):
        """
        Scans XML for a button. 
        FIX: Ignores buttons at the very top (previous post) 
        and picks the one closest to the center of the screen.
        """
        xml_file = self.scalpel() 
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        print(f"[*] SCALPEL: Searching for best '{text_identifier}'...")
        
        # Define Screen Center (approx for 2400px height)
        SCREEN_CENTER_Y = 1200 
        
        best_coords = None
        min_dist_to_center = 9999
        
        for node in root.iter('node'):
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower()
            res_id = node.attrib.get('resource-id', '').lower()
            
            if text_identifier==text:   #in desc or text_identifier in text or text_identifier in res_id:
                bounds = node.attrib.get('bounds')
                if bounds:
                    coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                    x1, y1, x2, y2 = map(int, coords)
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    # --- THE FIX ---
                    # 1. Ignore "Phantom" buttons at the very top (Previous Post)
                    if center_y < 300 or center_y > 1400 :
                        continue 
                        
                    # 2. Find the one closest to the middle
                    dist = abs(center_y - SCREEN_CENTER_Y)
                    if dist < min_dist_to_center:
                        min_dist_to_center = dist
                        best_coords = (center_x, center_y)

        if best_coords:
            print(f"[+] LOCKED BEST TARGET '{text_identifier}' at {best_coords}")
            return best_coords
                    
        print(f"[-] Element '{text_identifier}' NOT FOUND.")
        return None


    def post_comment_x(self, comment_text):
        """
        Full Sequence: Open Comments -> Type -> Find Send -> Escape.
        """
        print("[*] ACTION: Engaging Discourse Protocol...")
        
        # 1. Click the Comment Icon (You already have this part)
        # Assuming you used the 'triangulate' method to click the comment bubble
        # self.tap_comment_icon() 
        #self.tap_comment_btn()
        
        time.sleep(3) # WAIT for keyboard to pop up! Critical!
        
        # 2. Type the thought
        self.type_human(comment_text)
        
        # 3. Find and Click "Post" (The Blue Arrow)
        print("[*] SCALPEL: Hunting for 'Post' button...")
        
        # Use your Scalpel to find the button named "Post" or "Send"
        # In Instagram, it is often 'content-desc="Post"' or ID 'row_thread_composer_button_send'
        coords = self.find_element_coordinates_x_equal("reply") 
        
             
        if coords:
            x, y = coords
            print(f"[+] SENDING at {x}, {y}")
            self.device.shell(f"input tap {x} {y}")
        else:
            print("[!] PANIC: Cannot find Send button. Blind firing...")
            # Fallback: Right edge, just above keyboard (approx Y=1100-1200 usually)
            self.device.shell("input tap 630 114") 
            
        time.sleep(2) # Wait for comment to post
        
        # 4. THE ESCAPE (The "Run Away" Move)
        print("[*] ESCAPE: Returning to Void...")
        
        # Press BACK once to close Keyboard
        self.device.shell("input keyevent 4") 
        time.sleep(1)
        
        # Press BACK again to exit Comment Thread
        #self.device.shell("input keyevent 4")
        time.sleep(1)
        
        print("[*] MISSION COMPLETE. Back in Feed.")
    
    
    
    
    def expand_caption_lkdn(self):
        """
        1. Finds 'more'.
        2. If it's too low, drags it to the top.
        3. Clicks it.
        """
        found_more = True

       

        
        return found_more

        
        



    def extract_intelligence_x(self):
        """
        The Ultimate Text Harvester.
        1. Scans UI.
        2. Hunts for 'more' button & clicks it.
        3. If NO text found, does a 'Blind Micro-Scroll' and scans again.
        4. Returns the best text candidate.
        """
        print("[*] VISION: Initiating Intelligence Harvest...")

        #coord = self.find_element_coordinates("button_comment")
        #anchor_x,anchor_yy = coord

        #min_y = anchor_yy-500
        #max_y = anchor_yy

        footer_y = None
        min_dist_to_center = 9999
        screen_center_y = 800 # Approx center
        
        # --- PHASE 1: INITIAL SCAN ---
        xml_file = self.scalpel() 
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Check 1: Is there a "more" button?
        # (We reuse the logic to scroll-to-focus and click it)
        expanded = self.expand_caption_lkdn()
        
        if expanded:
            print("[*] VISION: Caption expanded. Re-scanning...")
            # If we clicked 'more', we MUST dump again to see the new text
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()


            comment_buttons = []
            profile_headers = []
        
        for node in root.iter('node'):
            res_id = node.attrib.get('resource-id', '').lower()
            desc = node.attrib.get('content-desc', '').lower()
            text = node.attrib.get('text', '').lower().strip()
            bounds = node.attrib.get('bounds')
            
            if not bounds: continue

            # Parse Y coords
            coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
            y_center = (int(coords[1]) + int(coords[3])) // 2

            if y_center>1400:continue
            
            # Identify Footer (Comment Button)
            if "grok" in res_id or "grok" in desc or "grok" in text :
                
                comment_buttons.append(y_center)
                
            # Identify Header (Profile Name)
            # Based on your logs: "row_feed_photo_profile_name"
            if "profile_name" in res_id:
                profile_headers.append(y_center)

        # Pick the Footer closest to screen center (The "Active" Post)
        if not comment_buttons:
            print("[-] No Footer found. Scrolling...")
            return None
            
        footer_y = min(comment_buttons, key=lambda y: abs(y - screen_center_y))
        print(f"[*] LOCKED FOOTER (Bottom Bread) at Y={footer_y}")

        # --- STEP 2: FIND THE HEADER (Top Bread) ---
        # We want the profile header that is ABOVE the footer, but CLOSEST to it.
        # Filter headers where Y < footer_y
        valid_headers = [y for y in profile_headers if y < footer_y]
        
        if not valid_headers:
            print("[-] No Header found. Assuming top of screen is boundary.")
            header_y = 0 
        else:
            # The closest one above the footer is the max of the valid list
            header_y = max(valid_headers)
            print(f"[*] LOCKED HEADER (Top Bread) at Y={header_y}")

        # --- STEP 3: EXTRACT THE MEAT ---
        candidates = []
            
        # --- PHASE 2: EVALUATE CANDIDATES ---
        candidates = self._parse_text_from_root(root)
        
        # --- PHASE 3: THE BLIND MICRO-SCROLL (Fail-Safe) ---
        # If we found NOTHING (and didn't expand), the caption might be off-screen.
        if not candidates and not expanded:
            print("[!] VISION: Zero intelligence found. Caption might be below fold.")
            print("[*] ACTION: Engaging Blind Micro-Scroll (200px)...")
            
            # Swipe UP just a little bit to peek below
            # From Y=1500 to Y=1300 (adjust based on your screen height)
            self.device.shell("input swipe 500 1500 500 1200 300")
            time.sleep(1.5) # Wait for physics to settle
            
            # Re-Dump
            print("[*] VISION: Re-scanning new sector...")
            xml_file = self.scalpel()
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Try to get text again
            candidates = self._parse_text_from_root(root, header_y, footer_y)

        # --- PHASE 4: RETURN BEST RESULT ---
        if candidates:
            # We want the longest text block (usually the caption)
            best_candidate = max(candidates, key=len)
            print(f"[+] INTELLIGENCE ACQUIRED: '{best_candidate[:5000]}...'")
            return best_candidate
        else:
            print("[-] VISION: No usable text found (Post is likely just a video).")
            return None

    def _parse_text_from_root_lkdn(self, root, header_yy , footer_yy):
        """Helper to extract clean text candidates from an XML root."""
        
        candidates = []
        for node in root.iter('node'):
            text = node.attrib.get('text')
            desc = node.attrib.get('content-desc')
            bounds = node.attrib.get('bounds')
            if bounds:
                coords = bounds.replace('][', ',').replace('[', '').replace(']', '').split(',')
                node_y_center = (int(coords[1]) + int(coords[3])) // 2
                if header_yy < node_y_center < footer_yy:
            
                    content = ""
                    if text: content += text + " "
                    if desc: content += desc
            
            # Filter trash
                    if content and len(content) > 15:
                        lower_content = content.lower()
                        if "battery" in lower_content or "wifi" in lower_content or "time" in lower_content:
                            continue
                        candidates.append(content.strip())
        return candidates



    def double_tap_like_x(self):
        """Double taps the center of the screen to like a post."""
        print("[*] DETECTED: Content worthy of acknowledgment.")
        print("[*] ACTION: Double-Tap (Like)")

        coords = self.find_element_coordinates_lkdn_comment("grok")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
       
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")

            
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5) - 260
            final_y = y + random.randint(-5, 5) - 38
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed()



    def tap_comment_btn_x(self):
        coords = self.find_element_coordinates_lkdn_comment("grok")
        
        # 2. If Like button is hidden, try finding the "Comment" button and offset left
       
        # 3. Execution Logic
        if coords:
            x, y = coords
            print(f"[+] LOCKED ON TARGET: {x}, {y}")
            
            # Add Jitter (Stealth)
            final_x = x + random.randint(-5, 5) - 466
            final_y = y + random.randint(-5, 5) - 38
            
            self.device.shell(f"input tap {final_x} {final_y}")
            time.sleep(1) 
        else:
            print("[!] TARGET LOST. Scrolling to refresh UI...")
            self.scroll_feed()





    def start_twitter(self):

        bot.launch_app("twitter")

        try:
            for i in range(10): # Do this 10 times then stop
                print(f"\n--- Cycle {i+1}/10 ---")

                

                time.sleep(random.uniform(4,7))

                bot.scroll_feed()

                time.sleep(random.uniform(3,2))

                bot.scroll_feed()

                if random.choice([True, False]):
                    bot.scroll_feed()

                    time.sleep(random.uniform(3,7))

                if random.choice([True, False]):
                    bot.scroll_feed()

                    time.sleep(random.uniform(3,7))


                    


                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("like")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")


                    time.sleep(random.uniform(4,7))

                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("reply")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")


                    time.sleep(random.uniform(4,7))

                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("grok")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")


                    time.sleep(random.uniform(4,7))

                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("like")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")


                time.sleep(random.uniform(4,7))
                if random.choice([True, False]):
    
            # 2. Read
                    text = bot.extract_intelligence_x()
    
            # 3. Decide
                    if text != None :
                # 4. Click Comment Button (Triangulation)
            # Note: You need a function that specifically clicks the comment icon, 
            # NOT the heart. Use the offset logic we discussed!
                        bot.tap_comment_btn_x() 
                        print("tapped on comment btn")

                        reply_text =  brain.query_llm(text)

                        clean_text = bot.clean_text_for_adb(reply_text)
        
                # 5. Execute the Speech
                        bot.post_comment_x(clean_text)
                        
        
                    else:
            # Just Like
                        bot.double_tap_like()
            
            # B. Human Pause (The Observation)
            # Sleep between 5 to 12 seconds (Randomly)
                        sleep_time = random.uniform(5, 12)


                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("bookmark")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")



            
                if random.choice([True, False]):
                    bot.double_tap_like_x()

                sleep_time = random.uniform(5, 12)


                try:


                    x,y = bot.find_element_coordinates_lkdn_comment("share")
                    print(f"like location are {x} , {y} ")
                except Exception as e :
                    print(f"{e}")

        except KeyboardInterrupt:
            print("\n[!] Manual Override. Shutting down.")







    

            
        
        


# --- EXECUTION ---
if __name__ == "__main__":
    bot = SentinelMotor()
    
    # 1. Wake the beast
    bot.wake_up()
    
    # 2. Open Instagram (Resource Acquisition Field)
    #bot.launch_app("instagram")

    bot.start_twitter()
    

    #bot.scroll_feed()


   

    
    
    print("[*] Mission Complete. Returning to Void.")
