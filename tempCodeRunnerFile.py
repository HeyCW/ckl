try:
            # Load dan resize image
            icon_image = Image.open("assets/logo.jpg")
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_image)
        
            # Set sebagai window icon
            root.iconphoto(False, icon_photo)
            
        except Exception as e:
            print(f"Icon tidak ditemukan: {e}")