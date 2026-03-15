# import cv2
# import numpy as np
# from ultralytics import YOLO
# import os

# # โหลดโมเดล YOLO ที่ถูก Fine-tuned แล้ว (best.pt)
# model = None
# try:
#     model = YOLO("best.pt")  # ตรวจสอบให้แน่ใจว่า best.pt อยู่โฟลเดอร์เดียวกับไฟล์นี้
#     print("Fine-tuned YOLO model loaded successfully.")
# except Exception as e:
#     print(f"Error loading fine-tuned YOLO model (best.pt): {e}")
#     print("Please ensure 'best.pt' is in the same directory as this script.")

# def detect_banana(image_path):
#     if model is None:
#         print("Error: YOLO model is not loaded. Cannot perform detection.")
#         return [], os.path.join("static", "error_processing.jpg")

#     img = cv2.imread(image_path)
#     if img is None:
#         print(f"Error: Could not load image from {image_path}")
#         return [], os.path.join("static", "error_processing.jpg")

#     output_path = os.path.join("static", "result.jpg")

#     try:
#         results_list = model.predict(img, conf=0.5, iou=0.45, verbose=False)
#         results = results_list[0]
#         labels_info = []

#         if len(results.boxes) == 0:
#             print("No bananas found. Saving original image.")
#             cv2.imwrite(output_path, img)
#             return [], output_path

#         H_img, W_img = img.shape[:2]

#         for i, box in enumerate(results.boxes.data):
#             x1, y1, x2, y2 = map(int, box[:4])
#             conf = float(box[4])
#             cls_id = int(box[5])

#             # ป้องกันไม่ให้ออกนอกขอบภาพ
#             x1, y1 = max(0, x1), max(0, y1)
#             x2, y2 = min(W_img - 1, x2), min(H_img - 1, y2)

#             # หดกรอบ ~5%
#             bw, bh = max(1, x2 - x1), max(1, y2 - y1)
#             padx, pady = max(1, int(0.05 * bw)), max(1, int(0.05 * bh))
#             xi1 = min(max(0, x1 + padx), W_img - 2)
#             yi1 = min(max(0, y1 + pady), H_img - 2)
#             xi2 = max(min(x2 - padx, W_img - 1), xi1 + 1)
#             yi2 = max(min(y2 - pady, H_img - 1), yi1 + 1)

#             crop = img[yi1:yi2, xi1:xi2]
#             if crop.size == 0:
#                 continue

#             # ============== BEGIN: HSV + spot detection block ==============
#             hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
#             H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

#             base_mask = np.where((S > 25) | ((V < 230) & (V > 20)), 255, 0).astype(np.uint8)
#             base_mask = cv2.morphologyEx(base_mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8), 1)
#             base_mask = cv2.morphologyEx(base_mask, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8), 2)
#             m = base_mask > 0

#             brown = ((H >= 8) & (H <= 30) & (S >= 60) & (V <= 170) & m)
#             black = ((V <= 60) & m)

#             spot_kernel = np.ones((3,3), np.uint8)
#             brown_clean = cv2.morphologyEx((brown.astype(np.uint8) * 255), cv2.MORPH_OPEN, spot_kernel, iterations=1)
#             black_clean = cv2.morphologyEx((black.astype(np.uint8) * 255), cv2.MORPH_OPEN, spot_kernel, iterations=1)
#             spot_mask = cv2.bitwise_or(brown_clean, black_clean)

#             num_labels, labels_cc, stats, _ = cv2.connectedComponentsWithStats((spot_mask>0).astype(np.uint8), connectivity=8)
#             spot_area = int((spot_mask>0).sum())
#             fg_area   = int(m.sum())
#             spot_frac = (spot_area / max(fg_area, 1))
#             spot_cnt  = int(((stats[1:, cv2.CC_STAT_AREA] >= 15) & (stats[1:, cv2.CC_STAT_AREA] <= 2000)).sum())

#             H_vals, S_vals, V_vals = H[m], S[m], V[m]
#             H_mean = float(np.mean(H_vals))   if H_vals.size else 0.0
#             H_med  = float(np.median(H_vals)) if H_vals.size else 0.0
#             S_mean = float(np.mean(S_vals))   if S_vals.size else 0.0
#             V_mean = float(np.mean(V_vals))   if V_vals.size else 0.0
#             V_std  = float(np.std(V_vals))    if V_vals.size else 0.0

#             dark_frac      = float(np.mean((V_vals < 80)))  if V_vals.size else 0.0
#             very_dark_frac = float(np.mean((V_vals < 50)))  if V_vals.size else 0.0
#             lowsat_frac    = float(np.mean((S_vals < 60)))  if V_vals.size else 0.0

# # 🔎 Debug print
#             print(f"Banana {i+1}: H_mean={H_mean:.1f}, H_med={H_med:.1f}, "
#             f"S_mean={S_mean:.1f}, V_mean={V_mean:.1f}, dark_frac={dark_frac:.2f}")           

#             edges = cv2.Canny(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), 50, 150)
#             edge_density = float(np.mean((edges > 0) & m)) if edges.size else 0.0

#             label = model.names[cls_id]

#             is_really_rotten = (
#                 very_dark_frac >= 0.35 or
#                 (dark_frac >= 0.65 and lowsat_frac >= 0.60) or
#                 ((V_mean < 85 and S_mean < 70) and edge_density < 0.02)
#             )

#             is_spotty_overripe = (
#                 (spot_frac >= 0.035) or
#                 (spot_cnt  >= 8)    or
#                 (dark_frac >= 0.20 and edge_density >= 0.02)
#             )

#             if is_really_rotten:
#                 label = "rotten"
#             elif is_spotty_overripe:
#                 label = "overripe"
#             else:
#                 H_YELLOW_MIN, H_YELLOW_MAX = 15, 38
#                 H_GREEN_MIN,  H_GREEN_MAX  = 38, 85

#                 if H_GREEN_MIN <= H_med < 65 and S_mean > 40 and V_mean > 60:
#                     label = "unripe"
#                 elif 65 <= H_med <= H_GREEN_MAX and S_mean > 35 and V_mean > 55:
#                     label = "raw"
#                 elif H_YELLOW_MIN <= H_med < H_YELLOW_MAX and S_mean > 40 and V_mean > 60:
#                     label = "ripe"
#                 else:
#                     label = "rotten" if dark_frac >= 0.55 else "overripe"

#             if label == "unripe" and is_spotty_overripe and conf >= 0.50:
#                 label = "overripe"
#             # ============== END: HSV + spot detection block ==============

#             # สีของกรอบตาม label
#             color = (255, 255, 255)
#             if label == "raw":
#                 color = (0, 255, 255)
#             elif label == "unripe":
#                 color = (0, 165, 255)
#             elif label == "ripe":
#                 color = (0, 255, 0)
#             elif label == "overripe":
#                 color = (60, 20, 140)
#             elif label == "rotten":
#                 color = (0, 0, 255)

#             cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(img, f"{label} ({conf:.2f})", (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

#             labels_info.append({
#                 "index": i + 1,
#                 "label": label,
#                 "confidence": round(conf, 2)
#             })

#         cv2.imwrite(output_path, img)
#         print(f"Output image saved to {output_path}")
#         return labels_info, output_path

#     except Exception as e:
#         print(f"Error during banana detection: {e}")
#         return [], os.path.join("static", "error_processing.jpg")
import cv2
import numpy as np
from ultralytics import YOLO
import os

# --- โหลดโมเดล ---
model = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "best.pt") 
    model = YOLO(model_path) 
    print(f"Model loaded from {model_path}")
except:
    try:
        model = YOLO("best.pt")
        model.to('cpu')
        print("Model loaded from best.pt")
    except:
        print("Error: best.pt not found.")

def detect_banana(image_path):
    if model is None:
        return [], os.path.join("static", "error_processing.jpg")

    img = cv2.imread(image_path)
    if img is None:
        return [], os.path.join("static", "error_processing.jpg")

    output_path = os.path.join("static", "result.jpg")

    try:
        results_list = model.predict(source=image_path, imgsz=320, conf=0.25, iou=0.45, verbose=False)
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
            # Hue 0-110, Sat > 25, Val > 45
            mask_skin = cv2.inRange(hsv, np.array([0, 25, 45]), np.array([110, 255, 255]))
            
            if cv2.countNonZero(mask_skin) < 50:
                label = "ripe"
            else:
                # 2. แยกองค์ประกอบสี (Color Components)
                
                # A. สีเขียว (Strict Green): Hue 32 - 100 
                # (ขยับเริ่มที่ 32 เพื่อไม่ให้กินสีเหลืองสด)
                mask_green = cv2.inRange(hsv, np.array([32, 20, 20]), np.array([100, 255, 255]))
                mask_green = cv2.bitwise_and(mask_green, mask_skin)
                green_pixels = cv2.countNonZero(mask_green)

                # B. สีเหลือง (Strict Yellow): Hue 10 - 32
                mask_yellow = cv2.inRange(hsv, np.array([10, 20, 60]), np.array([32, 255, 255]))
                mask_yellow = cv2.bitwise_and(mask_yellow, mask_skin)
                yellow_pixels = cv2.countNonZero(mask_yellow)

                # C. สีเน่า/ดำ (Rotten/Dark):
                mask_dark = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 90]))
                mask_dark = cv2.bitwise_and(mask_dark, mask_skin)
                dark_pixels = cv2.countNonZero(mask_dark)

                # D. จุด (Spots) สำหรับ Overripe:
                mask_spots = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([25, 255, 160]))
                mask_spots = cv2.bitwise_and(mask_spots, mask_skin)
                spot_pixels = cv2.countNonZero(mask_spots)

                # --- คำนวณสัดส่วนบนผิว (Skin Ratio) ---
                # เราจะดูแค่ "พื้นที่ผิว" (เขียว + เหลือง) ไม่เทียบกับพื้นหลัง
                skin_surface = green_pixels + yellow_pixels
                if skin_surface == 0: skin_surface = 1 # กันหารศูนย์

                green_fraction = green_pixels / skin_surface   # สัดส่วนเขียวต่อผิวทั้งหมด
                dark_ratio = dark_pixels / total_pixels        # สัดส่วนเน่าต่อทั้งภาพ
                spot_ratio = spot_pixels / total_pixels

                print(f"🍌 #{i}: G-Frac={green_fraction:.2f}, Dark={dark_ratio:.2f}")

                # --- 🧠 FINAL LOGIC (Relative Check) ---
                
                # 1. เช็คเน่า (Rotten) - ดำเกินครึ่ง
                if dark_ratio > 0.45:
                    label = "rotten"

                # 2. เช็คตระกูลดิบ (ดูจากสัดส่วนเขียวบนผิว)
                # ถ้าผิวเป็นสีเขียวเกิน 80% -> Raw
                elif green_fraction > 0.80:
                    label = "raw"
                
                # ถ้าผิวมีสีเขียวปน เกิน 20% -> Unripe
                # (รูปผ้าขนหนูจะมีเขียวปนประมาณ 30-40% จะตกช่องนี้)
                # (รูปกล้วยเหลือง จะมีเขียวปน < 10% จะหลุดไปช่องล่าง)
                elif green_fraction > 0.20:
                    label = "unripe"

                # 3. เช็คตระกูลสุก (เหลืองนำ)
                else:
                    # เหลืองนำ แต่มีจุดเยอะ -> Overripe
                    if spot_ratio > 0.15 or dark_ratio > 0.15:
                        label = "overripe"
                    # เหลืองสวย จุดน้อย -> Ripe
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
        return labels_info, output_path

    except Exception as e:
        print(f"Error: {e}")
        return [], os.path.join("static", "error_processing.jpg")