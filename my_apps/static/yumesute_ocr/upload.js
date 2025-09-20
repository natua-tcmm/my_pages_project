// ユーザーのUUIDをLocalStorageで管理し、Ajaxで動画アップロード＆CSVダウンロード（UI改善版）

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#yumesute-ocr-upload-form");
    const fileInput = document.querySelector("#id_video");
    const messageBox = document.querySelector("#yumesute-ocr-message");
    const downloadArea = document.querySelector("#yumesute-ocr-download-link");

    const uuidKey = "yumesute_ocr_uuid";
    const uuid = localStorage.getItem(uuidKey);

    // 再訪問時：UUIDがあれば「実行済みデータあり」メッセージ＋ダウンロードボタン（ポーリングで完了検知）
    if (uuid) {
        if (form) form.style.display = "none";
        if (messageBox) {
            messageBox.style.display = "block";
            messageBox.textContent = "実行済みのデータがあります！（処理中の場合は完了までお待ちください）";
        }
        if (downloadArea) {
            downloadArea.style.display = "block";
            downloadArea.innerHTML = `<span class="text-muted">処理中...</span>`;
        }

        // ポーリングでOCR完了を監視
        const pollStatus = () => {
            fetch(`/my_apps/yumesute_ocr_check_status?uuid=${encodeURIComponent(uuid)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.ready) {
                        if (downloadArea) {
                            downloadArea.innerHTML = `
                                <button id="yumesute-ocr-download-btn" class="btn btn-success">CSVをダウンロード</button>
                            `;
                            const btn = document.getElementById("yumesute-ocr-download-btn");
                            btn.addEventListener("click", function () {
                                btn.disabled = true;
                                btn.textContent = "ダウンロード中...";
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
                                        if (downloadArea) downloadArea.style.display = "none";
                                    })
                                    .catch(err => {
                                        if (messageBox) messageBox.textContent = err.message;
                                        btn.disabled = false;
                                        btn.textContent = "CSVをダウンロード";
                                    });
                            });
                        }
                    } else {
                        setTimeout(pollStatus, 2000);
                    }
                })
                .catch(() => setTimeout(pollStatus, 4000));
        };
        pollStatus();
        return;
    }

    // フォーム送信をAjax化
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (!fileInput.files.length) return;

            const formData = new FormData(form);
            if (messageBox) {
                messageBox.style.display = "block";
                messageBox.textContent = "アップロード中...";
            }

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
                        if (messageBox) {
                            messageBox.style.display = "block";
                            messageBox.textContent = "アップロード完了！サーバー側で処理を開始しました。ページを再読み込みせずにお待ちください。";
                        }
                        if (form) form.style.display = "none";
                        if (downloadArea) {
                            downloadArea.style.display = "block";
                            downloadArea.innerHTML = `
                                <span class="text-muted">処理が完了するとここにダウンロードボタンが表示されます。</span>
                            `;
                        }
                    } else {
                        if (messageBox) {
                            messageBox.style.display = "block";
                            messageBox.textContent = data.error || "アップロードに失敗しました。";
                        }
                    }
                })
                .catch(() => {
                    if (messageBox) {
                        messageBox.style.display = "block";
                        messageBox.textContent = "通信エラーが発生しました。";
                    }
                });
        });
    }
});
