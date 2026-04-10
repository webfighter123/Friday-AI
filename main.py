import cv2
import mediapipe as mp
import pyautogui
import time

# --- INITIALIZE VISION ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

def monitor_hand():
    cap = cv2.VideoCapture(0)
    print("SYSTEM: Vision Bridge Online. Waiting for gestures...")
    
    while cap.isOpened():
        success, img = cap.read()
        if not success: continue
        
        img = cv2.flip(img, 1)
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Logic to detect a Fist (All finger tips below mid-joints)
                # 8: Index, 12: Middle, 16: Ring, 20: Pinky
                is_fist = True
                for tip in [8, 12, 16, 20]:
                    if hand_lms.landmark[tip].y < hand_lms.landmark[tip-2].y:
                        is_fist = False
                
                if is_fist:
                    print("COMMAND: FIST DETECTED -> CLOSING TAB")
                    pyautogui.hotkey('ctrl', 'w')
                    time.sleep(1) # Prevent accidental double-closing
                
                # Draw the landmarks so you can see what Butter sees
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Butter Vision Link", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor_hand()
