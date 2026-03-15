# from flask import Flask, render_template, request
# from bana import detect_banana
# import os

# app = Flask(__name__)
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         image = request.files["image"]
#         if image:
#             path = os.path.join(UPLOAD_FOLDER, image.filename)
#             image.save(path)

#             results, output_path = detect_banana(path)
#             return render_template("result.html", results=results, image_path=output_path)

#     return render_template("index.html")

# if __name__ == "__main__":
#     app.run(debug=True)

# from flask import Flask, render_template, request, url_for, redirect
# import os
# # ตรวจสอบให้แน่ใจว่า bana.py อยู่ในไดเรกทอรีเดียวกัน หรืออยู่ใน PYTHONPATH
# from bana import detect_banana, model as bana_model # import model object ด้วย

# app = Flask(__name__)

# # กำหนดโฟลเดอร์สำหรับอัปโหลดไฟล์ชั่วคราว
# UPLOAD_FOLDER = "uploads"
# # กำหนดโฟลเดอร์สำหรับไฟล์ static (เช่น รูปภาพผลลัพธ์)
# STATIC_FOLDER = "static"

# # สร้างโฟลเดอร์ถ้ายังไม่มี
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(STATIC_FOLDER, exist_ok=True)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     print("Request received!") # Debug: ตรวจสอบว่ามี Request เข้ามา
#     if request.method == "POST":
#         print("POST request detected.") # Debug: ตรวจสอบว่าเป็น POST request

#         # ตรวจสอบว่ามีการส่งไฟล์มาหรือไม่
#         if "image" not in request.files:
#             print("Error: 'image' file not found in request.files") # Debug: ไม่พบไฟล์
#             return render_template("index.html", error_message="กรุณาเลือกไฟล์ภาพกล้วย")

#         image = request.files["image"]
#         print(f"File object received: {image}") # Debug: แสดงข้อมูล object ของไฟล์

#         # ตรวจสอบว่าไฟล์ที่ส่งมามีชื่อไฟล์หรือไม่ (ป้องกันกรณีผู้ใช้ไม่ได้เลือกไฟล์)
#         if image.filename == "":
#             print("Error: No file selected (filename is empty)") # Debug: ชื่อไฟล์ว่างเปล่า
#             return render_template("index.html", error_message="กรุณาเลือกไฟล์ภาพกล้วย")

#         if image:
#             print(f"File selected: {image.filename}") # Debug: แสดงชื่อไฟล์ที่เลือก

#             # สร้างเส้นทางสำหรับบันทึกไฟล์ที่อัปโหลดชั่วคราว
#             # ใช้ os.path.basename เพื่อป้องกันปัญหาเรื่อง path ที่อาจมี directory
#             upload_path = os.path.join(UPLOAD_FOLDER, os.path.basename(image.filename))
#             print(f"Attempting to save file to: {upload_path}") # Debug: แสดง path ที่จะบันทึก

#             try:
#                 image.save(upload_path)
#                 print(f"File saved successfully to {upload_path}") # Debug: บันทึกไฟล์สำเร็จ
#             except Exception as e:
#                 print(f"Error saving file: {e}") # Debug: เกิดข้อผิดพลาดในการบันทึกไฟล์
#                 return render_template("index.html", error_message=f"ไม่สามารถบันทึกไฟล์ได้: {e}")

#             try:
#                 # ตรวจสอบว่าโมเดลจาก bana.py โหลดสำเร็จหรือไม่
#                 if bana_model is None:
#                     print("Error: YOLO model was not loaded in bana.py. Returning model error.")
#                     return render_template("index.html", error_message="โมเดลวิเคราะห์ไม่พร้อมใช้งาน กรุณาตรวจสอบไฟล์โมเดล (yolo11n.pt)")

#                 # เรียกใช้ฟังก์ชัน detect_banana จาก bana.py
#                 # bana.py จะบันทึกภาพผลลัพธ์ไปที่ 'static/result.jpg'
#                 print(f"Calling detect_banana with image path: {upload_path}") # Debug: กำลังเรียก detect_banana
#                 results, output_file_name = detect_banana(upload_path)
#                 print(f"detect_banana returned results: {results}, output_file_name: {output_file_name}") # Debug: แสดงผลลัพธ์จาก detect_banana

#                 # ตรวจสอบว่า output_file_name เป็น string และไม่ใช่ None
#                 if not isinstance(output_file_name, str) or not output_file_name:
#                     print("Error: output_file_name from detect_banana is invalid.") # Debug: output_file_name ไม่ถูกต้อง
#                     return render_template("index.html", error_message="เกิดข้อผิดพลาดในการสร้างภาพผลลัพธ์")

#                 # แยกชื่อไฟล์ออกจาก path เพื่อใช้กับ url_for
#                 # output_file_name จาก bana.py คือ "static/result.jpg"
#                 # เราต้องการแค่ "result.jpg"
#                 static_image_filename = os.path.basename(output_file_name)

#                 # สร้าง URL สำหรับเข้าถึงภาพผลลัพธ์ผ่าน Flask static files
#                 # Flask จะเสิร์ฟไฟล์จากโฟลเดอร์ 'static'
#                 image_url = url_for("static", filename=static_image_filename)
#                 print(f"Generated image URL: {image_url}") # Debug: แสดง URL ภาพผลลัพธ์

#                 # ลบไฟล์ที่อัปโหลดชั่วคราวหลังจากประมวลผลเสร็จ (ไม่จำเป็นต้องเก็บไว้)
#                 if os.path.exists(upload_path):
#                     os.remove(upload_path)
#                     print(f"Removed temporary uploaded file: {upload_path}") # Debug: ลบไฟล์ชั่วคราวแล้ว

#                 return render_template("result.html", results=results, image_path=image_url)

#             except Exception as e:
#                 # หากเกิดข้อผิดพลาดในการประมวลผลภาพ
#                 print(f"Error during image processing (detect_banana or related): {e}") # Debug: เกิดข้อผิดพลาดในการประมวลผล
#                 return render_template("index.html", error_message=f"เกิดข้อผิดพลาดในการวิเคราะห์ภาพ: {e}")

#     print("GET request detected or no POST data.") # Debug: เป็น GET request
#     return render_template("index.html")

# if __name__ == "__main__":
#     # เปลี่ยน host เป็น '0.0.0.0' เพื่อรับการเชื่อมต่อจากทุก Network Interface
#     # เปลี่ยน port เป็น 8888 (หรือพอร์ตอื่นที่สูงๆ เช่น 9999)
#     app.run(debug=True, host='0.0.0.0', port=8888)

from flask import Flask, render_template, request, url_for, redirect
import os
# ตรวจสอบให้แน่ใจว่า bana.py อยู่ในไดเรกทอรีเดียวกัน หรืออยู่ใน PYTHONPATH
# และมีการ import 'model as bana_model' เพื่อเข้าถึงโมเดลที่โหลดใน bana.py
from bana import detect_banana, model as bana_model 

app = Flask(__name__)

# กำหนดโฟลเดอร์สำหรับอัปโหลดไฟล์ชั่วคราว
UPLOAD_FOLDER = "uploads"
# กำหนดโฟลเดอร์สำหรับไฟล์ static (เช่น รูปภาพผลลัพธ์)
STATIC_FOLDER = "static"

# สร้างโฟลเดอร์ถ้ายังไม่มี
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)


# ---------- Nutrition & Benefits mapping ----------
RIPENESS_INFO = {
    "raw": {
        "nutrition": "แป้งดิบสูง ย่อยยากกว่า มีแป้งทนย่อย (resistant starch) สูง",
        "benefit": "อิ่มนาน ช่วยควบคุมระดับน้ำตาล แต่ท้องอืดได้"
    },
    "unripe": {
        "nutrition": "คาร์บฯเชิงซ้อนมากกว่า กลูโคสยังไม่สูง ไฟเบอร์ปานกลาง",
        "benefit": "ดีต่อการคุมน้ำตาล มีพรีไบโอติกพอควร"
    },
    "ripe": {
        "nutrition": "พลังงาน ~89 kcal/100g คาร์บฯ ~23g โพแทสเซียมและวิตามิน B6 สูง",
        "benefit": "ให้พลังงานเร็ว เหมาะก่อน/หลังออกกำลังกาย ช่วยระบบขับถ่าย"
    },
    "overripe": {
        "nutrition": "น้ำตาลเดี่ยวสูง ย่อยเร็ว สารต้านอนุมูลอิสระเพิ่มขึ้น",
        "benefit": "ดีต่อการทำเบเกอรี่/สมูทตี้ แต่ควรกินพอดีหากคุมน้ำตาล"
    },
    "rotten": {
        "nutrition": "โภชนาการเสื่อม สีดำ/มีกลิ่น เป็นไปได้ว่ามีจุลินทรีย์ปนเปื้อน",
        "benefit": "ไม่แนะนำให้บริโภค"
    }
}
# ---------------------------------------------------


# @app.route("/", methods=["GET", "POST"])
# def index():
#     results = None 
#     output_file_name = None

#     print("Request received!") # Debug: ตรวจสอบว่ามี Request เข้ามา
#     if request.method == "POST":
#         print("POST request detected.") # Debug: ตรวจสอบว่าเป็น POST request

#         # ตรวจสอบว่ามีการส่งไฟล์มาหรือไม่
#         if "image" not in request.files:
#             print("Error: 'image' file not found in request.files") # Debug: ไม่พบไฟล์
#             return render_template("index.html", error_message="กรุณาเลือกไฟล์ภาพกล้วย")

#         image = request.files[  "image"]
#         print(f"File object received: {image}") # Debug: แสดงข้อมูล object ของไฟล์

#         # ตรวจสอบว่าไฟล์ที่ส่งมามีชื่อไฟล์หรือไม่ (ป้องกันกรณีผู้ใช้ไม่ได้เลือกไฟล์)
#         if image.filename == "":
#             print("Error: No file selected (filename is empty)") # Debug: ชื่อไฟล์ว่างเปล่า
#             return render_template("index.html", error_message="กรุณาเลือกไฟล์ภาพกล้วย")

#         if image:
#             print(f"File selected: {image.filename}") # Debug: แสดงชื่อไฟล์ที่เลือก

#             # สร้างเส้นทางสำหรับบันทึกไฟล์ที่อัปโหลดชั่วคราว
#             # ใช้ os.path.basename เพื่อป้องกันปัญหาเรื่อง path ที่อาจมี directory
#             upload_path = os.path.join(UPLOAD_FOLDER, os.path.basename(image.filename))
#             print(f"Attempting to save file to: {upload_path}") # Debug: แสดง path ที่จะบันทึก

#             try:
#                 image.save(upload_path)
#                 print(f"File saved successfully to {upload_path}") # Debug: บันทึกไฟล์สำเร็จ
#             except Exception as e:
#                 print(f"Error saving file: {e}") # Debug: เกิดข้อผิดพลาดในการบันทึกไฟล์
#                 return render_template("index.html", error_message=f"ไม่สามารถบันทึกไฟล์ได้: {e}")

#             try:
#                 # ตรวจสอบว่าโมเดลจาก bana.py โหลดสำเร็จหรือไม่
#                 # เราใช้ bana_model ที่ import มาจาก bana.py
#                 if bana_model is None:
#                     print("Error: YOLO model was not loaded in bana.py. Returning model error.")
#                     return render_template("index.html", error_message="โมเดลวิเคราะห์ไม่พร้อมใช้งาน กรุณาตรวจสอบไฟล์โมเดล (best.pt) ใน bana.py")

#                 # เรียกใช้ฟังก์ชัน detect_banana จาก bana.py
#                 # bana.py จะบันทึกภาพผลลัพธ์ไปที่ 'static/result.jpg'
#                 print(f"Calling detect_banana with image path: {upload_path}") # Debug: กำลังเรียก detect_banana
#                 results, output_file_name = detect_banana(upload_path)
#                 print(f"detect_banana returned results: {results}, output_file_name: {output_file_name}") # Debug: แสดงผลลัพธ์จาก detect_banana

#                 # ตรวจสอบว่า output_file_name เป็น string และไม่ใช่ None
#                 if not isinstance(output_file_name, str) or not output_file_name:
#                     print("Error: output_file_name from detect_banana is invalid.") # Debug: output_file_name ไม่ถูกต้อง
#                     return render_template("index.html", error_message="เกิดข้อผิดพลาดในการสร้างภาพผลลัพธ์")

#                 # แยกชื่อไฟล์ออกจาก path เพื่อใช้กับ url_for
#                 # output_file_name จาก bana.py คือ "static/result.jpg"
#                 # เราต้องการแค่ "result.jpg"
#                 static_image_filename = os.path.basename(output_file_name)

#                 # สร้าง URL สำหรับเข้าถึงภาพผลลัพธ์ผ่าน Flask static files
#                 # Flask จะเสิร์ฟไฟล์จากโฟลเดอร์ 'static'
#                 image_url = url_for("static", filename=static_image_filename)
#                 print(f"Generated image URL: {image_url}") # Debug: แสดง URL ภาพผลลัพธ์

#                 # ลบไฟล์ที่อัปโหลดชั่วคราวหลังจากประมวลผลเสร็จ (ไม่จำเป็นต้องเก็บไว้)
#                 if os.path.exists(upload_path):
#                     os.remove(upload_path)
#                     print(f"Removed temporary uploaded file: {upload_path}") # Debug: ลบไฟล์ชั่วคราวแล้ว

#                 # ตรวจสอบว่ามีผลลัพธ์การตรวจจับหรือไม่ (ถ้า results เป็น list ว่างเปล่า)
#                 if not results: 
#                     # แสดงข้อความจาก output_file_name (เช่น "ไม่พบกล้วยในภาพ")
#                     # เราส่งเป็น list ของ dict เพื่อให้เข้ากับโครงสร้างของ result.html
#                     return render_template("result.html", results=[{"index": 0, "label": output_file_name, "confidence": 1.0}], image_path=image_url)
#                 else:
#                     return render_template("result.html", results=results, image_path=image_url)

#             except Exception as e:
#                 # หากเกิดข้อผิดพลาดในการประมวลผลภาพ
#                 print(f"Error during image processing (detect_banana or related): {e}") # Debug: เกิดข้อผิดพลาดในการประมวลผล
#                 return render_template("index.html", error_message=f"เกิดข้อผิดพลาดในการวิเคราะห์ภาพ: {e}")

#     print("GET request detected or no POST data.") # Debug: เป็น GET request
#     # เลือกระดับความสุกตัวแรก (ถ้ามีหลายลูก)
#     main_label = results[0]["label"] if results else None

#     nutrition = ""
#     benefit = ""

#     if main_label in RIPENESS_INFO:
#         nutrition = RIPENESS_INFO[main_label]["nutrition"]
#         benefit = RIPENESS_INFO[main_label]["benefit"]

#     return render_template(
#         "result.html",
#         results=results,
#         image_path=image_url,
#         nutrition=nutrition,
#         benefit=benefit
#     )


# (ส่วน import เหมือนเดิม)

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    results = None
    nutrition = ""
    benefit = ""
    message = "" # ✅ ตัวแปรสำหรับข้อความแจ้งเตือน

    if request.method == "POST":
        if "image" not in request.files:
            return render_template("index.html", error_message="ไม่พบไฟล์ภาพ")
        
        image = request.files["image"]
        if image.filename == "":
            return render_template("index.html", error_message="ไม่ได้เลือกไฟล์")

        if image:
            upload_path = os.path.join(UPLOAD_FOLDER, os.path.basename(image.filename))
            try:
                image.save(upload_path)

                if bana_model is None:
                     return render_template("index.html", error_message="Model Error")

                # ส่งเข้า AI
                results, output_file_name = detect_banana(upload_path)
                
                # เตรียม URL รูป
                if output_file_name:
                    image_url = url_for("static", filename=os.path.basename(output_file_name))
                
                # ลบไฟล์ต้นฉบับ
                if os.path.exists(upload_path):
                    os.remove(upload_path)

                # ✅ เช็คว่าเจอกล้วยไหม?
                if not results:
                    # ถ้า results เป็นค่าว่าง (AI หาไม่เจอ)
                    message = "ไม่พบรูปกล้วยในภาพ (No banana detected)"
                else:
                    # ถ้าเจอ ก็ดึงข้อมูลโภชนาการปกติ
                    main_label = results[0]["label"]
                    if main_label in RIPENESS_INFO:
                        nutrition = RIPENESS_INFO[main_label]["nutrition"]
                        benefit = RIPENESS_INFO[main_label]["benefit"]

                # ส่งค่าไปหน้า result
                return render_template("result.html", 
                                       results=results, 
                                       image_path=image_url, 
                                       nutrition=nutrition, 
                                       benefit=benefit,
                                       message=message) # ✅ ส่ง message ไปด้วย

            except Exception as e:
                print(f"Error: {e}")
                return render_template("index.html", error_message=f"Error: {e}")

    return render_template("index.html")

if __name__ == "__main__":
    # เปลี่ยน host เป็น '0.0.0.0' เพื่อรับการเชื่อมต่อจากทุก Network Interface
    # เปลี่ยน port เป็น 8888 (หรือพอร์ตอื่นที่สูงๆ เช่น 9999)
    app.run(debug=True, host='0.0.0.0', port=8888)
