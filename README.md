<div align="center">

# 🚀 Hùng Vương Online Judge

### Nền tảng Online Judge hiện đại, nhẹ và tự triển khai bằng Django cho học sinh trường Trung Học Cơ Sở Hùng Vương .

**Luyện tập • Thi đấu • Học tập**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20?logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-blue)](https://www.linux.org/)
[![Status](https://img.shields.io/badge/Status-Active-success)]()

**Giải bài lập trình. Tổ chức cuộc thi. Chấm code tức thì.**

</div>

---

# ✨ Giới thiệu

**Hùng Vương Online Judge** là một nền tảng chấm bài lập trình mã nguồn mở, được xây dựng bằng **Django** và lấy cảm hứng từ các hệ thống như **Codeforces, AtCoder và LeetCode**.

Hệ thống cho phép giáo viên, trường học, câu lạc bộ lập trình và các tổ chức:

* Tạo và quản lý bài tập lập trình
* Cho phép học sinh gửi bài trực tuyến
* Tự động biên dịch và chấm code
* Tổ chức các cuộc thi lập trình
* Theo dõi bảng xếp hạng
* Quản lý người dùng
* Viết editorial cho bài toán
* Tra cứu lịch sử submission
* Trao đổi thông qua hệ thống chat

Toàn bộ nền tảng sử dụng **Django** làm backend và được thiết kế để có thể mở rộng trong tương lai.

---

# 🚀 Tính năng

## 📝 Quản lý bài toán

Hệ thống hỗ trợ quản lý bài toán với nhiều tính năng:

* Nội dung đề bài bằng Markdown
* Mô tả bài toán
* Ràng buộc dữ liệu
* Giải thích
* Gợi ý
* Mức độ khó
* Tags / chủ đề
* Input / Output
* Test mẫu
* Test ẩn
* Giới hạn thời gian
* Giới hạn bộ nhớ
* Đáp án mẫu
* Quản lý trạng thái bài toán

---

# ⚡ Hệ thống chấm bài

Online Judge hỗ trợ nhiều ngôn ngữ lập trình.

### Ngôn ngữ

* C — C11
* C++ — C++17
* Python — Python 3

### Kết quả chấm

Hệ thống có thể trả về các verdict:

| Verdict                  | Ý nghĩa                   |
| ------------------------ | ------------------------- |
| ✅ Accepted               | Bài làm đúng              |
| ❌ Wrong Answer           | Kết quả sai               |
| ⏱ Time Limit Exceeded    | Vượt quá thời gian        |
| 💾 Memory Limit Exceeded | Vượt quá bộ nhớ           |
| ⚠ Runtime Error          | Lỗi khi chạy chương trình |
| 🔨 Compilation Error     | Lỗi biên dịch             |
| 🚫 Judgement Failed      | Hệ thống chấm gặp lỗi     |

Mỗi submission có thể lưu:

* Thời gian chạy
* Bộ nhớ sử dụng
* Kết quả từng test
* Test bị sai
* Verdict
* Thông báo lỗi
* Ngôn ngữ
* Source code
* Thời gian submit
* Người gửi bài

---

# ▶ Chạy thử trước khi Submit

Người dùng có thể chạy code trước khi gửi submission chính thức.

Có thể chạy với:

* Test mẫu
* Input tùy chỉnh
* Nhiều lần thử nghiệm

Tính năng này tương tự trải nghiệm trên:

* LeetCode
* Codeforces
* AtCoder

Việc chạy thử không tạo submission chính thức.

---

# 🏆 Hệ thống cuộc thi

Online Judge hỗ trợ tổ chức các cuộc thi lập trình.

### Tính năng

* Đăng ký cuộc thi
* Thời gian bắt đầu
* Thời gian kết thúc
* Countdown
* Danh sách bài
* Bài ẩn
* Mở bài tự động
* Bảng xếp hạng trực tiếp
* Tính điểm
* Tính penalty
* Theo dõi submission
* Chế độ ICPC

### ICPC Scoring

Hệ thống có thể tính:

```text
Score = số bài giải đúng

Penalty =
    tổng thời gian submit
    + penalty cho các lần submit sai
```

Bảng xếp hạng có thể cập nhật theo thời gian thực thông qua polling.

---

# 📖 Editorial System

Mỗi bài toán có thể có một trang **Editorial** riêng.

Editorial có thể bao gồm:

* Ý tưởng
* Phân tích bài toán
* Thuật toán
* Độ phức tạp
* Code mẫu
* Lời giải bằng nhiều ngôn ngữ

Editorial có thể được thiết lập để:

* Hiển thị sau khi giải bài
* Hiển thị sau khi cuộc thi kết thúc
* Ẩn trong thời gian cuộc thi

---

# 📈 Leaderboard

Hệ thống có bảng xếp hạng người dùng.

Có thể xếp hạng dựa trên:

* Số bài đã giải
* Số submission
* Tỷ lệ Accepted
* Điểm cuộc thi
* Thành tích
* Rating trong tương lai

Ví dụ:

| Rank | User    | Solved | Submissions | Acceptance |
| ---: | ------- | -----: | ----------: | ---------: |
|    1 | alice   |    120 |         180 |      66.7% |
|    2 | bob     |    105 |         170 |      61.8% |
|    3 | charlie |     98 |         160 |      61.2% |

---

# 💬 Chat tích hợp

Hệ thống có chat ngay trong website.

### Global Chat

Tất cả người dùng có thể tham gia.

### Contest Chat

Chat riêng trong từng cuộc thi.

### Công nghệ

Chat sử dụng:

* AJAX
* HTTP polling
* Django views
* JavaScript

Không bắt buộc phải sử dụng WebSocket.

---

# 🔐 Authentication

Hệ thống cung cấp chức năng tài khoản người dùng.

### Người dùng

* Đăng ký
* Đăng nhập
* Đăng xuất
* Hồ sơ cá nhân
* Đổi mật khẩu
* Lịch sử bài làm
* Danh sách bài đã giải
* Thống kê submission
* Thống kê Accepted
* Theo dõi thành tích

---

# ⚙ Admin Dashboard

Hệ thống sử dụng **Django Admin** để quản lý toàn bộ nền tảng.

Admin có thể quản lý:

* 👤 Users
* 📝 Problems
* 🧪 Test Cases
* 🏆 Contests
* 📖 Editorials
* 📤 Submissions
* 💬 Chat
* 📊 Statistics
* 🔄 Rejudge

### Rejudge

Admin có thể yêu cầu chấm lại submission hoặc toàn bộ bài toán sau khi:

* Thay đổi test case
* Sửa đáp án
* Sửa checker
* Thay đổi giới hạn
* Cập nhật judge

---

# 🏗 Kiến trúc hệ thống

```text
                    +----------------+
                    |    Browser     |
                    +--------+-------+
                             |
                             |
                     Django Templates
                             |
                    +--------v--------+
                    | Django Backend  |
                    +--------+--------+
                             |
              +--------------+--------------+
              |                             |
              |                             |
        Local Judge                    Judge0 Backend
              |                             |
       +------+------+                +-----+-----+
       |      |      |                |           |
      gcc    g++   python3       Judge0 REST API
       |      |      |
       +------+------+
              |
       +------v-------+
       |   Database   |
       +--------------+
       | SQLite/MySQL |
       +--------------+
```

---

# 🛠 Công nghệ sử dụng

| Thành phần  | Công nghệ             |
| ----------- | --------------------- |
| Backend     | Django 4.2 LTS        |
| Ngôn ngữ    | Python 3              |
| Database    | SQLite / MySQL        |
| Judge       | Local Runner / Judge0 |
| Code Editor | CodeMirror 5          |
| Frontend    | Django Templates      |
| CSS         | Custom CSS            |
| JavaScript  | Vanilla JavaScript    |
| Chat        | AJAX Polling          |
| Deployment  | WSGI                  |

---

# 📦 Cài đặt

## 1. Clone repository

```bash
git clone https://github.com/ragibcs/online-judge.git

cd online-judge
```

---

## 2. Tạo Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```powershell
python -m venv venv

venv\Scripts\activate
```

---

# 📥 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄 4. Khởi tạo Database

Chạy migration:

```bash
python manage.py migrate
```

---

# 👤 5. Tạo tài khoản Admin

Có thể tạo administrator bằng:

```bash
python manage.py createsuperuser
```

Sau đó nhập:

```text
Username:
Email:
Password:
```

---

# 🌱 6. Tạo dữ liệu Demo

Nếu project có command `seed_demo`:

```bash
python manage.py seed_demo
```

Lệnh này có thể tạo dữ liệu mẫu như:

* Users
* Problems
* Test cases
* Contests
* Editorials

---

# ▶️ 7. Chạy server

```bash
python manage.py runserver
```

Sau đó mở:

```text
http://127.0.0.1:8000
```

Trang quản trị:

```text
http://127.0.0.1:8000/admin/
```

---

# 🧑‍💻 Tài khoản Demo

Nếu project được cấu hình sẵn dữ liệu demo:

| Username | Password | Role          |
| -------- | -------- | ------------- |
| admin    | admin123 | Administrator |
| alice    | demo1234 | User          |
| bob      | demo1234 | User          |

> ⚠️ **Quan trọng:** Không sử dụng mật khẩu demo trên server production. Hãy đổi mật khẩu administrator ngay sau khi triển khai.

---

# 🌍 Deployment

Trước khi triển khai production, nên kiểm tra:

```text
DEBUG = False
```

Thiết lập:

* Secret Key an toàn
* Allowed Hosts
* HTTPS
* Database production
* Static files
* Media files
* Judge backend an toàn

Thu thập static:

```bash
python manage.py collectstatic
```

---

# ☁️ Có thể triển khai trên

Online Judge có thể triển khai trên:

* PythonAnywhere
* Render
* Railway
* VPS
* Ubuntu Server
* DigitalOcean
* Các máy chủ Linux khác

---

# ⚙️ Configuration

Các biến môi trường đề xuất:

| Variable                 | Mặc định        | Mô tả                          |
| ------------------------ | --------------- | ------------------------------ |
| `OJ_SECRET_KEY`          | Development Key | Django Secret Key              |
| `OJ_DEBUG`               | `1`             | Chế độ debug                   |
| `OJ_ALLOWED_HOSTS`       | `*`             | Các domain được phép           |
| `OJ_TIME_ZONE`           | `UTC`           | Múi giờ                        |
| `OJ_JUDGE_BACKEND`       | `local`         | Backend chấm                   |
| `OJ_JUDGE0_URL`          | `localhost`     | Địa chỉ Judge0                 |
| `OJ_JUDGE0_AUTH_TOKEN`   | Optional        | Token Judge0                   |
| `OJ_SUBMISSION_COOLDOWN` | `15`            | Thời gian chờ giữa submission  |
| `OJ_RUN_COOLDOWN`        | `10`            | Thời gian chờ giữa các lần Run |

---

# 🧠 Judge Backend

Online Judge hỗ trợ hai hướng triển khai chính.

## 🖥 Local Judge

Local Judge chạy trực tiếp trên server.

Có thể sử dụng:

```text
gcc
g++
python3
```

### Ưu điểm

* Nhanh
* Không cần Internet
* Không phụ thuộc dịch vụ bên ngoài
* Dễ triển khai
* Phù hợp môi trường nội bộ

### Phù hợp với

* Trường học
* Phòng máy
* Coding Club
* Cuộc thi nội bộ
* Server cá nhân

> ⚠️ Local Judge không tự động sandbox code người dùng.

---

# ☁️ Judge0

Judge0 cung cấp hệ thống thực thi code thông qua REST API.

Luồng hoạt động:

```text
User
  |
  v
Django
  |
  v
Judge0 API
  |
  v
Compile
  |
  v
Run
  |
  v
Result
  |
  v
Django
  |
  v
User
```

Judge0 phù hợp hơn với các hệ thống:

* Public Online Judge
* Nhiều người dùng
* Website Internet-facing
* Hệ thống cần hỗ trợ nhiều ngôn ngữ

---

# 📂 Cấu trúc Project

Một cấu trúc điển hình:

```text
online-judge/
│
├── manage.py
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── chat/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── judge/
│   ├── judging/
│   │   ├── runner.py
│   │   ├── compiler.py
│   │   └── checker.py
│   │
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── problems/
│   ├── contests/
│   └── accounts/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── requirements.txt
│
└── README.md
```

---

# 🔒 Bảo mật

## ⚠️ Cảnh báo Local Judge

Local Judge **không nên được sử dụng trực tiếp để chạy code không tin cậy trên server production** nếu chưa có sandbox.

Code do người dùng gửi có thể cố gắng:

* Đọc file
* Sử dụng tài nguyên hệ thống
* Tạo process
* Truy cập network
* Chiếm CPU
* Sử dụng quá nhiều RAM
* Gây ảnh hưởng tới server

Do đó, không nên chạy:

```text
untrusted code
        ↓
directly on host
```

---

# 🛡 Khuyến nghị Sandbox

Đối với hệ thống public, nên sử dụng một cơ chế sandbox như:

* Judge0
* Docker
* Firecracker
* gVisor
* Container isolation
* Resource limits

Ngoài ra nên:

* Tắt `DEBUG`
* Sử dụng HTTPS
* Sử dụng Secret Key mạnh
* Giới hạn CPU
* Giới hạn RAM
* Giới hạn thời gian chạy
* Giới hạn kích thước source code
* Giới hạn số submission
* Kiểm soát quyền truy cập file
* Hạn chế network access của judge

---

# 📊 Luồng Submit

```text
                User writes code
                       |
                       v
                  Click Submit
                       |
                       v
                 Django Server
                       |
                       v
                 Create Submission
                       |
                       v
                  Judge Queue
                       |
                       v
                 Compile Code
                       |
              +--------+--------+
              |                 |
          Compile OK       Compile Error
              |                 |
              v                 v
          Run Tests          CE Result
              |
       +------+------+
       |             |
    All Pass      Failed
       |             |
       v             v
   Accepted      WA/TLE/RE
```

---

# 🧪 Test Case System

Mỗi bài toán có thể chứa nhiều test case.

Ví dụ:

```text
Problem
│
├── Sample Test 1
├── Sample Test 2
│
├── Hidden Test 1
├── Hidden Test 2
├── Hidden Test 3
└── Hidden Test 4
```

Test mẫu được hiển thị cho người dùng.

Test ẩn chỉ được sử dụng bởi judge.

---

# 🔄 Rejudge

Admin có thể rejudge khi cần.

Ví dụ:

```text
Problem
   |
   +-- Update Test Cases
   |
   +-- Update Checker
   |
   +-- Rejudge
          |
          v
      Submissions
          |
          v
      Judge Again
```

---

# 📈 Thống kê

Hệ thống có thể cung cấp các thống kê:

### User

* Tổng số bài đã giải
* Tổng submission
* Accepted
* Wrong Answer
* Runtime Error
* Compilation Error
* Acceptance Rate

### Problem

* Số người đã giải
* Số submission
* Acceptance Rate
* Độ khó
* Số lượt chạy

### Contest

* Số người tham gia
* Số bài được giải
* Submission theo thời gian
* Bảng xếp hạng

---

# 🎨 Frontend

Frontend sử dụng:

* Django Templates
* HTML5
* CSS3
* Vanilla JavaScript
* CodeMirror 5

Code editor có thể hỗ trợ:

* Syntax highlighting
* Line numbers
* Dark mode
* Code indentation
* Keyboard shortcuts

---

# 🌙 Dark Mode

Giao diện có thể hỗ trợ:

```text
Light Mode
Dark Mode
System Mode
```

Người dùng có thể lưu lựa chọn theme vào local storage hoặc profile.

---

# 🧩 Khả năng mở rộng

Project được thiết kế để có thể mở rộng thêm:

* C++
* C
* Python
* Java
* JavaScript
* Go
* Rust
* Kotlin
* PHP
* C#
* Pascal

Ngoài ra có thể bổ sung:

* Rating
* ELO
* Problemset nâng cao
* Virtual Contest
* Group
* Blog
* Discussion
* Notifications
* API
* WebSocket
* Code similarity detection
* Plagiarism detection

---

# 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh.

Quy trình đề xuất:

```text
Fork
  ↓
Create Branch
  ↓
Make Changes
  ↓
Test
  ↓
Commit
  ↓
Push
  ↓
Pull Request
```

Ví dụ:

```bash
git checkout -b feature/new-feature

git add .

git commit -m "Add new feature"

git push origin feature/new-feature
```

Sau đó tạo Pull Request trên GitHub.

---

# 🐛 Báo lỗi

Nếu phát hiện lỗi, hãy tạo Issue và cung cấp:

* Mô tả lỗi
* Các bước tái hiện
* Hệ điều hành
* Python version
* Django version
* Log lỗi
* Screenshot nếu cần

Không nên đăng:

* Password
* Secret Key
* API token
* Database credentials

---

# ⭐ Hỗ trợ dự án

Nếu dự án hữu ích với bạn, hãy:

* ⭐ Star repository
* 🐛 Báo lỗi
* 💡 Đề xuất tính năng
* 🤝 Đóng góp code
* 📖 Cải thiện documentation

Mỗi đóng góp đều giúp dự án phát triển hơn.

---

# 📄 License

Dự án được phát hành theo **MIT License**.

Xem file:

```text
LICENSE
```

để biết đầy đủ điều khoản sử dụng.

---

# ❤️ Credits

Dự án được xây dựng với:

* Python
* Django
* HTML
* CSS
* JavaScript
* CodeMirror

Lấy cảm hứng từ các nền tảng competitive programming phổ biến như:

* Codeforces
* AtCoder
* LeetCode
* DMOJ

---

<div align="center">

## 🚀 Hùng Vương Online Judge

**Practice • Compete • Learn**

Built with ❤️ using **Django** 
__________________________________________________________________________________________________________________________________________________________________
Tác giả : Nguyễn Lâm Huy.
</div>
