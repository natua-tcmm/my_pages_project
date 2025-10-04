// ユーザーのUUIDをLocalStorageで管理し、Ajaxで動画アップロード＆CSVダウンロード（UI改善版）

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#yumesute-ocr-upload-form");
    const fileInput = document.querySelector("#video");
    const messageBox = document.querySelector("#yumesute-ocr-message");
    const downloadArea = document.querySelector("#yumesute-ocr-download-link");

    const uuidKey = "yumesute_ocr_uuid";
    const uuid = localStorage.getItem(uuidKey);

    // 再訪問時：UUIDがあれば「実行済みデータあり」メッセージ＋ダウンロードボタン（ポーリングで完了検知）
    if (uuid) {
        if (form) form.style.display = "none";
        if (messageBox) {
            messageBox.style.display = "block";
            messageBox.textContent = "OCR実行中のデータがあります！";
        }
        if (downloadArea) {
            downloadArea.style.display = "block";
            downloadArea.innerHTML = `<span class="text-muted">状況確認中...</span>`;
        }

        // ポーリングでOCR完了を監視
        const pollStatus = () => {
            fetch(`/my_apps/yumesute_ocr_check_status?uuid=${encodeURIComponent(uuid)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.ready) {
                        if(messageBox) {
                            messageBox.classList.remove("alert-info");
                            messageBox.classList.add("alert-success");
                            messageBox.textContent = "OCR処理が完了しました！";
                        }
                        if (downloadArea) {
                            downloadArea.innerHTML = `
                                <p class="mb-2">以下のボタンからCSVファイルをダウンロードしてください。</p>
                                <button id="yumesute-ocr-download-btn" class="btn btn-success mb-4">CSVをダウンロード</button>
                                <p class="mb-2">再度ツールを使用する場合は「データクリア」ボタンを押してください。<span style="color: red;"><strong>今回のデータは消去され、二度とダウンロードできなくなります。</strong></span></p>
                                <button id="yumesute-ocr-clear" class="btn btn-secondary mb-4">データクリア</button>
                            `;
                            const btn = document.getElementById("yumesute-ocr-download-btn");
                            const clearBtn = document.getElementById("yumesute-ocr-clear");
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
                                        btn.disabled = false;
                                        btn.textContent = "CSVをダウンロード";
                                    })
                                    .catch(err => {
                                        alert(err.message);
                                        btn.disabled = false;
                                        btn.textContent = "CSVをダウンロード";
                                    });
                            });
                            clearBtn.addEventListener("click", function () {
                                if (confirm("本当にデータをクリアしますか？今回のデータは消去され、二度とダウンロードできなくなります。")) {
                                    localStorage.removeItem(uuidKey);
                                    window.location.reload();
                                }
                            });
                        }
                    } else {
                        downloadArea.innerHTML = "現在処理中です。完了するとダウンロードボタンが表示されます。";
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
                            messageBox.textContent = "アップロードが完了しました。ページが再読み込みされます...";
                            setTimeout(() => {
                                window.location.reload();
                            }, 3000);
                        }
                        if (form) form.style.display = "none";
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
