from .my_script.yumesute_ocr.run_ocr import run_ocr

def run_ocr_job(video_path, filename_uuid):
    """
    OCRジョブ本体（threading用）
    """
    print(f"OCRジョブ開始: {filename_uuid}")
    try:
        csv_filename, csv_path, uuid_val = run_ocr(video_path, filename_uuid)
        print(f"OCRジョブ完了: {csv_filename}")
    except Exception as e:
        print(f"OCRジョブ失敗: {e}")
