import qrcode

def generate_qr_code():
    print("génération qr code")


    url = "http://192.168.4.1:5000"

    img = qrcode.make(url)
    img.save("/static/qr.png")
    return img