// ユーザーのUUIDをLocalStorageで管理し、Ajaxで動画アップロード＆CSV自動ダウンロード

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#yumesute-ocr-upload-form");
    const fileInput = document.querySelector("#id_video");
    const messageBox = document.querySelector("#yumesute-ocr-message");
    const downloadLink = document.querySelector("#yumesute-ocr-download-link");

    // ページロード時：UUIDがあればCSVダウンロード
    const uuidKey = "yumesute_ocr_uuid";
    const uuid = localStorage.getItem(uuidKey);
    if (uuid) {
        fetch(`/my_apps/yumesute_ocr_csv_download?uuid=${encodeURIComponent(uuid)}`)
            .then(response => {
                if (response.status === 200) {
                    return response.blob();
                } else {
                    throw new Error("CSVファイルが見つかりませんでした。");
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${uuid}.csv`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                localStorage.removeItem(uuidKey);
                if (messageBox) messageBox.textContent = "CSVファイルをダウンロードしました。";
            })
            .catch(err => {
                if (messageBox) messageBox.textContent = err.message;
                localStorage.removeItem(uuidKey);
            });
        // アップロードフォームは非表示
        if (form) form.style.display = "none";
        return;
    }

    // フォーム送信をAjax化
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (!fileInput.files.length) return;

            const formData = new FormData(form);
            if (messageBox) messageBox.textContent = "アップロード中...";

            fetch("/my_apps/yumesute_ocr_ajax_upload", {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.filename_uuid) {
                        localStorage.setItem(uuidKey, data.filename_uuid);
                        if (messageBox) messageBox.textContent = "アップロード完了。ページを再読み込みします...";
                        setTimeout(() => window.location.reload(), 1000);
                    } else {
                        if (messageBox) messageBox.textContent = data.error || "アップロードに失敗しました。";
                    }
                })
                .catch(() => {
                    if (messageBox) messageBox.textContent = "通信エラーが発生しました。";
                });
        });
    }
});
