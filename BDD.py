import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import sqlite3
import os
from PIL import Image, ImageTk
import io


def connect_db():
    conn = sqlite3.connect('user_database.db')
    return conn

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_images (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            image BLOB,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(name, username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, username, password) VALUES (?, ?, ?)', (name, username, password))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def insert_face_image(user_id, image_path):
    conn = connect_db()
    cursor = conn.cursor()
    with open(image_path, 'rb') as file:
        blob_data = file.read()
    cursor.execute('INSERT INTO face_images (user_id, image) VALUES (?, ?)', (user_id, blob_data))
    conn.commit()
    conn.close()

def update_user(user_id, name=None, username=None, password=None):
    conn = connect_db()
    cursor = conn.cursor()
    if name:
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
    if username:
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
    if password:
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (password, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    cursor.execute('DELETE FROM face_images WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    cursor.execute('SELECT image FROM face_images WHERE user_id = ?', (user_id,))
    images = cursor.fetchall()
    conn.close()
    return user_data, images


class UserDatabaseApp:
    def __init__(self, root):
        self.root = root
        root.title("User Database App")

        # 用户信息输入区域
        tk.Label(root, text="Name:").grid(row=0, column=0)
        tk.Label(root, text="Username:").grid(row=1, column=0)
        tk.Label(root, text="Password:").grid(row=2, column=0)

        self.name_entry = tk.Entry(root)
        self.username_entry = tk.Entry(root)
        self.password_entry = tk.Entry(root, show="*")

        self.name_entry.grid(row=0, column=1)
        self.username_entry.grid(row=1, column=1)
        self.password_entry.grid(row=2, column=1)

        tk.Button(root, text="Add User", command=self.add_user).grid(row=3, column=0, columnspan=2)

        # 用户ID输入区域
        tk.Label(root, text="User ID:").grid(row=4, column=0)
        self.user_id_entry = tk.Entry(root)
        self.user_id_entry.grid(row=4, column=1)

        # 更新、删除、获取用户信息按钮
        tk.Button(root, text="Update User", command=self.update_user).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Delete User", command=self.delete_user).grid(row=6, column=0, columnspan=2)
        tk.Button(root, text="Get User Info", command=self.get_user_info).grid(row=7, column=0, columnspan=2)

        # 图片上传按钮
        tk.Button(root, text="Upload Image", command=self.upload_image).grid(row=8, column=0, columnspan=2)

    def add_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_id = insert_user(name, username, password)
        messagebox.showinfo("User Added", f"User {name} added with ID {user_id}")

    def update_user(self):
        user_id = int(self.user_id_entry.get())
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        update_user(user_id, name, username, password)
        messagebox.showinfo("User Updated", f"User with ID {user_id} updated")

    def delete_user(self):
        user_id = int(self.user_id_entry.get())
        delete_user(user_id)
        messagebox.showinfo("User Deleted", f"User with ID {user_id} deleted")

    def get_user_info(self):
        user_id = int(self.user_id_entry.get())
        user_data, images = get_user(user_id)

        # 显示用户信息
        user_info = f"Name: {user_data[1]}\nUsername: {user_data[2]}" if user_data else "User not found"
        messagebox.showinfo("User Info", user_info)

        # 显示第一张图片
        if images:
            image_data = images[0][0]  # 获取第一张图片的二进制数据
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)

            # 创建一个新窗口来显示图片
            image_window = tk.Toplevel(self.root)
            image_window.title("User Image")
            tk.Label(image_window, image=photo).pack()

            # 需要保持对photo的引用，否则图片可能不会显示
            image_window.photo = photo
        else:
            messagebox.showinfo("No Image", "No images available for this user")


    def upload_image(self):
        user_id = int(self.user_id_entry.get())
        file_path = filedialog.askopenfilename()
        if file_path:
            insert_face_image(user_id, file_path)
            messagebox.showinfo("Image Uploaded", "Image successfully uploaded")

root = tk.Tk()
app = UserDatabaseApp(root)
root.mainloop()
