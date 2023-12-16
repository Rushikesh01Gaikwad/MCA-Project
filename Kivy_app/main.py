import cv2
from datetime import datetime
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
import sqlite3
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
import qrcode
import numpy as np
from io import BytesIO
from pyzbar.pyzbar import decode



class testApp1(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    pass


class sign_in_file_stud(Screen):

    def validate_login_stud(self, roll, Pass):

        conn = sqlite3.connect("C:\\Users\Rushi\Desktop\sqlite3\Attend_Portal.db")
        c = conn.cursor()

        c.execute("select * from Stud_reg_page where Roll_number = ? AND Password = ?;", (roll, Pass))
        stud = c.fetchone()

        c.execute("select QR from Stud_reg_page where Roll_number = ? AND Password = ?;", (roll, Pass))
        Qr_data = c.fetchone()

        conn.close()

        if stud and Qr_data is not None:
            qr = Qr_data[0]
            image_text = CoreImage(BytesIO(qr), ext="png").texture
            image = Image(texture=image_text)
            self.manager.current = 'main_stud'
            self.manager.get_screen('main_stud').ids.qr_image.texture = image.texture
        else:
            self.ids.log_msg.text = 'Incorrect Roll_number or Password'



class sign_up_file_stud(Screen):

    def submit_stud(self, name, gender, Class, roll, mob, Pass):

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        combined_data = f"{roll}"
        qr.add_data(combined_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert the image to bytes for storing in the database

        img_byte_array = BytesIO()
        img.save(img_byte_array)
        img_byte_array = img_byte_array.getvalue()

        conn = sqlite3.connect("C:\\Users\Rushi\Desktop\sqlite3\Attend_Portal.db")
        c = conn.cursor()

        c.execute('INSERT INTO Stud_reg_page VALUES (?, ?, ?, ?, ?, ?, ?);', (name, gender, Class, roll, mob, Pass, img_byte_array))

        conn.commit()

        self.ids.name_input.text = ''
        self.ids.gender_input.text = ''
        self.ids.class_input.text = ''
        self.ids.roll_input.text = ''
        self.ids.mob_input.text = ''
        self.ids.pass_input.text = ''

        conn.close()


class sign_in_file_teacher(Screen):

    def validate_login_teach(self, name, sub, Pass):
        conn = sqlite3.connect("C:\\Users\Rushi\Desktop\sqlite3\Attend_Portal.db")
        c = conn.cursor()
        c.execute("select * from Teacher_reg_page where Name = ? AND Subject = ? AND Password = ?;", (name, sub, Pass))
        stud = c.fetchone()

        if stud:
            self.parent.current = 'main_teach'
        else:
            self.ids.log_msg.text = 'Incorrect Roll_number or Password'


class sign_up_file_teacher(Screen):

    def submit_teach(self, name, Class, subject, mob, Pass):
        conn = sqlite3.connect("C:\\Users\Rushi\Desktop\sqlite3\Attend_Portal.db")
        c = conn.cursor()

        c.execute('Insert into Teacher_reg_page values (?, ?, ?, ?, ?)', (name, Class, subject, mob, Pass))

        conn.commit()

        self.ids.name_teach.text = ''
        self.ids.class_teach.text = ''
        self.ids.subject_teach.text = ''
        self.ids.mob_teach.text = ''
        self.ids.pass_teach.text = ''

        conn.close()


class main_screen_stud(Screen):
    pass


class main_screen_teach(Screen):

    def open_cam(self):

        conn = sqlite3.connect("C:\\Users\Rushi\Desktop\sqlite3\Attend_Portal.db")
        c = conn.cursor()

        c. execute('select Roll_number from Stud_reg_page;')
        stud_data = [record[0] for record in c.fetchall()]

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)

        used_codes = []

        while True:
            success, img = cap.read()

            for barcode in decode(img):

                if barcode.data.decode('utf-8') not in used_codes:
                    mydata = barcode.data.decode('utf-8')
                    str_mydata = str(mydata)
                    used_codes.append(barcode.data.decode('utf-8'))

                    roll = str_mydata
                    current_date_time = datetime.now()
                    present = 'P'

                    if str_mydata in stud_data:
                        c.execute('Insert into Presenty_sheet values (?, ?, ?)', (roll, current_date_time, present))
                        conn.commit()
                    else:
                        pass

                elif barcode.data.decode('utf-8') in used_codes:
                    aluseQR = 'Present Successful'
                    pts = np.array([barcode.polygon], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(img, [pts], True, (255, 0, 255), 5)
                    pts2 = barcode.rect
                    cv2.putText(img, aluseQR, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
                                0.9, (255, 0, 255), 2)
                else:
                    pass
            cv2.imshow('Result', img)
            cv2.waitKey(1)



class WindowManager(ScreenManager):
    pass


Builder.load_file("1stpage.kv")

class MyApp(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        sm = ScreenManager()
        sm.add_widget(testApp1(name='1st_page'))
        sm.add_widget(sign_in_file_stud(name='sign_in_stud'))
        sm.add_widget(sign_up_file_stud(name='sign_up_stud'))
        sm.add_widget(sign_in_file_teacher(name='sign_in_teacher'))
        sm.add_widget(sign_up_file_teacher(name='sign_up_teacher'))
        sm.add_widget(main_screen_stud(name='main_stud'))
        sm.add_widget(main_screen_teach(name='main_teach'))

        return sm



if __name__ == "__main__":
    Window.size = (360, 600)
    MyApp().run()

