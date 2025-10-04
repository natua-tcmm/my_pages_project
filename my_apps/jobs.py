from .my_script.yumesute_ocr.run_ocr import run_ocr

def run_ocr_job(video_path, filename_uuid):
    """
    OCRジョブ本体（threading用）
    """
    import os
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    error_dir = os.path.join(BASE_DIR, "temp", "yumesute_ocr", "errors")
    os.makedirs(error_dir, exist_ok=True)

    print(f"OCRジョブ開始: {filename_uuid}")
    try:
        csv_filename, csv_path, uuid_val = run_ocr(video_path, filename_uuid)
        print(f"OCRジョブ完了: {csv_filename}")
    except Exception as e:
        print(f"OCRジョブ失敗: {e}")
        # エラー内容をファイルに保存
        error_path = os.path.join(error_dir, f"{filename_uuid}.error.txt")
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(str(e))
