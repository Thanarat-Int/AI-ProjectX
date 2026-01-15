# bot.py
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from data import DATA_MANAGER
from brain import AIBrain

class FormBot:
    def __init__(self, url, loops, log_callback, headless=False, use_faker=False, thread_id=1, target_groups=None):
        self.url = url
        self.loops = loops
        self.log = log_callback
        self.headless = headless
        self.use_faker = use_faker
        self.thread_id = thread_id
        self.target_groups = target_groups
        self.on_persona_change = None # Callback for UI updates
        self.is_running = False
        self.brain = AIBrain()
        self.driver = None

    def _human_delay(self, min_sec=0.1, max_sec=0.4):
        """Random delay to simulate human hesitation (Turbo Mode)"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _human_scroll(self, element):
        """Smooth scroll to element"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(random.uniform(0.2, 0.4)) 
        except:
            pass

    def _human_click(self, element):
        """Move cursor to element and click"""
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            actions.click().perform()
        except:
             self.driver.execute_script("arguments[0].click();", element)

    def _human_type(self, element, text):
        """Type text character by character"""
        try:
            self._human_scroll(element) # Scroll to element
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            
            # Fast typing for Turbo Mode
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.01, 0.05)) 
        except Exception as e:
            self.log(f"⚠️ Typing Error: {e}")

    def run(self):
        self.is_running = True
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
            # Headless optimization
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception as e:
            self.log(f"❌ Driver Error: {e}")
            return

        try:
            for i in range(self.loops):
                if not self.is_running: break
                
                # 1. Random Persona based on Target Groups
                candidate_personas = DATA_MANAGER.get_personas_by_groups(self.target_groups)
                if not candidate_personas:
                    self.log("⚠️ No personas found for selected groups! Using ALL.")
                    candidate_personas = DATA_MANAGER.personas
                    
                current_persona = random.choice(candidate_personas)
                
                # Notify UI
                if self.on_persona_change:
                    self.on_persona_change(self.thread_id, current_persona)

                self.log(f"----------------------------------------")
                self.log(f"🔄 Round {i+1}/{self.loops} : 👤 {current_persona['name']}")
                
                try:
                    self.driver.get(self.url)
                    self._human_delay(0.5, 1.0)
                except:
                     self.log("⚠️ Connection Error, retrying...")
                     time.sleep(2)
                     continue

                # === Filling Loop ===
                page_count = 1
                while True:
                    try:
                        self.log(f"📄 Page {page_count}: Scanning...")
                        
                        # A. Choice Interaction
                        all_questions = self.driver.find_elements(By.CSS_SELECTOR, "div[role='radiogroup'], div[role='list'], div[jscontroller], div[role='presentation']")
                        visible_questions = [g for g in all_questions if g.is_displayed()]
                        
                        unique_questions = {}
                        for q in visible_questions:
                            if q.id not in unique_questions: unique_questions[q.id] = q
                        question_list = list(unique_questions.values())
                        
                        answered_in_pass = 0
                        for group in question_list:
                             # Check if already answered
                            try:
                                checked_options = group.find_elements(By.CSS_SELECTOR, "div[role='radio'][aria-checked='true'], div[role='checkbox'][aria-checked='true']")
                                if checked_options: continue 

                                self._human_scroll(group)
                                
                                q_text = group.get_attribute("aria-label") or "General Question"
                                opts = group.find_elements(By.CSS_SELECTOR, "div[role='radio'], div[role='checkbox']")
                                
                                opt_data = []
                                for o in opts:
                                    txt = o.get_attribute("data-value") or o.get_attribute("aria-label") or ""
                                    if not txt:
                                        try: txt = o.find_element(By.XPATH, "./..").text
                                        except: pass
                                    
                                    # Strict Other Filter (Unless we handle text input later)
                                    if txt and not any(x in txt for x in ["อื่น", "Other", "ระบุ", "other"]):
                                        val = o.get_attribute("data-value") or ""
                                        if "__other_option__" not in val:
                                            opt_data.append((txt, o))
                                
                                if not opt_data: continue

                                chosen_text = self.brain.decide_answer(q_text, [d[0] for d in opt_data], current_persona)
                                
                                clicked_any = False
                                for txt, elem in opt_data:
                                    if txt == chosen_text:
                                        self._human_click(elem)
                                        clicked_any = True
                                        break
                                
                                if not clicked_any and opt_data:
                                    rand_opt = random.choice(opt_data)
                                    self._human_click(rand_opt[1])

                                answered_in_pass += 1
                                self._human_delay(0.1, 0.3)

                            except Exception as e: continue

                        # B. Text Input Interaction
                        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea, div[role='textbox']")
                        visible_text_inputs = [t for t in text_inputs if t.is_displayed()]
                        
                        for t_input in visible_text_inputs:
                            # Skip if already filled
                            if t_input.get_attribute("value") or t_input.text: continue

                            # Try to find label
                            try:
                                q_label = t_input.find_element(By.XPATH, "./ancestor::div[contains(@role, 'listitem')]//div[contains(@role, 'heading')]").text
                            except:
                                q_label = "Free Text Question"

                            # Ask Brain (Logic handles Faker check)
                            response_text = self.brain.decide_text_input(q_label, current_persona, self.use_faker)
                            
                            if response_text:
                                self.log(f"✍️ Typing: {response_text[:15]}...")
                                self._human_type(t_input, response_text)
                                answered_in_pass += 1
                        
                        if answered_in_pass > 0: self.log(f"⚡ Answered {answered_in_pass} items")

                        # C. Navigation / Submit
                        submit_btns = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button'][data-value='Submit']")
                        if not submit_btns:
                             for b in self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']"):
                                 if b.text in ["Submit", "ส่ง"]: 
                                     submit_btns = [b]; break
                        
                        if submit_btns:
                            self.log(f"🚀 {current_persona['name']} Submitting!")
                            self._human_scroll(submit_btns[0])
                            self._human_click(submit_btns[0])
                            time.sleep(2) 
                            break
                        
                        next_btns = [b for b in self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']") if b.text in ["Next", "ถัดไป"] and b.is_displayed()]
                        if next_btns:
                            self._human_scroll(next_btns[0])
                            self._human_click(next_btns[0])
                            self.log("➡️ Next Page...")
                            page_count += 1
                            time.sleep(1.5)
                        else:
                            time.sleep(2)

                    except Exception as e:
                        self.log(f"⚠️ Error: {e}")
                        time.sleep(2)
                
                time.sleep(2) 

        except Exception as e:
            self.log(f"❌ Critical Error: {e}")
        finally:
            if self.driver: 
                try: self.driver.quit()
                except: pass
            if not self.headless: # Final log only if visible
                self.log("🏁 Thread Finished")