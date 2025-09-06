from django import forms

class YumesuteOcrVideoForm(forms.Form):
    video = forms.FileField(
        label="動画ファイル（.mp4のみ・最大300MB）",
        help_text="300MBまでの.mp4ファイルのみアップロード可能です。",
        widget=forms.ClearableFileInput(attrs={"accept": ".mp4"}),
    )

    def clean_video(self):
        file = self.cleaned_data["video"]
        if not file.name.lower().endswith(".mp4"):
            raise forms.ValidationError("mp4ファイルのみアップロードできます。")
        if file.size > 300 * 1024 * 1024:
            raise forms.ValidationError("ファイルサイズは300MB以下にしてください。")
        return file
