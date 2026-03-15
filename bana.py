
# import cv2
# import numpy as np
# from ultralytics import YOLO
# import os

# # --- โหลดโมเดล ---
# model = None
# try:
#     model_path = os.path.join(os.path.dirname(__file__), "best.pt") 
#     model = YOLO(model_path) 
#     print(f"Model loaded from {model_path}")
# except:
#     try:
#         model = YOLO("best.pt")
#         model.to('cpu')
#         print("Model loaded from best.pt")
#     except:
#         print("Error: best.pt not found.")

# def detect_banana(image_path):
#     if model is None:
#         return [], os.path.join("static", "error_processing.jpg")

#     img = cv2.imread(image_path)
#     if img is None:
#         return [], os.path.join("static", "error_processing.jpg")

#     output_path = os.path.join("static", "result.jpg")

#     try:
#         results_list = model.predict(source=image_path, imgsz=320, conf=0.25, iou=0.45, verbose=False)
#         results = results_list[0]
#         labels_info = []

#         if len(results.boxes) == 0:
#             cv2.imwrite(output_path, img)
#             return [], output_path

#         H_img, W_img = img.shape[:2]

#         for i, box in enumerate(results.boxes.data):
#             x1, y1, x2, y2 = map(int, box[:4])
#             conf = float(box[4])
            
#             # Crop กรอบกล้วย
#             pad = 5
#             x1_show, y1_show = max(0, x1-pad), max(0, y1-pad)
#             x2_show, y2_show = min(W_img, x2+pad), min(H_img, y2+pad)
            
#             # --- Center Crop (เจาะไข่แดง) ---
#             w_box, h_box = x2 - x1, y2 - y1
#             cx1 = int(x1 + w_box * 0.20)
#             cy1 = int(y1 + h_box * 0.20)
#             cx2 = int(x2 - w_box * 0.20)
#             cy2 = int(y2 - h_box * 0.20)
            
#             if cx2 <= cx1 or cy2 <= cy1:
#                 crop_analyze = img[y1:y2, x1:x2]
#             else:
#                 crop_analyze = img[cy1:cy2, cx1:cx2]

#             if crop_analyze.size == 0: continue

#             # --- PROCESS COLORS ---
#             hsv = cv2.cvtColor(crop_analyze, cv2.COLOR_BGR2HSV)
#             total_pixels = crop_analyze.shape[0] * crop_analyze.shape[1]
            
#             # 1. Mask รวม (เอาเฉพาะเนื้อกล้วย ตัดพื้นหลัง)
#             # Hue 0-110, Sat > 25, Val > 45
#             mask_skin = cv2.inRange(hsv, np.array([0, 25, 45]), np.array([110, 255, 255]))
            
#             if cv2.countNonZero(mask_skin) < 50:
#                 label = "ripe"
#             else:
#                 # 2. แยกองค์ประกอบสี (Color Components)
                
#                 # A. สีเขียว (Strict Green): Hue 32 - 100 
#                 # (ขยับเริ่มที่ 32 เพื่อไม่ให้กินสีเหลืองสด)
#                 mask_green = cv2.inRange(hsv, np.array([32, 20, 20]), np.array([100, 255, 255]))
#                 mask_green = cv2.bitwise_and(mask_green, mask_skin)
#                 green_pixels = cv2.countNonZero(mask_green)

#                 # B. สีเหลือง (Strict Yellow): Hue 10 - 32
#                 mask_yellow = cv2.inRange(hsv, np.array([10, 20, 60]), np.array([32, 255, 255]))
#                 mask_yellow = cv2.bitwise_and(mask_yellow, mask_skin)
#                 yellow_pixels = cv2.countNonZero(mask_yellow)

#                 # C. สีเน่า/ดำ (Rotten/Dark):
#                 mask_dark = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 90]))
#                 mask_dark = cv2.bitwise_and(mask_dark, mask_skin)
#                 dark_pixels = cv2.countNonZero(mask_dark)

#                 # D. จุด (Spots) สำหรับ Overripe:
#                 mask_spots = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([25, 255, 160]))
#                 mask_spots = cv2.bitwise_and(mask_spots, mask_skin)
#                 spot_pixels = cv2.countNonZero(mask_spots)

#                 # --- คำนวณสัดส่วนบนผิว (Skin Ratio) ---
#                 # เราจะดูแค่ "พื้นที่ผิว" (เขียว + เหลือง) ไม่เทียบกับพื้นหลัง
#                 skin_surface = green_pixels + yellow_pixels
#                 if skin_surface == 0: skin_surface = 1 # กันหารศูนย์

#                 green_fraction = green_pixels / skin_surface   # สัดส่วนเขียวต่อผิวทั้งหมด
#                 dark_ratio = dark_pixels / total_pixels        # สัดส่วนเน่าต่อทั้งภาพ
#                 spot_ratio = spot_pixels / total_pixels

#                 print(f"🍌 #{i}: G-Frac={green_fraction:.2f}, Dark={dark_ratio:.2f}")

#                 # --- 🧠 FINAL LOGIC (Relative Check) ---
                
#                 # 1. เช็คเน่า (Rotten) - ดำเกินครึ่ง
#                 if dark_ratio > 0.45:
#                     label = "rotten"

#                 # 2. เช็คตระกูลดิบ (ดูจากสัดส่วนเขียวบนผิว)
#                 # ถ้าผิวเป็นสีเขียวเกิน 80% -> Raw
#                 elif green_fraction > 0.80:
#                     label = "raw"
                
#                 # ถ้าผิวมีสีเขียวปน เกิน 20% -> Unripe
#                 # (รูปผ้าขนหนูจะมีเขียวปนประมาณ 30-40% จะตกช่องนี้)
#                 # (รูปกล้วยเหลือง จะมีเขียวปน < 10% จะหลุดไปช่องล่าง)
#                 elif green_fraction > 0.20:
#                     label = "unripe"

#                 # 3. เช็คตระกูลสุก (เหลืองนำ)
#                 else:
#                     # เหลืองนำ แต่มีจุดเยอะ -> Overripe
#                     if spot_ratio > 0.15 or dark_ratio > 0.15:
#                         label = "overripe"
#                     # เหลืองสวย จุดน้อย -> Ripe
#                     else:
#                         label = "ripe"

#             # --- วาดรูป ---
#             color_map = {
#                 "raw": (0, 255, 255), "unripe": (0, 165, 255),
#                 "ripe": (0, 255, 0), "overripe": (0, 100, 255),
#                 "rotten": (0, 0, 255)
#             }
#             color = color_map.get(label, (255, 255, 255))
            
#             cv2.rectangle(img, (x1_show, y1_show), (x2_show, y2_show), color, 2)
            
#             label_text = f"{label} ({conf:.2f})"
#             (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
#             cv2.rectangle(img, (x1_show, y1_show-25), (x1_show+tw, y1_show), color, -1)
#             cv2.putText(img, label_text, (x1_show, y1_show-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,50,50), 2)

#             labels_info.append({"index": i+1, "label": label, "confidence": round(conf, 2)})

#         cv2.imwrite(output_path, img)
#         return labels_info, output_path

#     except Exception as e:
#         print(f"Error: {e}")
#         return [], os.path.join("static", "error_processing.jpg")

import cv2
import numpy as np
import os

# ลบการโหลด model ด้านนอกทิ้งทั้งหมด เพื่อไม่ให้กิน RAM ตอนเปิดเครื่อง
model = None 

def detect_banana(image_path):
    # --- ท่าไม้ตายประหยัด RAM: โหลดเฉพาะตอนจะใช้งาน (Lazy Loading) ---
    from ultralytics import YOLO
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), "best.pt")
        # โหลดโมเดล และบังคับใช้ CPU ทันที
        current_model = YOLO(model_path)
        current_model.to('cpu') 
        print(f"Model loaded temporarily for analysis.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return [], os.path.join("static", "error_processing.jpg")

    img = cv2.imread(image_path)
    if img is None:
        return [], os.path.join("static", "error_processing.jpg")

    output_path = os.path.join("static", "result.jpg")

    try:
        # ใช้ imgsz=320 เพื่อประหยัด RAM ตอนทำ Prediction
        results_list = current_model.predict(source=image_path, imgsz=320, conf=0.55, iou=0.45, verbose=False)
        results = results_list[0]
        labels_info = []

        if len(results.boxes) == 0:
            cv2.imwrite(output_path, img)
            return [], output_path

        H_img, W_img = img.shape[:2]

        for i, box in enumerate(results.boxes.data):
            x1, y1, x2, y2 = map(int, box[:4])
            conf = float(box[4])
            
            # Crop กรอบกล้วย
            pad = 5
            x1_show, y1_show = max(0, x1-pad), max(0, y1-pad)
            x2_show, y2_show = min(W_img, x2+pad), min(H_img, y2+pad)
            
            # --- Center Crop (เจาะไข่แดง) ---
            w_box, h_box = x2 - x1, y2 - y1
            cx1 = int(x1 + w_box * 0.20)
            cy1 = int(y1 + h_box * 0.20)
            cx2 = int(x2 - w_box * 0.20)
            cy2 = int(y2 - h_box * 0.20)
            
            if cx2 <= cx1 or cy2 <= cy1:
                crop_analyze = img[y1:y2, x1:x2]
            else:
                crop_analyze = img[cy1:cy2, cx1:cx2]

            if crop_analyze.size == 0: continue

            # --- PROCESS COLORS ---
            hsv = cv2.cvtColor(crop_analyze, cv2.COLOR_BGR2HSV)
            total_pixels = crop_analyze.shape[0] * crop_analyze.shape[1]
            
            # 1. Mask รวม (เอาเฉพาะเนื้อกล้วย ตัดพื้นหลัง)
            mask_skin = cv2.inRange(hsv, np.array([0, 25, 45]), np.array([110, 255, 255]))
            
            if cv2.countNonZero(mask_skin) < 50:
                label = "ripe"
            else:
                # 2. แยกองค์ประกอบสี
                mask_green = cv2.inRange(hsv, np.array([32, 20, 20]), np.array([100, 255, 255]))
                mask_green = cv2.bitwise_and(mask_green, mask_skin)
                green_pixels = cv2.countNonZero(mask_green)

                mask_yellow = cv2.inRange(hsv, np.array([10, 20, 60]), np.array([32, 255, 255]))
                mask_yellow = cv2.bitwise_and(mask_yellow, mask_skin)
                yellow_pixels = cv2.countNonZero(mask_yellow)

                mask_dark = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 90]))
                mask_dark = cv2.bitwise_and(mask_dark, mask_skin)
                dark_pixels = cv2.countNonZero(mask_dark)

                mask_spots = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([25, 255, 160]))
                mask_spots = cv2.bitwise_and(mask_spots, mask_skin)
                spot_pixels = cv2.countNonZero(mask_spots)

                skin_surface = green_pixels + yellow_pixels
                if skin_surface == 0: skin_surface = 1

                green_fraction = green_pixels / skin_surface
                dark_ratio = dark_pixels / total_pixels
                spot_ratio = spot_pixels / total_pixels

                # --- LOGIC การจำแนก ---
                if dark_ratio > 0.45:
                    label = "rotten"
                elif green_fraction > 0.80:
                    label = "raw"
                elif green_fraction > 0.20:
                    label = "unripe"
                else:
                    if spot_ratio > 0.15 or dark_ratio > 0.15:
                        label = "overripe"
                    else:
                        label = "ripe"

            # --- วาดรูป ---
            color_map = {
                "raw": (0, 255, 255), "unripe": (0, 165, 255),
                "ripe": (0, 255, 0), "overripe": (0, 100, 255),
                "rotten": (0, 0, 255)
            }
            color = color_map.get(label, (255, 255, 255))
            
            cv2.rectangle(img, (x1_show, y1_show), (x2_show, y2_show), color, 2)
            
            label_text = f"{label} ({conf:.2f})"
            (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img, (x1_show, y1_show-25), (x1_show+tw, y1_show), color, -1)
            cv2.putText(img, label_text, (x1_show, y1_show-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,50,50), 2)

            labels_info.append({"index": i+1, "label": label, "confidence": round(conf, 2)})

        cv2.imwrite(output_path, img)
        
        # เคลียร์ตัวแปรทิ้งเพื่อคืน RAM ให้ได้มากที่สุด
        del current_model
        
        return labels_info, output_path

    except Exception as e:
        print(f"Error during detection: {e}")
        return [], os.path.join("static", "error_processing.jpg")