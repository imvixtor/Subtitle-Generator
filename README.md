# Hướng Dẫn Sử Dụng Ứng Dụng Tạo Phụ Đề Tự Động (Forced Alignment)

Đây là ứng dụng dòng lệnh (CLI) giúp bạn đồng bộ hóa lời bài hát (lyrics) với file âm thanh (audio) để tạo ra file phụ đề chuẩn (SRT). Ứng dụng sử dụng mô hình AI `stable-ts` (dựa trên OpenAI Whisper) để đạt độ chính xác cao và hỗ trợ chia nhỏ phụ đề theo độ dài mong muốn.

## Yêu Cầu Hệ Thống (System Requirements)

Ứng dụng chạy trên mô hình AI nên tốc độ xử lý phụ thuộc lớn vào cấu hình máy tính của bạn.

### 1. Cấu Hình Tối Thiểu (Có Thể Chạy Được)
Đây là cấu hình để chạy được ứng dụng, nhưng tốc độ có thể chậm (xử lý 1 bài hát 5 phút có thể mất 2-5 phút).
-   **CPU**: Intel Core i5 (đời 8 trở lên) hoặc AMD Ryzen 5 tương đương.
-   **RAM**: 8 GB.
-   **GPU (Card Màn Hình)**: Không bắt buộc (chạy bằng CPU).
-   **Ổ Cứng**: Hỗ trợ SSD (khuyến khích) để load model nhanh hơn.
-   **Hệ Điều Hành**: Windows 10/11, macOS, Linux.

### 2. Cấu Hình Khuyến Nghị (Chạy Mượt)
Cấu hình này giúp xử lý nhanh chóng (gần như tức thì hoặc trong vài chục giây cho 1 bài hát).
-   **CPU**: Intel Core i7 / AMD Ryzen 7 trở lên.
-   **RAM**: 16 GB trở lên.
-   **GPU (Card Màn Hình)**: NVIDIA GPU với ít nhất **4GB VRAM** (VRAM càng cao càng tốt, ví dụ GTX 1650, RTX 2060 trở lên). *Lưu ý: Cần cài đặt CUDA để chạy bằng GPU.*
-   **Ổ Cứng**: SSD.

> **Lưu ý**: Nếu máy bạn không có GPU rời, ứng dụng vẫn chạy tốt nhưng sẽ sử dụng CPU, tốc độ sẽ chậm hơn đáng kể.

## Phần Mềm Yêu Cầu
1.  **Python 3.8** trở lên.
2.  **FFmpeg**: Cần được cài đặt để xử lý file âm thanh.
    -   *Windows*: Tải từ [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), giải nén và thêm thư mục `bin` vào PATH.
    -   *Mac/Linux*: Cài qua brew hoặc apt (`brew install ffmpeg` hoặc `sudo apt install ffmpeg`).

## Cài Đặt

1.  Mở terminal tại thư mục dự án.
2.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```

## Cách Sử Dụng

Chạy ứng dụng bằng câu lệnh sau:

```bash
python main.py --audio <đường_dẫn_file_âm_thanh> --lyrics <đường_dẫn_file_lời> --output <tên_file_phụ_đề_ra> [tùy_chọn]
```

### Các Tham Số Tùy Chọn

-   `--audio`: Đường dẫn đến file âm thanh (mp3, wav, m4a, v.v.). **(Bắt buộc)**
-   `--lyrics`: Đường dẫn đến file văn bản chứa lời bài hát (.txt). **(Bắt buộc)**
-   `--output`: Đường dẫn/tên file phụ đề đầu ra (.srt). **(Bắt buộc)**
-   `--max_len`: Số lượng ký tự tối đa trên mỗi dòng phụ đề. Mặc định là **40**.
-   `--language`: Mã ngôn ngữ của bài hát (ví dụ: `vi` cho tiếng Việt, `en` cho tiếng Anh). Mặc định là `vi`.

### Ví Dụ

Cơ bản:
```bash
python main.py --audio bai_hat.mp3 --lyrics loi_bai_hat.txt --output phu_de.srt
```

Tùy chỉnh độ dài dòng ngắn hơn (30 ký tự):
```bash
python main.py --audio bai_hat.mp3 --lyrics loi_bai_hat.txt --output phu_de.srt --max_len 30
```

## Cách Hoạt Động

1.  **Căn Chỉnh (Alignment)**: Ứng dụng dùng AI để xác định thời gian bắt đầu và kết thúc chính xác của từng từ trong file âm thanh.
2.  **Phân Đoạn (Segmentation)**: Các từ được ghép lại thành câu. Ứng dụng sẽ tự động ngắt xuống dòng mới nếu câu vượt quá độ dài `max_len` bạn quy định, giúp phụ đề hiển thị đẹp trên video.
3.  **Xuất File**: Kết quả được lưu dưới dạng file `.srt`, bạn có thể import trực tiếp vào Premiere Pro, CapCut, DaVinci Resolve, v.v.

## Xử Lý Lỗi Thường Gặp

-   **Lỗi "FFmpeg not found"**: Hãy chắc chắn bạn đã cài FFmpeg và restart lại terminal.
-   **Lỗi bộ nhớ (Memory)**: Mô hình AI có thể tốn RAM. Nếu máy yếu, quá trình xử lý file dài có thể hơi lâu.
